"""
fetch_regulatory_updates.py
Searches news for regulatory developments per territory in data/regulatory.csv,
asks Groq whether each article materially changes that territory's row, and
applies proposed edits to regulatory.csv. Intended to run from a workflow that
opens a pull request — risk ratings drive market-entry decisions, so nothing
here is committed straight to main.

Source:
  - Google News RSS search, one query per territory (regulator names +
    exosome / stem cell / cell therapy terms). Google News links are redirect
    URLs; reviewers may want to swap in the original article URL before merge.

Outputs:
  - data/regulatory.csv       edited rows (Change Flag, Source URL,
                              Last Updated, date_added set so the dashboard
                              flags them 🆕 NEW)
  - data/regulatory_seen.csv  every article reviewed + verdict, so the same
                              article is not re-proposed after merge
  - Markdown summary          path given as argv[1] (default
                              regulatory_summary.md) — used as the PR body

NOTE ON SILENT FAILURE: as in fetch_signals_csv.py, feedparser does not raise
on a dead URL. A feed that returns zero entries for EVERY territory is treated
as a hard failure rather than "quiet week".

Requirements: pip install feedparser groq
"""

import os, sys, csv, json, hashlib, datetime, urllib.parse, feedparser
from groq import Groq

DATA_DIR  = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
REG_FILE  = os.path.join(DATA_DIR, "regulatory.csv")
SEEN_FILE = os.path.join(DATA_DIR, "regulatory_seen.csv")
GROQ_KEY  = os.environ["GROQ_API_KEY"]
GROQ_MODEL = "openai/gpt-oss-120b"  # keep in sync with fetch_signals_csv.py
LOOKBACK_DAYS = 14
MAX_ARTICLES_PER_TERRITORY = 8

# Google News silently returns ~0 results for long nested OR queries (a
# combined EU query got 0 hits where "EMA exosome" got 32), so we run many
# short "<term> <topic>" queries instead and merge.
TOPIC_TERMS = ['exosome', '"stem cell"', '"cell therapy"']

# Regulator / market terms per territory — keys must match the Territory column
TERRITORY_TERMS = {
    "USA":         ['FDA', '"warning letter"', 'injunction'],
    "EU":          ['EMA', 'ATMP', '"Cosmetics Regulation"'],
    "Australia":   ['TGA', 'Australia'],
    "Germany":     ['BfArM', '"Paul-Ehrlich-Institut"'],
    "France":      ['ANSM'],
    "Switzerland": ['Swissmedic'],
    "Brazil":      ['ANVISA'],
    "South Korea": ['MFDS', 'Korea regulation'],
    "UAE":         ['UAE', '"Dubai Health Authority"'],
    "Taiwan":      ['TFDA', 'Taiwan'],
    "Thailand":    ['"Thai FDA"', 'Thailand'],
    "Singapore":   ['HSA Singapore'],
    "Philippines": ['"FDA Philippines"'],
    "Malaysia":    ['NPRA', 'Malaysia'],
    "Indonesia":   ['BPOM', 'Indonesia'],
    "Mexico":      ['COFEPRIS'],
    "Colombia":    ['INVIMA'],
    "Argentina":   ['ANMAT'],
}

# Cheap pre-filter before spending a Groq call: title must read like a
# regulatory story, not a product review or clinic ad.
REGULATORY_KEYWORDS = [
    "fda", "regulat", " ban", "approv", "warning", "guidance", "guideline",
    "decree", "law", "rule", "injunction", "enforce", "licen", "registr",
    "classif", "agency", "ministry", "authority", "crackdown", "illegal",
    "unapproved", "prohibit", "notice", "circular", "court", "lawsuit",
    "seiz", "recall", "compliance", "policy", " bill ", "atmp",
]

EDITABLE_FIELDS = ["Topical/Cosmetic", "Soft Indications", "IV/Therapeutic"]
RISK_LEVELS     = ["🔴 HIGH", "🟡 MEDIUM", "🟡 LOW-MED", "🟢 LOW"]
SEEN_HEADERS    = ["hash", "date_seen", "territory", "verdict", "title", "link"]

SYSTEM_PROMPT = f"""You are a regulatory analyst for a BM-MSC exosome manufacturer selling
non-IND, non-therapeutic products (B2B cosmetic / aesthetic / soft medical channels),
with a longer-term IV/therapeutic pipeline.

You get one territory's current regulation row and one news article. Decide whether
the article reports a NEW, CONCRETE regulatory development (law, decree, guidance,
enforcement action, approval, ban, classification decision) in that territory that
the row does not already reflect. Clinic marketing, product launches, general
explainers, research papers and other territories do NOT count.

Return ONLY valid JSON with these exact fields:
{{
  "material": true or false,
  "field": one of {json.dumps(EDITABLE_FIELDS)} or null,
  "new_text": "full replacement text for that field, keeping still-valid existing facts, max 400 chars, prefix new facts with month+year" or null,
  "risk": one of {json.dumps(RISK_LEVELS)} (repeat the current risk unless the development clearly changes it),
  "change_flag": "🆕 short label, max 90 chars" or null,
  "rationale": "one sentence, max 200 chars"
}}

Return ONLY the JSON object. No markdown, no explanation."""


def make_hash(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()[:12]


def load_regulatory() -> tuple[list, list]:
    with open(REG_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader), reader.fieldnames


def load_seen() -> set:
    if not os.path.exists(SEEN_FILE):
        return set()
    with open(SEEN_FILE, "r", encoding="utf-8") as f:
        return {row["hash"] for row in csv.DictReader(f)}


def fetch_territory_news(territory: str) -> tuple[list, int]:
    """Returns (regulatory-looking articles, raw entry count). The raw count
    lets main() tell a dead feed apart from a week with no regulatory news."""
    articles, seen_titles, raw_count = [], set(), 0
    for term in TERRITORY_TERMS[territory]:
        for topic in TOPIC_TERMS:
            query = f'{term} {topic} when:{LOOKBACK_DAYS}d'
            url = "https://news.google.com/rss/search?" + urllib.parse.urlencode(
                {"q": query, "hl": "en-US", "gl": "US", "ceid": "US:en"})
            feed = feedparser.parse(url)
            raw_count += len(feed.entries)
            for entry in feed.entries:
                title = getattr(entry, "title", "")
                if title in seen_titles or not any(kw in title.lower() for kw in REGULATORY_KEYWORDS):
                    continue
                seen_titles.add(title)
                pub = getattr(entry, "published_parsed", None)
                articles.append({
                    "title":     title,
                    "summary":   getattr(entry, "summary", title)[:600],
                    "link":      getattr(entry, "link", ""),
                    "date":      datetime.date(*pub[:3]).isoformat() if pub else datetime.date.today().isoformat(),
                    "territory": territory,
                    "hash":      make_hash(territory + "|" + title),
                })
    # Exosome stories first, then newest (stable two-pass sort)
    articles.sort(key=lambda a: a["date"], reverse=True)
    articles.sort(key=lambda a: "exosome" not in a["title"].lower())
    return articles[:MAX_ARTICLES_PER_TERRITORY], raw_count


class GroqCallError(Exception):
    """Raised when the Groq API call itself fails — distinct from the model
    judging an article not material."""


def assess(client: Groq, row: dict, article: dict) -> dict | None:
    current = {k: row.get(k, "") for k in ["Territory", "Body", *EDITABLE_FIELDS, "Risk", "Last Updated"]}
    prompt = (f"Current row:\n{json.dumps(current, ensure_ascii=False)}\n\n"
              f"Article ({article['date']}):\nTitle: {article['title']}\nSummary: {article['summary']}")
    try:
        r = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt},
            ],
            temperature=0.1,
            max_tokens=600,
        )
    except Exception as e:
        print(f"  Groq error: {e}")
        raise GroqCallError(str(e)) from e

    try:
        raw = r.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except Exception as e:
        print(f"  Response parse error: {e}")
        return None


def write_summary(path: str, changes: list, reviewed: int) -> None:
    lines = [
        f"## Proposed regulatory updates — {datetime.date.today()}",
        "",
        f"Reviewed {reviewed} new article(s) across {len(TERRITORY_TERMS)} territories; "
        f"{len(changes)} proposed change(s). Please check each source before merging — "
        "edits are AI-drafted, and risk ratings feed market-entry decisions.",
        "",
    ]
    for c in changes:
        lines += [
            f"### {c['territory']} — {c['field']}",
            f"**Source:** [{c['title']}]({c['link']}) ({c['date']})",
            f"**Why:** {c['rationale']}",
        ]
        if c["old_risk"] != c["new_risk"]:
            lines.append(f"**⚠️ Risk change:** {c['old_risk']} → {c['new_risk']}")
        lines += ["", f"- Before: {c['before']}", f"- After: {c['after']}", ""]
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main():
    summary_path = sys.argv[1] if len(sys.argv) > 1 else "regulatory_summary.md"
    print(f"\n{'='*60}")
    print(f"Regulatory Update Fetcher — {datetime.date.today()}")
    print(f"{'='*60}\n")

    rows, fieldnames = load_regulatory()
    by_territory = {r["Territory"]: r for r in rows}
    seen = load_seen()

    articles, total_raw = [], 0
    for territory in TERRITORY_TERMS:
        if territory not in by_territory:
            print(f"  ⚠️  {territory} not in regulatory.csv — skipped")
            continue
        found, raw_count = fetch_territory_news(territory)
        total_raw += raw_count
        new = [a for a in found if a["hash"] not in seen]
        print(f"  [{territory}] {raw_count} raw, {len(found)} regulatory-looking, {len(new)} new")
        articles.extend(new)

    if total_raw == 0:
        print("\n❌ Every territory query returned 0 entries — the feed URL is likely dead, "
              "not a quiet week. Check fetch_territory_news().")
        raise SystemExit(1)

    print(f"\nNew articles to assess: {len(articles)}")
    client = Groq(api_key=GROQ_KEY) if articles else None
    changes, seen_rows, groq_errors = [], [], 0
    today = datetime.datetime.utcnow()

    for i, article in enumerate(articles, 1):
        print(f"  [{i}/{len(articles)}] {article['territory']}: {article['title'][:70]}")
        row = by_territory[article["territory"]]
        try:
            result = assess(client, row, article)
        except GroqCallError:
            groq_errors += 1
            continue  # not logged as seen — retried next run

        field = (result or {}).get("field")
        material = bool(result and result.get("material") and field in EDITABLE_FIELDS and result.get("new_text"))
        seen_rows.append({
            "hash": article["hash"], "date_seen": today.strftime("%Y-%m-%d"),
            "territory": article["territory"], "verdict": "proposed" if material else "not material",
            "title": article["title"][:200], "link": article["link"],
        })
        if not material:
            print("         → not material")
            continue

        new_risk = result.get("risk") if result.get("risk") in RISK_LEVELS else row["Risk"]
        changes.append({
            **article, "field": field, "rationale": result.get("rationale", ""),
            "before": row[field], "after": result["new_text"][:400],
            "old_risk": row["Risk"], "new_risk": new_risk,
        })
        row[field]          = result["new_text"][:400]
        row["Risk"]         = new_risk
        row["Change Flag"]  = (result.get("change_flag") or "🆕 Auto-proposed update")[:90]
        row["Source URL"]   = article["link"]
        row["Last Updated"] = today.strftime("%b %Y")
        row["date_added"]   = today.strftime("%Y-%m-%d")
        print(f"         → proposed edit to {field}")

    if articles and groq_errors == len(articles):
        print(f"\n❌ All {groq_errors} Groq API calls failed — treating this as a hard failure. "
              f"Check GROQ_API_KEY and GROQ_MODEL.")
        raise SystemExit(1)

    if changes:
        with open(REG_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)

    if seen_rows:
        file_exists = os.path.exists(SEEN_FILE)
        with open(SEEN_FILE, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=SEEN_HEADERS, lineterminator="\n")
            if not file_exists:
                writer.writeheader()
            writer.writerows(seen_rows)

    write_summary(summary_path, changes, len(articles))
    if groq_errors:
        print(f"\n⚠️  {groq_errors}/{len(articles)} articles skipped due to Groq API errors.")
    print(f"\n✅ Done — {len(changes)} change(s) proposed. Summary: {summary_path}\n")


if __name__ == "__main__":
    main()

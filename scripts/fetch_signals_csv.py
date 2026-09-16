"""
fetch_signals_csv.py
Fetches exosome market signals from bot-friendly RSS/Atom feeds plus the
NCBI E-utilities API, categorizes with Groq AI, and appends new signals
to data/signals.csv.

Sources:
  - PubMed          (NIH E-utilities esearch/esummary — NOT RSS; PubMed's
                      term-based RSS URL serves an HTML search page, not a
                      feed, so feedparser silently got 0 entries from it.
                      See fetch_pubmed_articles().)
  - FDA RSS          (FDA.gov press releases — the old biologics/warning-
                      letters RSS paths 404 after FDA's site redesign)
  - BioSpace RSS      (biotech news — old /rss/news path 404s; now /all-news.rss)
  - GlobeNewswire RSS (press releases — no bot-blocking)
  - PRNewswire RSS    (press releases — no bot-blocking)
  - ClinicalTrials.gov RSS (trial updates — no bot-blocking)

  Dropped: EMA — europa.eu no longer publishes a working sitewide news RSS
  (every URL we could find is an HTML landing page for a per-medicine RSS
  builder, not a feed itself).

NOTE ON SILENT FAILURE: feedparser does not raise on a 404 — it just parses
whatever HTML comes back, finds no <item> elements, and returns an empty
entries list. A dead feed URL therefore looks identical in the logs to "no
new articles today". Always verify a feed change with a direct curl check
of the URL before trusting "0 relevant entries" as a healthy result.

Requirements: pip install feedparser groq
"""

import os, csv, json, hashlib, datetime, urllib.request, urllib.parse, feedparser
from groq import Groq

DATA_DIR     = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
SIGNALS_FILE = os.path.join(DATA_DIR, "signals.csv")
META_FILE    = os.path.join(DATA_DIR, "meta.csv")
GROQ_KEY     = os.environ["GROQ_API_KEY"]
GROQ_MODEL   = "openai/gpt-oss-120b"  # llama-3.3-70b-versatile was decommissioned by Groq 2026-08-16
LOOKBACK_DAYS = 10   # slightly wider window for safety

# ── PubMed — via NCBI E-utilities, not RSS (see module docstring) ─
PUBMED_QUERIES = [
    ("exosome MSC therapy",              "Structural"),
    ("extracellular vesicle clinical trial", "Regulatory"),
    ("exosome aesthetic skin",           "Structural"),
]

# ── Bot-friendly RSS feeds ────────────────────────────────────────
FEEDS = [
    # FDA press releases — the old biologics/warning-letters RSS paths 404;
    # this one is confirmed live
    ("https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/press-releases/rss.xml",
     "Enforcement", "FDA"),

    # BioSpace — biotech news; old /rss/news path 404s, this one is confirmed live
    ("https://www.biospace.com/all-news.rss",
     "Investment", "BioSpace"),

    # GlobeNewswire — press releases
    ("https://www.globenewswire.com/RssFeed/subjectcode/15-Life+Sciences",
     "Partnership", "GlobeNewswire"),
    ("https://www.globenewswire.com/RssFeed/subjectcode/1-Mergers+%26+Acquisitions",
     "M&A", "GlobeNewswire"),

    # PRNewswire — life sciences
    ("https://www.prnewswire.com/rss/news-releases-list.rss?tagid=313",
     "Partnership", "PRNewswire"),

    # ClinicalTrials.gov — exosome trials
    ("https://classic.clinicaltrials.gov/ct2/results/rss.xml?rcv_d=14&lup_d=14&sel_rss=new14&cond=exosome&count=20",
     "Regulatory", "ClinicalTrials"),
    ("https://classic.clinicaltrials.gov/ct2/results/rss.xml?rcv_d=14&lup_d=14&sel_rss=new14&term=extracellular+vesicle&count=20",
     "Regulatory", "ClinicalTrials"),
]

RELEVANCE_KEYWORDS = [
    "exosome", "msc", "mesenchymal", "extracellular vesicle", "ev therapy",
    "stem cell exosome", "regenerative aesthetic", "exosome market",
    "exosome therapy", "exopten", "nurexone", "roosterbio", "exocobio",
    "stem nova", "kimera", "anteage", "exo biologic",
]

SYSTEM_PROMPT = """You are a market intelligence analyst for the global MSC exosome
market (regenerative aesthetics, longevity, soft medical indications, therapeutic).

For each article return ONLY valid JSON with these exact fields:
{
  "relevant": true or false,
  "type": one of ["Regulatory","Enforcement","Partnership","Investment","M&A","Structural","Pricing","Geographic","Warning"],
  "event": "one sentence max 120 chars",
  "impact": "one sentence commercial impact for a BM-MSC exosome manufacturer, max 120 chars",
  "sentiment": one of ["Positive","Risk","Neutral"],
  "territory": "most relevant geography e.g. USA, EU, Thailand, UAE, Global, South Korea"
}

Return ONLY the JSON object. No markdown, no explanation."""


def make_hash(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()[:12]


def load_existing_hashes() -> set:
    if not os.path.exists(SIGNALS_FILE):
        return set()
    hashes = set()
    with open(SIGNALS_FILE, "r", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("hash"):
                hashes.add(row["hash"])
            if row.get("event"):
                hashes.add(make_hash(row["event"]))
    return hashes


def fetch_pubmed_articles() -> list:
    """PubMed has no working ad-hoc term-based RSS (the old URL serves an
    HTML search page, not a feed — see module docstring), so we go through
    NCBI's E-utilities JSON API instead: esearch for matching PMIDs in the
    lookback window, then esummary for titles/dates."""
    articles = []
    for query, hint_type in PUBMED_QUERIES:
        try:
            esearch_url = (
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?"
                + urllib.parse.urlencode({
                    "db": "pubmed", "term": query, "retmax": 20,
                    "retmode": "json", "datetype": "pdat", "reldate": LOOKBACK_DAYS,
                })
            )
            with urllib.request.urlopen(esearch_url, timeout=15) as resp:
                ids = json.loads(resp.read())["esearchresult"]["idlist"]

            if not ids:
                print(f"  [PubMed] {hint_type} ({query!r}): 0 relevant entries")
                continue

            esummary_url = (
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?"
                + urllib.parse.urlencode({"db": "pubmed", "id": ",".join(ids), "retmode": "json"})
            )
            with urllib.request.urlopen(esummary_url, timeout=15) as resp:
                result = json.loads(resp.read())["result"]

            count_added = 0
            for pmid in result.get("uids", []):
                item = result[pmid]
                title = item.get("title", "")
                link = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                articles.append({
                    "title":        title,
                    "summary":      title,  # esummary has no abstract text; title carries the signal
                    "link":         link,
                    "date":         datetime.date.today().isoformat(),
                    "hint_type":    hint_type,
                    "source_label": "PubMed",
                    "hash":         make_hash(title),
                })
                count_added += 1
            print(f"  [PubMed] {hint_type} ({query!r}): {count_added} relevant entries")
        except Exception as e:
            print(f"  Feed error (PubMed {query!r}): {e}")
    return articles


def fetch_articles() -> list:
    cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=LOOKBACK_DAYS)
    articles, seen_links = [], set()

    articles.extend(fetch_pubmed_articles())
    for a in articles:
        seen_links.add(a["link"])

    for url, hint_type, source_label in FEEDS:
        try:
            feed = feedparser.parse(url)
            count_added = 0
            for entry in feed.entries:
                link    = getattr(entry, "link",    "")
                title   = getattr(entry, "title",   "")
                summary = getattr(entry, "summary", getattr(entry, "description", title))

                if link in seen_links:
                    continue
                seen_links.add(link)

                # Date filter
                pub = getattr(entry, "published_parsed", None)
                if pub:
                    pub_dt = datetime.datetime(*pub[:6])
                    if pub_dt < cutoff:
                        continue
                    pub_str = pub_dt.strftime("%Y-%m-%d")
                else:
                    pub_str = datetime.date.today().isoformat()

                # Relevance pre-filter
                combined = (title + " " + summary).lower()
                if not any(kw in combined for kw in RELEVANCE_KEYWORDS):
                    continue

                articles.append({
                    "title":        title,
                    "summary":      summary[:600],
                    "link":         link,
                    "date":         pub_str,
                    "hint_type":    hint_type,
                    "source_label": source_label,
                    "hash":         make_hash(title),
                })
                count_added += 1

            print(f"  [{source_label}] {hint_type}: {count_added} relevant entries")
        except Exception as e:
            print(f"  Feed error ({source_label}): {e}")

    print(f"\nTotal relevant articles fetched: {len(articles)}")
    return articles


class GroqCallError(Exception):
    """Raised when the Groq API call itself fails (bad model, auth, rate limit, etc.)
    — distinct from the model legitimately judging an article 'not relevant'."""


def categorize(client: Groq, article: dict) -> dict | None:
    prompt = f"Title: {article['title']}\nSource: {article['source_label']}\nSummary: {article['summary']}"
    try:
        r = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt},
            ],
            temperature=0.1,
            max_tokens=250,
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


def append_to_csv(new_rows: list) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    file_exists = os.path.exists(SIGNALS_FILE)
    headers = ["date", "type", "event", "impact", "sentiment",
               "source", "territory", "auto_generated", "hash", "date_added"]
    with open(SIGNALS_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        if not file_exists:
            writer.writeheader()
        for row in new_rows:
            writer.writerow(row)
    print(f"✅ Appended {len(new_rows)} new signals to signals.csv")


def update_meta() -> None:
    rows = []
    if os.path.exists(META_FILE):
        with open(META_FILE, "r", encoding="utf-8") as f:
            rows = list(csv.reader(f))
    now_str = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    prev_val = ""
    updated_last = False
    updated_prev = False
    for row in rows:
        if row and row[0] == "last_run":
            prev_val = row[1]
            row[1] = now_str
            updated_last = True
        elif row and row[0] == "prev_last_run":
            row[1] = prev_val
            updated_prev = True
    if not updated_last:
        rows.append(["last_run", now_str])
    if not updated_prev:
        rows.append(["prev_last_run", prev_val])
    with open(META_FILE, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)


def main():
    print(f"\n{'='*60}")
    print(f"Exosome Signal Fetcher — {datetime.date.today()}")
    print(f"Sources: PubMed (E-utilities), FDA, BioSpace, GlobeNewswire, PRNewswire, ClinicalTrials")
    print(f"{'='*60}\n")

    existing_hashes = load_existing_hashes()
    print(f"Existing signals: {len(existing_hashes)}\n")

    articles = fetch_articles()
    new_articles = [a for a in articles if a["hash"] not in existing_hashes]
    print(f"New articles to process: {len(new_articles)}")

    if not new_articles:
        print("Nothing new — CSV is up to date.")
        update_meta()
        return

    client = Groq(api_key=GROQ_KEY)
    new_signals = []
    groq_errors = 0
    sentiment_map = {"Positive": "🟢 Positive", "Risk": "🔴 Risk", "Neutral": "🟡 Neutral"}

    for i, article in enumerate(new_articles, 1):
        print(f"  [{i}/{len(new_articles)}] {article['title'][:70]}")
        try:
            result = categorize(client, article)
        except GroqCallError:
            groq_errors += 1
            continue

        if not result or not result.get("relevant", False):
            print("         → not relevant, skipped")
            continue

        new_signals.append({
            "date":           article["date"],
            "type":           result.get("type",   article["hint_type"]),
            "event":          result.get("event",  article["title"])[:200],
            "impact":         result.get("impact", "")[:200],
            "sentiment":      sentiment_map.get(result.get("sentiment", "Neutral"), "🟡 Neutral"),
            "source":         article["link"],
            "territory":      result.get("territory", "Global"),
            "auto_generated": "auto",
            "hash":           article["hash"],
            "date_added":     datetime.datetime.utcnow().strftime("%Y-%m-%d"),
        })

    # If every single Groq call failed (bad model id, revoked key, outage),
    # committing "0 signals added" would look identical to a quiet news day.
    # Fail the workflow loudly instead so it doesn't rot silently again.
    if groq_errors > 0 and groq_errors == len(new_articles):
        print(f"\n❌ All {groq_errors} Groq API calls failed — treating this as a hard failure, "
              f"not 'nothing new'. Check GROQ_API_KEY and GROQ_MODEL.")
        raise SystemExit(1)

    append_to_csv(new_signals)
    update_meta()
    if groq_errors:
        print(f"\n⚠️  {groq_errors}/{len(new_articles)} articles skipped due to Groq API errors.")
    print(f"\n✅ Done — {len(new_signals)} signals added.\n")


if __name__ == "__main__":
    main()

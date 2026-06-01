"""
fetch_signals_csv.py
Fetches exosome market signals from bot-friendly RSS/Atom feeds,
categorizes with Groq AI, and appends new signals to data/signals.csv.

Replaces Google News RSS (which blocks GitHub Actions IPs) with:
  - PubMed RSS         (NIH — always accessible from CI)
  - FDA RSS            (FDA.gov — always accessible from CI)
  - EMA RSS            (EMA.europa.eu — always accessible from CI)
  - BioSpace RSS       (biotech news — no bot-blocking)
  - GlobeNewswire RSS  (press releases — no bot-blocking)
  - PRNewswire RSS     (press releases — no bot-blocking)
  - ClinicalTrials.gov RSS (trial updates — no bot-blocking)

Requirements: pip install feedparser groq
"""

import os, csv, json, hashlib, datetime, feedparser
from groq import Groq

DATA_DIR     = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
SIGNALS_FILE = os.path.join(DATA_DIR, "signals.csv")
META_FILE    = os.path.join(DATA_DIR, "meta.csv")
GROQ_KEY     = os.environ["GROQ_API_KEY"]
LOOKBACK_DAYS = 10   # slightly wider window for safety

# ── Bot-friendly RSS feeds ────────────────────────────────────────
FEEDS = [
    # PubMed — NIH RSS, never blocked from CI
    ("https://pubmed.ncbi.nlm.nih.gov/rss/search/?term=exosome+MSC+therapy&format=abstract&limit=20",
     "Structural", "PubMed"),
    ("https://pubmed.ncbi.nlm.nih.gov/rss/search/?term=extracellular+vesicle+clinical+trial&format=abstract&limit=20",
     "Regulatory", "PubMed"),
    ("https://pubmed.ncbi.nlm.nih.gov/rss/search/?term=exosome+aesthetic+skin&format=abstract&limit=20",
     "Structural", "PubMed"),

    # FDA news & safety alerts — always open
    ("https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/biologics-blood-vaccines/rss.xml",
     "Enforcement", "FDA"),
    ("https://www.fda.gov/about-fda/contact-fda/stay-informed/rss-feeds/warning-letters/rss.xml",
     "Enforcement", "FDA"),

    # EMA news
    ("https://www.ema.europa.eu/en/news-events/rss-feeds",
     "Regulatory", "EMA"),

    # BioSpace — biotech news, no bot-blocking
    ("https://www.biospace.com/rss/news",
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


def fetch_articles() -> list:
    cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=LOOKBACK_DAYS)
    articles, seen_links = [], set()

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


def categorize(client: Groq, article: dict) -> dict | None:
    prompt = f"Title: {article['title']}\nSource: {article['source_label']}\nSummary: {article['summary']}"
    try:
        r = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": prompt},
            ],
            temperature=0.1,
            max_tokens=250,
        )
        raw = r.choices[0].message.content.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        return json.loads(raw)
    except Exception as e:
        print(f"  Groq error: {e}")
        return None


def append_to_csv(new_rows: list) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    file_exists = os.path.exists(SIGNALS_FILE)
    headers = ["date", "type", "event", "impact", "sentiment",
               "source", "territory", "auto_generated", "hash"]
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
    updated = False
    for row in rows:
        if row and row[0] == "last_run":
            row[1] = now_str
            updated = True
    if not updated:
        rows.append(["last_run", now_str])
    with open(META_FILE, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)


def main():
    print(f"\n{'='*60}")
    print(f"Exosome Signal Fetcher — {datetime.date.today()}")
    print(f"Sources: PubMed, FDA, EMA, BioSpace, GlobeNewswire, PRNewswire, ClinicalTrials")
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
    sentiment_map = {"Positive": "🟢 Positive", "Risk": "🔴 Risk", "Neutral": "🟡 Neutral"}

    for i, article in enumerate(new_articles, 1):
        print(f"  [{i}/{len(new_articles)}] {article['title'][:70]}")
        result = categorize(client, article)

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
        })

    append_to_csv(new_signals)
    update_meta()
    print(f"\n✅ Done — {len(new_signals)} signals added.\n")


if __name__ == "__main__":
    main()

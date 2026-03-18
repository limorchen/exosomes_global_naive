"""
fetch_signals_csv.py
Fetches exosome market news via Google News RSS, categorizes with Groq AI,
and appends new signals to data/signals.csv in the repo.

GitHub Actions commits the updated CSV back to the repo automatically.
No Google credentials needed.

Requirements: pip install feedparser groq
"""

import os
import csv
import json
import hashlib
import datetime
import feedparser
from groq import Groq

DATA_DIR     = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
SIGNALS_FILE = os.path.join(DATA_DIR, "signals.csv")
META_FILE    = os.path.join(DATA_DIR, "meta.csv")
GROQ_KEY     = os.environ["GROQ_API_KEY"]
LOOKBACK_DAYS = 8

FEEDS = [
    ("https://news.google.com/rss/search?q=exosome+FDA+warning+letter&hl=en-US&gl=US&ceid=US:en",            "Enforcement"),
    ("https://news.google.com/rss/search?q=exosome+regulatory+approval&hl=en-US&gl=US&ceid=US:en",           "Regulatory"),
    ("https://news.google.com/rss/search?q=MSC+exosome+regulation&hl=en-US&gl=US&ceid=US:en",                "Regulatory"),
    ("https://news.google.com/rss/search?q=exosome+EMA+ATMP&hl=en-US&gl=US&ceid=US:en",                     "Regulatory"),
    ("https://news.google.com/rss/search?q=exosome+Thai+FDA+Thailand&hl=en-US&gl=US&ceid=US:en",             "Regulatory"),
    ("https://news.google.com/rss/search?q=ANVISA+exosome+Brazil&hl=en-US&gl=US&ceid=US:en",                 "Regulatory"),
    ("https://news.google.com/rss/search?q=exosome+market+partnership+distributor&hl=en-US&gl=US&ceid=US:en","Partnership"),
    ("https://news.google.com/rss/search?q=exosome+investment+funding+series&hl=en-US&gl=US&ceid=US:en",     "Investment"),
    ("https://news.google.com/rss/search?q=exosome+acquisition+merger&hl=en-US&gl=US&ceid=US:en",            "M&A"),
    ("https://news.google.com/rss/search?q=exosome+pricing+cost+manufacturing&hl=en-US&gl=US&ceid=US:en",    "Structural"),
    ("https://news.google.com/rss/search?q=exosome+lyophilization+cold+chain&hl=en-US&gl=US&ceid=US:en",     "Structural"),
    ("https://news.google.com/rss/search?q=exosome+UAE+Dubai+longevity&hl=en-US&gl=US&ceid=US:en",           "Geographic"),
    ("https://news.google.com/rss/search?q=exosome+Southeast+Asia+aesthetic&hl=en-US&gl=US&ceid=US:en",      "Geographic"),
    ("https://news.google.com/rss/search?q=stem+cell+exosome+therapy+clinic&hl=en-US&gl=US&ceid=US:en",      "Structural"),
]

RELEVANCE_KEYWORDS = [
    "exosome","msc","mesenchymal","extracellular vesicle","ev therapy",
    "stem cell therapy","regenerative aesthetic","exosome market",
]

SYSTEM_PROMPT = """You are a market intelligence analyst for the global MSC exosome 
market (regenerative aesthetics, longevity, soft medical indications).

For each article return ONLY valid JSON with these exact fields:
{
  "relevant": true or false,
  "type": one of ["Regulatory","Enforcement","Partnership","Investment","M&A","Structural","Pricing","Geographic","Warning"],
  "event": "one sentence max 120 chars",
  "impact": "one sentence commercial impact for a BM-MSC manufacturer max 120 chars",
  "sentiment": one of ["Positive","Risk","Neutral"],
  "territory": "most relevant geography e.g. USA, EU, Thailand, UAE, Global"
}

Return ONLY the JSON object. No markdown, no explanation."""

def make_hash(text):
    return hashlib.md5(text.encode()).hexdigest()[:12]

def load_existing_hashes():
    if not os.path.exists(SIGNALS_FILE):
        return set()
    with open(SIGNALS_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return {row.get("hash","") for row in reader if row.get("hash")}

def fetch_articles():
    cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=LOOKBACK_DAYS)
    articles, seen_links = [], set()

    for url, hint_type in FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                link    = getattr(entry, "link",    "")
                title   = getattr(entry, "title",   "")
                summary = getattr(entry, "summary", title)

                if link in seen_links:
                    continue
                seen_links.add(link)

                pub = getattr(entry, "published_parsed", None)
                if pub:
                    pub_dt = datetime.datetime(*pub[:6])
                    if pub_dt < cutoff:
                        continue
                    pub_str = pub_dt.strftime("%Y-%m-%d")
                else:
                    pub_str = datetime.date.today().isoformat()

                combined = (title + " " + summary).lower()
                if not any(kw in combined for kw in RELEVANCE_KEYWORDS):
                    continue

                articles.append({
                    "title":     title,
                    "summary":   summary[:600],
                    "link":      link,
                    "date":      pub_str,
                    "hint_type": hint_type,
                    "hash":      make_hash(title),
                })
        except Exception as e:
            print(f"  Feed error: {e}")

    print(f"Fetched {len(articles)} relevant articles")
    return articles

def categorize(client, article):
    prompt = f"Title: {article['title']}\nSummary: {article['summary']}"
    try:
        r = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role":"system","content":SYSTEM_PROMPT},
                {"role":"user",  "content":prompt},
            ],
            temperature=0.1,
            max_tokens=250,
        )
        raw = r.choices[0].message.content.strip()
        raw = raw.replace("```json","").replace("```","").strip()
        return json.loads(raw)
    except Exception as e:
        print(f"  Groq error: {e}")
        return None

def append_to_csv(new_rows):
    os.makedirs(DATA_DIR, exist_ok=True)
    file_exists = os.path.exists(SIGNALS_FILE)

    with open(SIGNALS_FILE, "a", newline="", encoding="utf-8") as f:
        headers = ["date","type","event","impact","sentiment","source","territory","auto_generated","hash"]
        writer  = csv.DictWriter(f, fieldnames=headers)
        if not file_exists:
            writer.writeheader()
        for row in new_rows:
            writer.writerow(row)

    print(f"✅ Appended {len(new_rows)} new signals to signals.csv")

def update_meta():
    rows = []
    if os.path.exists(META_FILE):
        with open(META_FILE, "r", encoding="utf-8") as f:
            rows = list(csv.reader(f))

    # Update or add last_run row
    updated = False
    now_str = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    for row in rows:
        if row and row[0] == "last_run":
            row[1] = now_str
            updated = True
    if not updated:
        rows.append(["last_run", now_str])

    with open(META_FILE, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerows(rows)

def main():
    print(f"\n{'='*55}")
    print(f"Exosome Signal Fetcher (CSV) — {datetime.date.today()}")
    print(f"{'='*55}\n")

    existing_hashes = load_existing_hashes()
    print(f"Existing signals in CSV: {len(existing_hashes)}")

    articles = fetch_articles()
    new_articles = [a for a in articles if a["hash"] not in existing_hashes]
    print(f"New articles to process: {len(new_articles)}")

    if not new_articles:
        print("Nothing new — CSV is up to date.")
        update_meta()
        return

    client     = Groq(api_key=GROQ_KEY)
    new_signals = []

    for i, article in enumerate(new_articles, 1):
        print(f"  [{i}/{len(new_articles)}] {article['title'][:70]}")
        result = categorize(client, article)

        if not result or not result.get("relevant", False):
            print("         → skipped")
            continue

        sentiment_map = {"Positive":"🟢 Positive","Risk":"🔴 Risk","Neutral":"🟡 Neutral"}
        new_signals.append({
            "date":           article["date"],
            "type":           result.get("type",      article["hint_type"]),
            "event":          result.get("event",     article["title"])[:200],
            "impact":         result.get("impact",    "")[:200],
            "sentiment":      sentiment_map.get(result.get("sentiment","Neutral"),"🟡 Neutral"),
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

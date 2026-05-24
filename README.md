# 🧬 Global Naive MSC Exosome Market Dashboard

Strategic intelligence for BM-MSC-derived exosome market entry — built for [NurExone Biologic](https://nurexone.com).

## 🔗 Live Dashboard

**👉 [Open the dashboard](https://YOUR-STREAMLIT-URL.streamlit.app)**
> Replace this link once deployed on Streamlit Community Cloud

---

## What's inside

| Tab | Contents |
|-----|----------|
| 📊 Market Overview | 6 KPI cards · 5-source market size triangulation · regional forecasts 2024–2030 |
| 🗺️ Geographic Analysis | **Choropleth world map** · regulatory risk by country · bubble chart · CEE & US state detail |
| 🏢 Distributors & Entry Points | 25+ named distributors · filterable by region/channel/priority · B2B price waterfall |
| ⚖️ Regulation | 16-territory regulatory framework · milestone timeline · ANVISA-COFEPRIS MoU |
| 💰 Pricing & COGS | Per-10B benchmark · OOP patient pricing · B2B tiers · COGS breakdown · **Margin Scenario Modeler** |
| 📡 Signals & Trends | Auto-updated market signals · trend cards |
| ✅ Strategy Checklist | 14 prioritised actions (CRITICAL → MEDIUM) |

---

## Running locally

```bash
pip install -r requirements.txt
streamlit run market_dashboard_v2.py
```

---

## Live data pipeline

Market signals auto-update every Monday at 7am UTC via GitHub Actions:

- `data/signals.csv` — fetched from Google News RSS + Groq summarisation
- `data/meta.csv` — timestamp of last run
- `data/distributors.csv`, `data/regulatory.csv`, `data/pricing.csv` — manually maintained; dashboard falls back to static baseline if absent

To trigger a manual update: **Actions → Update Exosome Market Signals → Run workflow**

---

## Data sources

InsightAce Analytic · The Insight Partners · Coherent Market Insights · Future Market Insights ·
Credence Research · Grand View Research · Astute Analytica · RoosterBio · Atlantis Bioscience ·
Jolifill.de · HUK Aesthetics · Bookimed · DIA Global Forum · FDA.gov · TGA.gov.au ·
HSA Singapore · PH FDA · Florida Statute §456.47 · Nevada SB128/AB148

> ⚠️ Market figures are summary-level intelligence only. Regulatory guidance is not legal advice.
> Consult qualified regulatory counsel before commercial launch.

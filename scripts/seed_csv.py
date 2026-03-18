"""
seed_csv.py
One-time script to populate /data/*.csv files with baseline dashboard data.
No Google credentials needed — just run it and commit the CSVs to GitHub.

Usage:
    python scripts/seed_csv.py
"""

import os
import csv
import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")

def write_csv(filename, headers, rows):
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, filename)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    print(f"  ✅ {filename}: {len(rows)} rows written")

# ── SIGNALS ───────────────────────────────────────────────────────────────────
SIGNALS_HEADERS = ["date","type","event","impact","sentiment","source","territory","auto_generated","hash"]
SIGNALS_ROWS = [
    ["Jan 2026",  "Regulatory",  "Philippine FDA Cosmetic Notification — UnicoCell",           "ASEAN gateway validated; blueprint for TH, MY, ID",             "🟢 Positive", "", "Philippines",  "manual", ""],
    ["May 2025",  "Enforcement", "FDA warning letter — Florida IV exosome clinic",             "US IV channel high risk; pivot to topical/cosmetic",            "🔴 Risk",     "", "USA",          "manual", ""],
    ["Late 2025", "Regulatory",  "ANVISA-COFEPRIS MoU fully operational",                     "Single approval pathway for Brazil and Mexico",                 "🟢 Positive", "", "LATAM",        "manual", ""],
    ["Feb 2025",  "Investment",  "ExoLab Italia raises EU5M Series A (plant-derived)",        "Plant-derived trend rising in EU; BM-MSC must counter",         "🟡 Neutral",  "", "EU",           "manual", ""],
    ["Jan 2025",  "Regulatory",  "Thai FDA drafting new health product import/export policy", "Favourable regulatory window to enter Thailand now",            "🟢 Positive", "", "Thailand",     "manual", ""],
    ["Mar 2024",  "Partnership", "Croma-Pharma x Aesthetic Management Partners (EU)",         "DACH region actively seeking new regenerative brands",          "🟢 Positive", "", "EU",           "manual", ""],
    ["Ongoing",   "Enforcement", "FDA: 12+ warning letters total on exosome products",        "US = cosmetic channel only for next 3-5 years",                 "🔴 Risk",     "", "USA",          "manual", ""],
    ["Jul 2023",  "M&A",         "ExoCoBio acquires majority stake in US BENEV",              "Market consolidating; window to establish brand now",           "🟢 Positive", "", "USA",          "manual", ""],
    ["2021",      "Regulatory",  "Thai FDA launches HSA Singapore Reliance Route",            "Singapore approval fast-tracks SEA/Thailand entry",             "🟢 Positive", "", "Thailand/SEA", "manual", ""],
    ["Ongoing",   "Structural",  "Lyophilisation segment $50-60M growing to $100M+ by 2030", "Cold-chain barrier eliminated globally",                        "🟢 Positive", "", "Global",       "manual", ""],
    ["Oct 2025",  "Enforcement", "Atlantis Bioscience documents 12+ FDA warning letters",     "Confirms US IV channel shutdown; cosmetic only pathway",        "🔴 Risk",     "", "USA",          "manual", ""],
    ["2025",      "Structural",  "RoosterBio hollow-fiber bioreactors cut media cost 60-70%","Largest BM-MSC COGS component now compressible at scale",      "🟢 Positive", "", "Global",       "manual", ""],
    ["Jan 2026",  "Structural",  "QY Research: lyophilization market forecast to 2032",      "Segment growing to low hundreds of millions early 2030s",       "🟢 Positive", "", "Global",       "manual", ""],
]

# ── DISTRIBUTORS ──────────────────────────────────────────────────────────────
DIST_HEADERS = ["distributor","region","territory","brands","approach","priority","channel","last_flagged","news_snippet"]
DIST_ROWS = [
    ["Jolifill",               "Europe",   "Germany",          "EXOXE, EXOMIDE, EXOJUV",       "Direct e-commerce + professional",          "🟢 High",   "Aesthetic",        "", ""],
    ["Croma-Pharma",           "Europe",   "Austria/DACH",     "Aesthetic Mgmt Partners",      "Strategic regional partnerships",           "🟢 High",   "Aesthetic",        "", ""],
    ["Teoxane France",         "Europe",   "France",           "Teoxane proprietary",          "Direct subsidiary model",                   "🟡 Medium", "Aesthetic",        "", ""],
    ["Taumedika S.r.l.",       "Europe",   "Italy",            "Karisma Exo Care",             "Specialist aesthetic networks",             "🟡 Medium", "Aesthetic",        "", ""],
    ["Teoxane Polska",         "Europe",   "Poland/CEE",       "EPICEXOSOME",                  "Emerging market expansion",                 "🟡 Medium", "Aesthetic",        "", ""],
    ["Giostar Mexico",         "LATAM",    "Mexico (Cancun)",  "Multiple MSC brands",          "Medical tourism + ortho",                   "🟢 High",   "Medical/Ortho",    "", ""],
    ["PRMEDICA",               "LATAM",    "Mexico (Cabos)",   "MSC exosomes",                 "Inflammatory modulation",                   "🟡 Medium", "Medical",          "", ""],
    ["R3 Stem Cell Brazil",    "LATAM",    "Brazil",           "R3 proprietary",               "Centers of Excellence",                     "🟢 High",   "Medical/Aesthetic","", ""],
    ["Vanguard Aesthetics",    "SEA",      "Philippines",      "Innovative med-aesthetic",     "ASEAN hub strategy",                        "🟢 High",   "Aesthetic",        "", ""],
    ["MGRC / GGA Malaysia",    "SEA",      "Malaysia",         "cGMP MSC exosomes",            "Research + diagnostics",                    "🟡 Medium", "Research",         "", ""],
    ["PT. Sel Regenerasi",     "SEA",      "Indonesia",        "Local brands",                 "Physician clinic training",                 "🟡 Medium", "Medical",          "", ""],
    ["Thai Aesthetic Clinics", "Thailand", "Bangkok/Phuket",   "Multi-brand",                  "Direct clinic supply via cosmetic notif.",  "🟢 High",   "Aesthetic",        "", ""],
    ["Bumrungrad/Samitivej",   "Thailand", "Thailand",         "Proprietary protocols",        "Premium private hospital group",            "🟡 Medium", "Medical",          "", ""],
    ["Innotech / Mega Life.",  "Thailand", "Thailand",         "Local pharma distribution",    "License + supply agreement",               "🟢 High",   "Pharma/Import",    "", ""],
    ["Biogenix / InterMed",    "Pacific",  "Australia",        "Cervos KeyPRP, Marrow Cell",   "TGA-compliant partnership",                 "🟡 Medium", "Medical",          "", ""],
    ["DUBIMED",                "UAE/GCC",  "UAE/Qatar/Oman",   "Galderma, Mesoestetic",        "Exclusive 40yr relationships",              "🟢 High",   "Aesthetic/Medical","", ""],
    ["Troya Aesthetics",       "UAE/GCC",  "UAE",              "Premium regional",             "Dermatologist patient care",               "🟡 Medium", "Aesthetic",        "", ""],
    ["EDEN AESTHETICS",        "UAE/GCC",  "Dubai",            "Integrative exosome protocol", "High-dose IV longevity",                   "🟢 High",   "Longevity IV",     "", ""],
    ["Regen Suppliers (R3)",   "USA",      "USA (national)",   "ReBellaXO (UC-MSC)",           "Position BM-MSC as premium ortho-grade",    "🟢 High",   "Medical/Aesthetic","", ""],
    ["Elevai Labs / BENEV",    "USA",      "USA",              "Elevai E30, ExoCoBio",         "OEM/white-label cosmetic topical",          "🟢 High",   "Aesthetic",        "", ""],
    ["Medical Spa chains",     "USA",      "USA (TX,FL,AZ)",   "Post-procedure adjuncts",      "Direct clinic supply — cosmetic only",     "🟡 Medium", "Aesthetic",        "", ""],
    ["US CDMO channel",        "USA",      "USA",              "Biotech/pharma clinical",      "GMP supply for Phase I/II trials",         "🟡 Medium", "Research/CDMO",    "", ""],
]

# ── REGULATORY ────────────────────────────────────────────────────────────────
REG_HEADERS = ["territory","body","topical_cosmetic","soft_indications","iv_therapeutic","risk","last_updated","change_flag"]
REG_ROWS = [
    ["USA",         "FDA",        "Permitted — no claims",             "Gray — physician discretion",                "IND required — 12+ warning letters",         "HIGH",    "Mar 2026", ""],
    ["EU",          "EMA",        "CE-IVD compliant",                  "Cosmetic grade only",                        "ATMP required — 0 approved",                 "HIGH",    "Mar 2026", ""],
    ["Australia",   "TGA",        "Cosmetic — limited claims",         "TGA-registered only",                        "ATMP / PBAC risk-sharing",                   "HIGH",    "Mar 2026", ""],
    ["Germany",     "BfArM",      "Cosmetic — active market",          "Medical spa channel",                        "ATMP pathway",                               "MEDIUM",  "Mar 2026", ""],
    ["France",      "ANSM",       "Cosmetic — active",                 "Dermatology protocols",                      "ATMP pathway",                               "MEDIUM",  "Mar 2026", ""],
    ["Switzerland", "Swissmedic", "High-value cosmetic",               "Longevity clinics (private)",                "Clinical registration",                      "MEDIUM",  "Mar 2026", ""],
    ["Brazil",      "ANVISA",     "RDC 949/2024 notification",         "IOR required",                               "AFE license required",                       "MEDIUM",  "Mar 2026", ""],
    ["South Korea", "MFDS",       "K-beauty cosmetic framework",       "Hospital partnerships",                      "Clinical approval route",                    "MEDIUM",  "Mar 2026", ""],
    ["UAE",         "MOHAP/DHA",  "CE/FDA-certified device",           "Clinic-based IV protocols — active",         "Strict cosmetic procedure standards",        "MEDIUM",  "Mar 2026", ""],
    ["Mexico",      "COFEPRIS",   "Cosmetic compliant",                "Physician dispensing — active",              "MoU reliance with ANVISA",                   "LOW",     "Mar 2026", ""],
    ["Thailand",    "Thai FDA",   "Cosmetic notification required",    "Gray area — active physician use",           "Drug Act B.E. 2510 — no explicit guideline", "LOW-MED", "Mar 2026", ""],
    ["Philippines", "PH FDA",     "Notification approved Jan 2026",    "ASEAN compliant",                            "Emerging",                                   "LOW",     "Jan 2026", ""],
    ["Malaysia",    "NPRA",       "ASEAN aligned",                     "cGMP research active",                       "Early stage",                                "LOW",     "Mar 2026", ""],
    ["Indonesia",   "BPOM",       "ASEAN cosmetic directive",          "Physician training pathway",                 "BPOM engaged",                               "LOW",     "Mar 2026", ""],
    ["Colombia",    "INVIMA",     "2025 Regional Reform",              "LATAM integration aligning",                 "Streamlined pathway",                        "LOW",     "Mar 2026", ""],
    ["Argentina",   "ANMAT",      "2025 Deregulation",                 "Fast-track entry",                           "Streamlined",                                "LOW",     "Mar 2026", ""],
]

# ── PRICING ───────────────────────────────────────────────────────────────────
PRICE_HEADERS = ["market","end_user_low","end_user_high","b2b_low","b2b_high","last_updated","change_flag"]
PRICE_ROWS = [
    ["Germany/EU",      280, 450, 140, 225, "Mar 2026", ""],
    ["UAE/GCC",         350, 600, 175, 300, "Mar 2026", ""],
    ["USA (aesthetic)", 300, 550, 150, 275, "Mar 2026", ""],
    ["Australia",       350, 600, 175, 300, "Mar 2026", ""],
    ["Mexico/LATAM",    200, 350, 100, 175, "Mar 2026", ""],
    ["Thailand",        180, 300,  90, 150, "Mar 2026", ""],
    ["Philippines/SEA", 150, 250,  75, 125, "Mar 2026", ""],
]

# ── META ──────────────────────────────────────────────────────────────────────
META_HEADERS = ["key","value"]
META_ROWS = [
    ["last_run",     f"Seeded {datetime.date.today().isoformat()}"],
    ["data_version", "v2.0"],
    ["report_date",  "March 2026"],
    ["seed_source",  "seed_csv.py"],
]

# ── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    print("\n" + "="*55)
    print("Exosome Dashboard — CSV Seed Script")
    print("="*55)
    print(f"Writing to: {DATA_DIR}\n")

    write_csv("signals.csv",      SIGNALS_HEADERS, SIGNALS_ROWS)
    write_csv("distributors.csv", DIST_HEADERS,    DIST_ROWS)
    write_csv("regulatory.csv",   REG_HEADERS,     REG_ROWS)
    write_csv("pricing.csv",      PRICE_HEADERS,   PRICE_ROWS)
    write_csv("meta.csv",         META_HEADERS,    META_ROWS)

    print("\n" + "="*55)
    print("✅ All CSV files written to /data folder")
    print("\nNext steps:")
    print("  1. Check the /data folder looks right in VS Code")
    print("  2. git add data/ && git commit -m 'seed baseline data'")
    print("  3. git push — Streamlit will pick it up automatically")
    print("="*55 + "\n")

if __name__ == "__main__":
    main()

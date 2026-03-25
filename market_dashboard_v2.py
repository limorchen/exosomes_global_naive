"""
Global Naive MSC Exosome Market Dashboard — v2 (March 2026)
Enhanced with: US & Thailand markets, BM-MSC COGS breakdown,
particle-normalized pricing, distributor attractiveness analysis,
and adaptable data config for live updating.

Run with: streamlit run market_dashboard_v2.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    layout="wide",
    page_title="Global MSC Exosome Market | March 2026",
    page_icon="🧬",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════
REPORT_DATE  = "March 2026"
DATA_VERSION = "v2.4-strategic"

# ── Change these to match your GitHub repo ───────────────────
GITHUB_USER = "limorchen"
GITHUB_REPO = "exosomes_global_naive"
BRANCH      = "main"
RAW_BASE    = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{BRANCH}/data"

# ══════════════════════════════════════════════════════════════
# LIVE DATA LOADER
# ══════════════════════════════════════════════════════════════
@st.cache_data(ttl=3600)
def load_csv(filename):
    """Load a CSV from the GitHub repo. Returns (dataframe, error_string)."""
    try:
        df = pd.read_csv(f"{RAW_BASE}/{filename}")
        df.columns = [c.strip() for c in df.columns]
        return df, None
    except Exception as e:
        return None, str(e)

@st.cache_data(ttl=3600)
def load_last_run():
    df, err = load_csv("meta.csv")
    if err or df is None:
        return "Not yet run"
    row = df[df["key"] == "last_run"]
    return row["value"].values[0] if not row.empty else "Unknown"

def get_live_or_static(live_df, static_df):
    """Return live data if available, fall back to static."""
    if live_df is not None and not live_df.empty:
        return live_df, True
    return static_df, False

def live_badge(is_live, last_run):
    if is_live:
        st.caption(f"🟢 Live data — last auto-updated: {last_run}")
    else:
        st.caption("🟡 Showing static baseline data")

# ── Load all live data once at startup ───────────────────────
live_signals,      signals_err  = load_csv("signals.csv")
live_distributors, dist_err     = load_csv("distributors.csv")
live_regulatory,   reg_err      = load_csv("regulatory.csv")
live_pricing,      price_err    = load_csv("pricing.csv")
last_run                        = load_last_run()

# ── CUSTOM CSS ─────────────────────────────────────────────────
st.markdown("""
<style>
  /* ── Base ── */
  [data-testid="stAppViewContainer"] { background:#f7f9fc; }
  h1 { letter-spacing:-0.5px; }

  /* ── Metric cards ── */
  .metric-card {
    background: linear-gradient(135deg,#1e3a5f 0%,#2e6da4 100%);
    border-radius:12px; padding:18px 14px; color:#fff; text-align:center;
    box-shadow:0 2px 8px rgba(30,58,95,.25);
  }
  .metric-value { font-size:1.85rem; font-weight:700; color:#7ec8e3; }
  .metric-label { font-size:0.78rem; opacity:.88; margin-top:5px; letter-spacing:.3px; }
  .metric-sub   { font-size:0.68rem; opacity:.65; margin-top:3px; }

  /* ── Section headers ── */
  .section-header {
    background:linear-gradient(90deg,#1e3a5f,#2e6da4);
    color:#fff; padding:7px 16px; border-radius:6px;
    font-size:1rem; font-weight:700; margin:14px 0 8px 0;
    letter-spacing:.2px;
  }
  .section-subheader {
    color:#1e3a5f; font-size:.95rem; font-weight:600;
    border-bottom:2px solid #2e6da4; padding-bottom:4px; margin:10px 0 6px;
  }

  /* ── Info cards ── */
  .signal-card {
    border-left:4px solid #2e6da4; background:#eef5ff;
    padding:9px 14px; border-radius:4px; margin:5px 0; line-height:1.5;
  }
  .warning-card {
    border-left:4px solid #e05c2a; background:#fff3ee;
    padding:9px 14px; border-radius:4px; margin:5px 0; line-height:1.5;
  }
  .success-card {
    border-left:4px solid #3db07a; background:#edfaf3;
    padding:9px 14px; border-radius:4px; margin:5px 0; line-height:1.5;
  }
  .critical-card {
    border-left:4px solid #c62828; background:#ffeaea;
    padding:9px 14px; border-radius:4px; margin:5px 0; line-height:1.5;
  }
  .validated-card {
    border-left:4px solid #3db07a; background:#edfaf3;
    padding:9px 14px; border-radius:4px; margin:5px 0; line-height:1.5;
  }
  .unverified-card {
    border-left:4px solid #f0a030; background:#fffbeb;
    padding:9px 14px; border-radius:4px; margin:5px 0; line-height:1.5;
  }
  .conf-high  { color:#166534; font-weight:700; }
  .conf-med   { color:#92400e; font-weight:700; }
  .conf-low   { color:#c62828; font-weight:700; }

  /* ── Priority badge ── */
  .badge-critical { background:#c62828; color:#fff; border-radius:4px; padding:2px 7px; font-size:.75rem; font-weight:700; }
  .badge-high     { background:#e05c2a; color:#fff; border-radius:4px; padding:2px 7px; font-size:.75rem; font-weight:700; }
  .badge-medium   { background:#f0a030; color:#fff; border-radius:4px; padding:2px 7px; font-size:.75rem; font-weight:700; }

  /* ── Tab strip ── */
  [data-testid="stTabs"] > div:first-child { gap:4px; }

  /* ── Tables ── */
  [data-testid="stDataFrame"] thead th { background:#1e3a5f !important; color:#fff !important; }
</style>
""", unsafe_allow_html=True)

# ── Header ──────────────────────────────────────────────────────
# ── Header ──────────────────────────────────────────────────────
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.title("🧬 Global Naive MSC Exosome Market")
    st.caption(
        f"Strategic intelligence: addressable market · COGS · pricing · regulation · entry points  "
        f"**|**  Bone Marrow MSC Source  **|**  {REPORT_DATE}  **|**  {DATA_VERSION}"
    )
with col_h2:
    # ── Live data status bar ──────────────────────────────────
    all_live = all(df is not None for df in [live_signals, live_distributors, live_regulatory, live_pricing])
    status_color  = "#3db07a" if all_live else "#f0a030"
    status_label  = "🟢 Live data" if all_live else "🟡 Partial data"
    total_signals = len(live_signals) if live_signals is not None else 0
    st.markdown(
        f"""<div style="text-align:right;padding-top:8px;">
        <span style="background:#1e3a5f;color:#7ec8e3;padding:4px 10px;border-radius:6px;font-size:.8rem;">
        🗓 Last updated: {REPORT_DATE}</span><br><br>
        <span style="background:{status_color};color:#fff;padding:4px 10px;border-radius:6px;font-size:.8rem;font-weight:600;">
        {status_label} · {total_signals} signals · auto-updated: {last_run}</span>
        </div>""",
        unsafe_allow_html=True,
    )
    if st.button("🔄 Refresh data"):
        st.cache_data.clear()
        st.rerun()

st.markdown("---")

# ── Critical finding banner ──────────────────────────────────────
st.markdown(
    '<div class="critical-card">⚠️ <strong>CRITICAL FINDING:</strong> No exosome-based therapeutic has received '
    "regulatory approval anywhere in the world as of March 2026. The addressable market today is overwhelmingly the "
    "<strong>wellness, aesthetics &amp; cosmeceutical channel ($81M → 35.9% CAGR)</strong>, with secondary opportunity "
    "in soft indications (wound healing, ortho pain) via physician-dispensed channels in permissive jurisdictions "
    "(Mexico, UAE, Thailand, SEA).</div>",
    unsafe_allow_html=True,
)
st.markdown("")

# ══════════════════════════════════════════════════════════════
# TABS
# ══════════════════════════════════════════════════════════════
tabs = st.tabs([
    "📊 Market Overview",
    "🗺️ Geographic Analysis",
    "🏢 Distributors & Entry Points",
    "⚖️ Regulation",
    "💰 Pricing & COGS",
    "📡 Signals & Trends",
    "✅ Strategy Checklist",
])

# ════════════════════════════════════════════════════════════════
# TAB 1 — MARKET OVERVIEW
# ════════════════════════════════════════════════════════════════
with tabs[0]:
    # ── KPI row ─────────────────────────────────────────────────
    st.markdown('<div class="section-header">Global Market KPIs (Addressable Wellness + Soft Indications)</div>', unsafe_allow_html=True)

    kpis = [
        ("~$88.5M", "2024 Addressable Market", "Wellness + soft indications only"),
        ("~$494M",  "2030 Forecast",            "Wellness + soft indications"),
        ("~33%",    "CAGR 2024–2030",           "Addressable segment"),
        ("~$2,500", "BM-MSC COGS / Dose (2026)","10B-particle dose midpoint"),
        ("35.9%",   "Regen Aesthetics CAGR",    "Precedence Research 2025"),
        ("$81M",    "Regen Aesthetics (2024)",  "Primary commercial segment"),
    ]
    cols = st.columns(6)
    for col, (val, label, sub) in zip(cols, kpis):
        col.markdown(
            f'<div class="metric-card">'
            f'<div class="metric-value">{val}</div>'
            f'<div class="metric-label">{label}</div>'
            f'<div class="metric-sub">{sub}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown("")

    # ── Segment table + pie ──────────────────────────────────────
    col_a, col_b = st.columns([1, 1])

    with col_a:
        st.markdown('<div class="section-header">Market Valuation Reconciliation — Why Numbers Range $177M to $58B</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="validated-card">✅ These figures are <strong>not contradictory</strong> — they measure fundamentally different things. '
            "A manufacturer of BM-MSC exosome <em>products</em> operates in the <strong>$81–177M B2B product market</strong>. "
            "The $58B figure includes hospital labor, capital equipment, and all procedure fees — "
            "the economic activity of which exosome vials are a tiny input cost.</div>",
            unsafe_allow_html=True,
        )
        st.markdown("")

        recon_df = pd.DataFrame([
            {"Research Firm":"Grand View Research",     "Segment":"Total Exosomes (B2B products)",          "2024/25 Value":"$177.4M", "2030/35 Forecast":"$794.2M (2030)",   "What's Included":"B2B kits, reagents, isolation services",                       "Relevant to Manufacturer?":"✅ YES — core market"},
            {"Research Firm":"InsightAce Analytic",     "Segment":"Regen Aesthetics Exosomes",              "2024/25 Value":"$81.1M",  "2030/35 Forecast":"$1.69B (2034)",    "What's Included":"Aesthetic exosome products specifically",                       "Relevant to Manufacturer?":"✅ YES — PRIMARY"},
            {"Research Firm":"DelveInsight",            "Segment":"Exosome Diagnostics (IVD)",              "2024/25 Value":"$119.3M", "2030/35 Forecast":"$2.56B (2032)",    "What's Included":"In-vitro diagnostic tests only (ExoDx Prostate etc.)",         "Relevant to Manufacturer?":"⚠️ Partial — separate channel"},
            {"Research Firm":"Transparency Market Res.","Segment":"Cosmetic Applications (broad)",          "2024/25 Value":"$1.8B",   "2030/35 Forecast":"$26.6B (2035)",    "What's Included":"Retail cosmeceuticals, formulations, broader cosmetic use",    "Relevant to Manufacturer?":"⚠️ Partial — broader scope"},
            {"Research Firm":"Statifacts",              "Segment":"U.S. Exosome-Based Therapy",             "2024/25 Value":"$15.6M",  "2030/35 Forecast":"$79.7M (2034)",    "What's Included":"U.S.-specific therapeutic service revenues only",               "Relevant to Manufacturer?":"⚠️ US only; service revenue"},
            {"Research Firm":"Precedence Research",     "Segment":"Exosome Therapy (full sector)",          "2024/25 Value":"$58.12B", "2030/35 Forecast":"$307.04B (2035)",  "What's Included":"Hospital labor + procedure fees + capital equipment included",  "Relevant to Manufacturer?":"❌ NOT product B2B — service sector"},
        ])
        st.dataframe(recon_df, hide_index=True, use_container_width=True)
        st.markdown("")

        # ── Reconciliation waterfall chart ────────────────────────
        recon_chart = pd.DataFrame({
            "Scope":  ["Regen Aesthetics\n(InsightAce)", "Total Exosome B2B\n(Grand View)", "Diagnostics\n(DelveInsight)", "Cosmetic Apps\n(TMR, broad)", "Exosome Therapy\n(Precedence, incl. fees)"],
            "Value":  [81.1, 177.4, 119.3, 1800, 58120],
            "Type":   ["Primary target","B2B product","Diagnostics","Broader cosmetic","Service sector total"],
        })
        fig_recon = px.bar(
            recon_chart, x="Scope", y="Value",
            color="Type",
            color_discrete_map={
                "Primary target":    "#1e3a5f",
                "B2B product":       "#2e6da4",
                "Diagnostics":       "#7ec8e3",
                "Broader cosmetic":  "#f0a030",
                "Service sector total":"#e05c2a",
            },
            text="Value",
            log_y=True,
            title="Market Valuations by Research Firm — Log Scale (note: these measure different things)",
        )
        fig_recon.update_traces(texttemplate="%{text:,.0f}M", textposition="outside")
        fig_recon.update_layout(
            height=360, margin=dict(t=50,b=10), showlegend=True,
            yaxis_title="USD Million (log scale)", xaxis_title="",
            legend=dict(orientation="h", yanchor="bottom", y=1.01, font=dict(size=9)),
        )
        st.plotly_chart(fig_recon, use_container_width=True)
        st.caption("Log scale used because values span $81M to $58,000M. Each bar measures a different economic concept — they are not alternative estimates of the same thing.")

        st.markdown('<div class="section-header">Addressable Market by Region (2024)</div>', unsafe_allow_html=True)
        st.caption("Source: InsightAce Analytic Nov 2025 (global base); Credence Research 2025 (regional shares); FMI 2024 (APAC); author estimates for sub-regions.")
        addr_df = pd.DataFrame({
            "Region":    ["North America", "Europe (W)", "Rest of APAC*", "Southeast Asia", "CEE (PL/RO/CZ)", "Latin America", "UAE/GCC", "Thailand", "Australia", "Rest of World"],
            "2024 ($M)": [35,   15,   13.5, 7,    3,    5,    5,    3,    2,    1.5],
            "2030 ($M)": [195,  68,   88,   47,   15,   24,   28,   20,   9,    8],
            "CAGR":      ["33%","28%","37%","37%","32%","30%","33%","37%","28%","33%"],
            "Source":    [
                "InsightAce leading region; Credence 45% share; FL medspa $1.2B",
                "Credence 20%; Dataintelo 25%; market.us data",
                "FMI: China 23.1% CAGR, Korea ExoCoBio 9.6% share",
                "ASEAN pathway; PH FDA Jan 2026",
                "Romania $300.9M cosmetic surgery; Poland $4.8M est.; CEE CAGR 10.1%",
                "Credence: LATAM = 4.5% of total; ANVISA-COFEPRIS MoU Aug 2025",
                "GloGrowthInsights MEA ~12%; UAE subset",
                "Medical tourism; Thai FDA modernising",
                "TGA-restricted; regenerative protocols",
                "Emerging adoption",
            ],
        })
        # Note: Rest of APAC includes Korea, Japan, China (not separately tracked in dashboard)
        fig_addr = px.bar(
            addr_df, x="Region", y=["2024 ($M)", "2030 ($M)"],
            barmode="group",
            color_discrete_sequence=["#2e6da4", "#7ec8e3"],
            title="Addressable Market: 2024 vs 2030 Forecast by Region ($M)",
            text_auto=".1f",
        )
        fig_addr.update_layout(height=340, margin=dict(t=50, b=10), legend_title="Year",
                                xaxis_tickangle=-35, yaxis_title="USD Million")
        st.plotly_chart(fig_addr, use_container_width=True)
        st.caption("*Rest of APAC includes South Korea (ExoCoBio ~9.6% global share), Japan, and China (23.1% CAGR per FMI)")

    with col_b:
        st.markdown('<div class="section-header">Regional Share — Addressable Market 2024</div>', unsafe_allow_html=True)
        pie_df = addr_df.copy()
        fig_pie = px.pie(
            pie_df, names="Region", values="2024 ($M)",
            color_discrete_sequence=["#1e3a5f","#2e6da4","#4a90d9","#6aabdf","#7ec8e3","#a8d5e8","#b3dff0","#e05c2a","#f0a07a","#ffd8c0"],
            hole=0.45,
        )
        fig_pie.update_traces(textposition="outside", textinfo="percent+label")
        fig_pie.update_layout(margin=dict(t=10, b=80), showlegend=False, height=380)
        st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown('<div class="section-header">CAGR by Region</div>', unsafe_allow_html=True)
        cagr_df = addr_df.copy()
        cagr_df["CAGR_num"] = [33, 28, 37, 37, 32, 30, 33, 37, 28, 33]
        cagr_df_sorted = cagr_df.sort_values("CAGR_num", ascending=True)
        fig_cagr = px.bar(
            cagr_df_sorted, x="CAGR_num", y="Region", orientation="h",
            color="CAGR_num",
            color_continuous_scale=["#b3dff0", "#1e3a5f"],
            text="CAGR",
        )
        fig_cagr.update_traces(textposition="outside")
        fig_cagr.update_layout(
            height=320, margin=dict(t=10, b=10),
            coloraxis_showscale=False,
            xaxis_title="CAGR (%)", yaxis_title="",
        )
        st.plotly_chart(fig_cagr, use_container_width=True)

    # ── Tab 1 Sources ────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">Market Overview — Data Sources</div>', unsafe_allow_html=True)
    sources_tab1 = [
        ("InsightAce Analytic", "Regenerative Aesthetics Exosome Products Market, Nov 2025", "$81.1M global base; 35.9% CAGR 2025–2034; North America as leading region"),
        ("Grand View Research", "Exosomes Market Size and Share — Industry Report 2030, 2024", "$177.4M total exosome market (2024); $794.2M forecast (2030); B2B kits/reagents/isolation"),
        ("Precedence Research", "Exosome Therapeutics Market Size 2025–2034, Nov 2025", "$58.12B Exosome Therapy sector (2025) including procedure fees and hospital labor"),
        ("DelveInsight", "Exosome Diagnostics Market Insights and Forecast 2034, 2025", "$119.3M diagnostics (2024); $2.56B (2032); IVD channel only"),
        ("Transparency Market Research", "Exosome Market for Cosmetic Applications, 2024", "$1.8B cosmetic applications (2024); $26.6B (2035); includes retail cosmeceuticals"),
        ("Statifacts / Precedence Research", "U.S. Exosome-Based Therapy Market, 2025", "$15.61M U.S.-specific therapeutic service revenues (2024); $79.67M (2034)"),
        ("Credence Research", "Exosomes Skincare Market Size, Share and Growth Report 2032", "Regional shares: NA 45%, APAC 25%, Europe 20%, LATAM $18.67M of $418M total"),
        ("Coherent Market Insights", "Exosomes Skincare Market Size, Share, Trends & Forecast 2032", "NA ~40% share; APAC ~32% in 2025; fastest-growing region confirmation"),
        ("Future Market Insights", "Exosome-Based Skincare Market, 2024", "China 23.1% CAGR; India 21.8% CAGR; Korea ExoCoBio ~9.6% global share"),
        ("Astute Analytica", "Exosome Therapy Market Size, Growth — Trends Analysis 2035", "COGS trajectory benchmark: $5,000 (2023) → $2,500 (2026) → $500 (2030) midpoints"),
        ("RoosterBio / Corning", "Exosome Production Bioreactor Kits; Expert Roundtable Feb 2025", "BM-MSC COGS component benchmarks; hollow-fiber bioreactor cost reductions"),
        ("Strategic Reconciliation Report", "BM-MSC Sector Analysis, March 2026", "COGS per 10B particles: 2023 $3,100–4,900; 2026 $1,950–3,150; 2030 $690–1,050"),
    ]
    col_s1, col_s2 = st.columns(2)
    for i, (firm, title, detail) in enumerate(sources_tab1):
        col = col_s1 if i % 2 == 0 else col_s2
        col.markdown(
            f'<div class="signal-card" style="margin:3px 0;padding:6px 10px;">'
            f'<strong>{firm}</strong> — <em>{title}</em><br>'
            f'<span style="font-size:.82rem;color:#444;">{detail}</span></div>',
            unsafe_allow_html=True,
        )
# ════════════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown('<div class="section-header">Market Opportunity vs Regulatory Risk (All Regions)</div>', unsafe_allow_html=True)
    st.markdown("")

    geo_df = pd.DataFrame([
        {"Region":"North America", "Stage":"Restricted",    "Segment":"Cosmetic / Research",  "Reg Risk":"High",   "CAGR":33,"OOP":False,"2024 ($M)":35,  "2030 ($M)":195, "Note":"Largest market — cosmetic channel only; FL medspa $1.2B; Nevada SB128/AB148"},
        {"Region":"Europe (W)",    "Stage":"Established",   "Segment":"Aesthetic/Wellness",   "Reg Risk":"Medium", "CAGR":28,"OOP":True, "2024 ($M)":15,  "2030 ($M)":68,  "Note":"Credence 20% share; Germany, France, Italy lead"},
        {"Region":"CEE",           "Stage":"Emerging",      "Segment":"Medical Tourism Hub",  "Reg Risk":"Low",    "CAGR":32,"OOP":True, "2024 ($M)":3,   "2030 ($M)":15,  "Note":"Romania $300.9M cosmetic surgery; Poland $4.8M; Prague sessions ~$320"},
        {"Region":"Rest of APAC",  "Stage":"Emerging",      "Segment":"K-Beauty/Hospital",    "Reg Risk":"Medium", "CAGR":37,"OOP":True, "2024 ($M)":13.5,"2030 ($M)":88,  "Note":"Korea ExoCoBio 9.6% share; China 23.1% CAGR (FMI)"},
        {"Region":"Southeast Asia","Stage":"Emerging",      "Segment":"K-Beauty/Aesthetic",   "Reg Risk":"Low",    "CAGR":37,"OOP":True, "2024 ($M)":7,   "2030 ($M)":47,  "Note":"ASEAN gateway; PH FDA Jan 2026 approved"},
        {"Region":"Latin America", "Stage":"Growing",       "Segment":"Medical Tourism",      "Reg Risk":"Medium", "CAGR":30,"OOP":True, "2024 ($M)":5,   "2030 ($M)":24,  "Note":"Credence: LATAM = 4.5% of total; ANVISA-COFEPRIS MoU Aug 2025"},
        {"Region":"UAE/GCC",       "Stage":"Niche/Premium", "Segment":"Longevity/Luxury",     "Reg Risk":"Low-Med","CAGR":33,"OOP":True, "2024 ($M)":5,   "2030 ($M)":28,  "Note":"Premium subset of MEA; luxury longevity channel"},
        {"Region":"Thailand",      "Stage":"Emerging",      "Segment":"Medical Tourism",      "Reg Risk":"Low-Med","CAGR":37,"OOP":True, "2024 ($M)":3,   "2030 ($M)":20,  "Note":"Medical tourism hub; Thai FDA modernising 2025"},
        {"Region":"Australia",     "Stage":"Established",   "Segment":"Medical Regen",        "Reg Risk":"High",   "CAGR":28,"OOP":False,"2024 ($M)":2,   "2030 ($M)":9,   "Note":"TGA-restricted; regenerative protocols only"},
    ])

    risk_order = {"Low":1,"Low-Med":2,"Medium":3,"High":4}
    geo_df["Risk Num"] = geo_df["Reg Risk"].map(risk_order)

    fig_bubble = px.scatter(
        geo_df, x="CAGR", y="Reg Risk",
        size="2030 ($M)",
        color="Stage",
        text="Region",
        hover_data={"2024 ($M)":True,"2030 ($M)":True,"Segment":True,"Reg Risk":True,"CAGR":True,"Note":True},
        color_discrete_sequence=["#1e3a5f","#2e6da4","#4a90d9","#7ec8e3","#e05c2a","#f0a07a","#c62828"],
        size_max=70,
        title="Bubble size = 2030 market forecast ($M) — North America largest market, most restricted channel",
    )
    fig_bubble.update_traces(textposition="top center")
    fig_bubble.update_layout(
        height=480, xaxis_title="Estimated CAGR (%)", yaxis_title="Regulatory Barrier",
        yaxis=dict(categoryorder="array", categoryarray=["High","Medium","Low-Med","Low"]),
        margin=dict(t=50, b=20),
    )
    st.plotly_chart(fig_bubble, use_container_width=True)
    st.caption("⚠️ Note: North America is the largest market by size but most restricted by regulation. Best accessible entry points remain SEA, LATAM, UAE, and Thailand.")

    # ── Country detail tables ────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">Europe — Country Detail</div>', unsafe_allow_html=True)
        eur_df = pd.DataFrame([
            {"Country":"Germany",    "Maturity":"High",   "Key Segment":"Clinical Aesthetic",  "Barrier":"Medium", "Distributor":"Jolifill / Croma-Pharma"},
            {"Country":"France",     "Maturity":"High",   "Key Segment":"Medical Spa",         "Barrier":"Medium", "Distributor":"Teoxane France"},
            {"Country":"Switzerland","Maturity":"Medium", "Key Segment":"Longevity Clinics",   "Barrier":"High",   "Distributor":"Swissmedic partners"},
            {"Country":"Austria",    "Maturity":"Medium", "Key Segment":"Aesthetic Devices",   "Barrier":"Medium", "Distributor":"Croma-Pharma DACH"},
            {"Country":"Italy",      "Maturity":"Medium", "Key Segment":"Specialist Networks", "Barrier":"Medium", "Distributor":"Taumedika S.r.l."},
            {"Country":"Poland/CEE", "Maturity":"Low",    "Key Segment":"Emerging Aesthetics", "Barrier":"Low",    "Distributor":"Teoxane Polska"},
            {"Country":"South Korea","Maturity":"High",   "Key Segment":"K-beauty / Hospital", "Barrier":"Medium", "Distributor":"ExoCoBio, ASCE+"},
        ])
        st.dataframe(eur_df, hide_index=True, use_container_width=True)

        st.markdown('<div class="section-header">🇺🇸 US State-Permissive Markets — Florida & Nevada Detail</div>', unsafe_allow_html=True)
        us_state_df = pd.DataFrame([
            {"State":"Florida",                   "Market":"Medspa (statewide 2024)","Size":"$1.2B","2034 Forecast":"$2.5B","CAGR":"7.8%",   "Key Legislation":"FL Statute §456.47 — informed consent; structured elective pathway"},
            {"State":"Florida — South FL cluster","Market":"Miami-Dade/Broward/Palm Beach medspa","Size":"$199.5M","2033 Forecast":"$1.09B","CAGR":"20.69%","Key Legislation":"Same §456.47; highest concentration of exosome-ready medspas"},
            {"State":"Nevada",                    "Market":"Anti-aging / performance protocols","Size":"Emerging hub","2034 Forecast":"High growth","CAGR":"est. 15%+","Key Legislation":"SB128 + AB148 — licensed physicians may perform non-FDA-approved cell therapies"},
        ])
        st.dataframe(us_state_df, hide_index=True, use_container_width=True)

        col_fl1, col_fl2 = st.columns(2)
        with col_fl1:
            st.markdown(
                '<div class="success-card">🌴 <strong>Florida §456.47 — Why it matters:</strong><br>'
                "This statute requires physicians to obtain informed consent advising patients that exosome products are not FDA-approved — "
                "but critically, it <em>creates</em> a structured, state-monitored pathway for elective clinical use. "
                "It does not prohibit use; it regulates it. "
                "South Florida's 20.69% CAGR medspa market is the most actionable US sub-market for a new supplier today. "
                "Entry strategy: position as post-procedure recovery topical to capture the $1.2B Florida medspa channel while maintaining federal compliance.</div>",
                unsafe_allow_html=True,
            )
        with col_fl2:
            st.markdown(
                '<div class="success-card">🎰 <strong>Nevada SB128 + AB148 — Why it matters:</strong><br>'
                "Nevada (along with Florida and Utah) has passed state regulations allowing licensed physicians to perform "
                "certain cell-derived therapies not approved by the FDA. "
                "Las Vegas has established itself as a destination hub for exosome anti-aging and performance protocols. "
                "Average single session: <strong>$4,900 in Miami/Las Vegas</strong>; comprehensive plans up to <strong>$15,000</strong>. "
                "Entry strategy: direct-to-clinic premium positioning; performance and longevity angle; no therapeutic claims on labeling.</div>",
                unsafe_allow_html=True,
            )

    with col2:
        st.markdown('<div class="section-header">Asia-Pacific, LATAM & ME Detail</div>', unsafe_allow_html=True)
        apac_df = pd.DataFrame([
            {"Territory":"Philippines", "Region":"SEA",   "Maturity":"Emerging", "Note":"ASEAN gateway — PH FDA notif. Jan 2026"},
            {"Territory":"Malaysia",    "Region":"SEA",   "Maturity":"Medium",   "Note":"16.2% research CAGR; cGMP active"},
            {"Territory":"Thailand",    "Region":"SEA",   "Maturity":"Emerging", "Note":"Medical tourism hub; Thai FDA modernising 2025"},
            {"Territory":"Indonesia",   "Region":"SEA",   "Maturity":"Early",    "Note":"Clinic training pathway; BPOM engaged"},
            {"Territory":"Singapore",   "Region":"SEA",   "Maturity":"Medium",   "Note":"HSA approval = ASEAN reliance gateway"},
            {"Territory":"Brazil",      "Region":"LATAM", "Maturity":"High",     "Note":"2nd-largest aesthetic market globally"},
            {"Territory":"Mexico",      "Region":"LATAM", "Maturity":"High",     "Note":"Medical tourism; COFEPRIS-ANVISA MoU"},
            {"Territory":"UAE/GCC",     "Region":"ME",    "Maturity":"Premium",  "Note":"Luxury longevity; DUBIMED 40yr network"},
        ])
        st.dataframe(apac_df, hide_index=True, use_container_width=True)

        st.markdown('<div class="section-header">Australia Detail</div>', unsafe_allow_html=True)
        st.markdown('<div class="warning-card">🇦🇺 <strong>Australia (TGA):</strong> High regulatory barrier — TGA-registered clinics only; PBAC risk-sharing model for ATMPs. Entry via Biogenix-style TGA-compliant partnership. Market ~$2M (2024), restricted channel.</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-header">🆕 Central & Eastern Europe (CEE) — Emerging Hub</div>', unsafe_allow_html=True)
        cee_df = pd.DataFrame([
            {"Country":"Romania",        "Market Size (2024)":"$300.9M cosmetic surgery", "2032 Forecast":"$589.7M", "CAGR":"~8%",   "Key Driver":"High demand corrective treatments; medical tourism from W. Europe","Session Price":"~$400–800"},
            {"Country":"Poland",         "Market Size (2024)":"$4.8M est. (aesthetic med)","2030 Forecast":"$14.5M", "CAGR":"~20%",  "Key Driver":"Regional distribution hub; LaserMe + ASCE+ protocol active","Session Price":"~$500 (2,000 PLN)"},
            {"Country":"Czech Republic", "Market Size (2024)":"$2.1M est. (bioregen)",    "2033 Forecast":"$6.8M",  "CAGR":"~16%",  "Key Driver":"Clinical expansion in Prague; tech-forward clinic network","Session Price":"~$320 (7,500 CZK)"},
        ])
        st.dataframe(cee_df, hide_index=True, use_container_width=True)
        st.markdown(
            '<div class="signal-card">🌍 <strong>CEE Strategic Value:</strong> Exosome injectables are the fastest-growing '
            "segment in the European bioregenerative aesthetic market through 2033 (CAGR 10.1%). "
            "CEE session prices ($320–800) vs US ($4,900 average in Miami/Las Vegas) make CEE a high-volume, "
            "lower-margin channel — ideal for driving distributor stocking and brand establishment before entering W. Europe at premium pricing. "
            "Target distributors: Teoxane Polska (Poland/CEE) already active in EPICEXOSOME distribution.</div>",
            unsafe_allow_html=True,
        )

        st.markdown('<div class="section-header">End User Profiles</div>', unsafe_allow_html=True)
        eu_df = pd.DataFrame([
            {"Region":"Europe",        "Primary User":"Dermatologists / Med Spas",    "Application":"Post-procedure recovery"},
            {"Region":"Latin America", "Primary User":"Medical Tourism Clinics",      "Application":"Aesthetic + ortho"},
            {"Region":"SEA",           "Primary User":"Aesthetic / K-beauty Clinics", "Application":"Skin rejuvenation"},
            {"Region":"UAE/GCC",       "Primary User":"Luxury Longevity Clinics",     "Application":"Systemic IV longevity"},
            {"Region":"Thailand",      "Primary User":"Med Spas / Private Hospitals", "Application":"Anti-aging + IV drip"},
            {"Region":"USA",           "Primary User":"Medical Spas / Dermatology",   "Application":"Cosmetic topical / hair"},
            {"Region":"Australia",     "Primary User":"TGA-registered Clinics",       "Application":"Medical regenerative"},
        ])
        st.dataframe(eu_df, hide_index=True, use_container_width=True)

    # ── Tab 2 Sources ────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">Geographic Analysis — Data Sources</div>', unsafe_allow_html=True)
    sources_tab2 = [
        ("InsightAce Analytic", "Nov 2025 (multiple press releases)", "North America confirmed as leading region for regen aesthetics exosomes"),
        ("Credence Research", "Exosomes Skincare Market Size, Share and Growth Report 2032", "NA 45% share; APAC 25%; Europe 20%; LATAM $18.67M of $418M = 4.5%"),
        ("Coherent Market Insights", "Exosomes Skincare Market 2032", "NA ~40%; APAC ~32%; fastest-growing region"),
        ("Future Market Insights", "Exosome-Based Skincare Market 2024", "China 23.1% CAGR; India 21.8% CAGR; Korea ExoCoBio 9.6% global share"),
        ("Global Growth Insights", "Exosomes Skincare Market 2025", "APAC 39%; NA 26%; Europe 23%; MEA 12%"),
        ("Dataintelo", "Exosomes Skincare Market Size, Share, Trends & Forecast 2025–2033", "NA 35% (2023); APAC fastest-growing at 11.2% CAGR"),
        ("Strategic Reconciliation Report", "BM-MSC Sector Analysis, March 2026", "CEE market data: Romania $300.9M cosmetic surgery → $589.7M (2032); Poland $4.8M → $14.5M (2030); Czech Republic $2.1M → $6.8M (2033); CEE CAGR 10.1%"),
        ("Florida Statute §456.47", "State of Florida Legislature", "Structured informed consent pathway for elective physician use of non-FDA-approved exosome products"),
        ("Nevada SB128 + AB148", "State of Nevada Legislature", "Licensed physicians may perform non-FDA-approved cell-derived therapies"),
        ("Florida Medical Spa Market Data", "Industry analysis 2024", "Statewide $1.2B (2024) → $2.5B (2034) at 7.8% CAGR; South FL $199.5M → $1.09B (2033) at 20.69% CAGR"),
        ("NutraIngredients / ClinRegs", "Jan 2025; Aug 2025", "Thai FDA modernisation; new health product import/export policies"),
        ("HSA Singapore", "ASEAN Cosmetic Directive guidance", "Thai FDA HSA Reliance Route (2021); ASEAN harmonization framework"),
    ]
    col_g1, col_g2 = st.columns(2)
    for i, (firm, title, detail) in enumerate(sources_tab2):
        col = col_g1 if i % 2 == 0 else col_g2
        col.markdown(
            f'<div class="signal-card" style="margin:3px 0;padding:6px 10px;">'
            f'<strong>{firm}</strong> — <em>{title}</em><br>'
            f'<span style="font-size:.82rem;color:#444;">{detail}</span></div>',
            unsafe_allow_html=True,
        )
# ════════════════════════════════════════════════════════════════
# TAB 3 — DISTRIBUTORS & ENTRY POINTS
# ════════════════════════════════════════════════════════════════
with tabs[2]:
    # ── Full distributor table ───────────────────────────────────
    st.markdown('<div class="section-header">Global Distributor Intelligence</div>', unsafe_allow_html=True)

    dist_df_static = pd.DataFrame([
        # Europe
        {"Distributor":"Jolifill",             "Region":"Europe",   "Territory":"Germany",         "Brands":"EXOXE, EXOMIDE, EXOJUV",       "Approach":"Direct e-commerce + professional",     "Priority":"🟢 High",  "Channel":"Aesthetic"},
        {"Distributor":"Croma-Pharma",         "Region":"Europe",   "Territory":"Austria/DACH",    "Brands":"Aesthetic Mgmt Partners",      "Approach":"Strategic regional partnerships",      "Priority":"🟢 High",  "Channel":"Aesthetic"},
        {"Distributor":"Teoxane France",       "Region":"Europe",   "Territory":"France",          "Brands":"Teoxane proprietary",          "Approach":"Direct subsidiary model",             "Priority":"🟡 Medium","Channel":"Aesthetic"},
        {"Distributor":"Taumedika S.r.l.",     "Region":"Europe",   "Territory":"Italy",           "Brands":"Karisma Exo Care",             "Approach":"Specialist aesthetic networks",        "Priority":"🟡 Medium","Channel":"Aesthetic"},
        {"Distributor":"Teoxane Polska",       "Region":"CEE",      "Territory":"Poland/CEE",      "Brands":"EPICEXOSOME",                  "Approach":"Emerging market expansion; LaserMe+ASCE+ protocol", "Priority":"🟢 High",  "Channel":"Aesthetic"},
        {"Distributor":"LaserMe Clinics",      "Region":"CEE",      "Territory":"Poland",          "Brands":"ASCE+ / multi-brand",          "Approach":"High-volume clinic chain; ~500 USD/session","Priority":"🟢 High", "Channel":"Aesthetic"},
        {"Distributor":"Prague Bioregen network","Region":"CEE",    "Territory":"Czech Republic",  "Brands":"Local + EU brands",            "Approach":"Clinical expansion; ~320 USD/session",  "Priority":"🟡 Medium","Channel":"Medical/Aesthetic"},
        {"Distributor":"Romanian aesthetic distributors","Region":"CEE","Territory":"Romania",     "Brands":"EU aesthetic brands",          "Approach":"$300.9M cosmetic surgery market; W.EU medical tourism inflow","Priority":"🟢 High","Channel":"Aesthetic"},
        # LATAM
        {"Distributor":"Giostar Mexico",       "Region":"LATAM",    "Territory":"Mexico (Cancun)", "Brands":"Multiple MSC brands",          "Approach":"Medical tourism + ortho",             "Priority":"🟢 High",  "Channel":"Medical/Ortho"},
        {"Distributor":"PRMEDICA",             "Region":"LATAM",    "Territory":"Mexico (Cabos)",  "Brands":"MSC exosomes",                 "Approach":"Inflammatory modulation",             "Priority":"🟡 Medium","Channel":"Medical"},
        {"Distributor":"R3 Stem Cell Brazil",  "Region":"LATAM",    "Territory":"Brazil",          "Brands":"R3 proprietary",               "Approach":"Centers of Excellence",               "Priority":"🟢 High",  "Channel":"Medical/Aesthetic"},
        # SEA
        {"Distributor":"Vanguard Aesthetics",  "Region":"SEA",      "Territory":"Philippines",     "Brands":"Innovative med-aesthetic",     "Approach":"ASEAN hub strategy",                  "Priority":"🟢 High",  "Channel":"Aesthetic"},
        {"Distributor":"MGRC / GGA Malaysia",  "Region":"SEA",      "Territory":"Malaysia",        "Brands":"cGMP MSC exosomes",            "Approach":"Research + diagnostics",              "Priority":"🟡 Medium","Channel":"Research"},
        {"Distributor":"PT. Sel Regenerasi",   "Region":"SEA",      "Territory":"Indonesia",       "Brands":"Local brands",                 "Approach":"Physician clinic training",           "Priority":"🟡 Medium","Channel":"Medical"},
        # Thailand (new)
        {"Distributor":"Thai Aesthetic Clinics","Region":"Thailand", "Territory":"Bangkok/Phuket", "Brands":"Multi-brand",                  "Approach":"Direct clinic supply via cosmetic notif.","Priority":"🟢 High","Channel":"Aesthetic"},
        {"Distributor":"Bumrungrad/Samitivej",  "Region":"Thailand", "Territory":"Thailand",       "Brands":"Proprietary protocols",        "Approach":"Premium private hospital group",      "Priority":"🟡 Medium","Channel":"Medical"},
        {"Distributor":"Innotech / Mega Life.", "Region":"Thailand", "Territory":"Thailand",       "Brands":"Local pharma distribution",    "Approach":"License + supply agreement",          "Priority":"🟢 High",  "Channel":"Pharma/Import"},
        # Australia
        {"Distributor":"Biogenix / InterMed",  "Region":"Pacific",  "Territory":"Australia",       "Brands":"Cervos KeyPRP, Marrow Cell",   "Approach":"TGA-compliant partnership",           "Priority":"🟡 Medium","Channel":"Medical"},
        # UAE/GCC
        {"Distributor":"DUBIMED",              "Region":"UAE/GCC",  "Territory":"UAE/Qatar/Oman",  "Brands":"Galderma, Mesoestetic",        "Approach":"Exclusive 40yr relationships",         "Priority":"🟢 High",  "Channel":"Aesthetic/Medical"},
        {"Distributor":"Troya Aesthetics",     "Region":"UAE/GCC",  "Territory":"UAE",             "Brands":"Premium regional",             "Approach":"Dermatologist patient care",          "Priority":"🟡 Medium","Channel":"Aesthetic"},
        {"Distributor":"EDEN AESTHETICS",      "Region":"UAE/GCC",  "Territory":"Dubai",           "Brands":"Integrative exosome protocol", "Approach":"High-dose IV longevity",              "Priority":"🟢 High",  "Channel":"Longevity IV"},
        # USA (new)
        {"Distributor":"Regen Suppliers (R3)", "Region":"USA",      "Territory":"USA (national)",  "Brands":"ReBellaXO (UC-MSC)",           "Approach":"Position BM-MSC as premium ortho-grade","Priority":"🟢 High", "Channel":"Medical/Aesthetic"},
        {"Distributor":"Elevai Labs / BENEV",  "Region":"USA",      "Territory":"USA",             "Brands":"Elevai E30, ExoCoBio",         "Approach":"OEM/white-label cosmetic topical",    "Priority":"🟢 High",  "Channel":"Aesthetic"},
        {"Distributor":"Medical Spa chains",   "Region":"USA",      "Territory":"USA (TX,FL,AZ)",  "Brands":"Post-procedure adjuncts",      "Approach":"Direct clinic supply — cosmetic only","Priority":"🟡 Medium","Channel":"Aesthetic"},
        {"Distributor":"US CDMO channel",      "Region":"USA",      "Territory":"USA",             "Brands":"Biotech/pharma clinical",      "Approach":"GMP supply for Phase I/II trials",   "Priority":"🟡 Medium","Channel":"Research/CDMO"},
    ])
    dist_df, dist_is_live = get_live_or_static(live_distributors, dist_df_static)
    # Ensure expected columns exist when reading from CSV
    for col in ["Distributor","Region","Territory","Brands","Approach","Priority","Channel"]:
        if col.lower() in dist_df.columns and col not in dist_df.columns:
            dist_df = dist_df.rename(columns={col.lower(): col})
    live_badge(dist_is_live, last_run)

    col_f1, col_f2 = st.columns([1, 3])
    with col_f1:
        region_opts = ["All"] + sorted(dist_df["Region"].unique().tolist())
        region_sel  = st.selectbox("Filter by Region", region_opts)
        channel_opts = ["All"] + sorted(dist_df["Channel"].unique().tolist())
        channel_sel  = st.selectbox("Filter by Channel", channel_opts)
        priority_opts = ["All", "🟢 High", "🟡 Medium"]
        priority_sel  = st.selectbox("Filter by Priority", priority_opts)

    with col_f2:
        filtered = dist_df.copy()
        if region_sel   != "All": filtered = filtered[filtered["Region"]   == region_sel]
        if channel_sel  != "All": filtered = filtered[filtered["Channel"]  == channel_sel]
        if priority_sel != "All": filtered = filtered[filtered["Priority"] == priority_sel]
        st.dataframe(
            filtered[["Distributor","Region","Territory","Brands","Approach","Priority","Channel"]],
            hide_index=True, use_container_width=True, height=320,
        )

    # ── Count chart + approach cards ────────────────────────────
    col_c1, col_c2 = st.columns([1, 1])

    with col_c1:
        st.markdown('<div class="section-header">Distributor Count by Region</div>', unsafe_allow_html=True)
        cnt = dist_df.groupby("Region").size().reset_index(name="Count").sort_values("Count", ascending=True)
        fig_cnt = px.bar(
            cnt, x="Count", y="Region", orientation="h",
            color="Count", color_continuous_scale=["#b3dff0","#1e3a5f"],
            text="Count",
        )
        fig_cnt.update_traces(textposition="outside")
        fig_cnt.update_layout(
            showlegend=False, height=320, margin=dict(t=10, b=10),
            coloraxis_showscale=False, xaxis_title="Number of Key Distributors", yaxis_title="",
        )
        st.plotly_chart(fig_cnt, use_container_width=True)

    with col_c2:
        st.markdown('<div class="section-header">High-Priority Distributor Approach Guide</div>', unsafe_allow_html=True)
        approaches = [
            ("🇦🇪 UAE — DUBIMED", "signal-card",
             "Emphasise clinical credibility + longevity angle. Offer a 'longevity module' fitting their existing "
             "aesthetic infrastructure. 40-yr reputation means they value established brands. Target: 20B-particle "
             "vials priced $175–300/vial B2B."),
            ("🇪🇺 Europe — Croma-Pharma / Jolifill", "signal-card",
             "Focus on premium aesthetic segment. Lead with BM-MSC clinical literature vs. plant-derived competitors. "
             "Croma-Pharma actively seeking new regenerative brands. Target B2B: $140–225/vial (10B particles)."),
            ("🌎 LATAM — Giostar / R3 Stem Cell", "signal-card",
             "Leverage medical tourism + ANVISA-COFEPRIS MoU. Lyophilised format solves cold-chain. Emphasise "
             "CD73/CD90/CD90 markers, CoA, and GMP certification."),
            ("🇹🇭 Thailand — Thai Aesthetic Clinics / Innotech", "success-card",
             "NEW: Use Philippine FDA cosmetic notification as ASEAN compliance proof. Appoint local licensed importer. "
             "Free Sale Certificate required. Thai FDA HSA reliance route (since 2021) can fast-track with Singapore registration. "
             "Target B2B: $90–150/vial (10B particles)."),
            ("🇺🇸 USA — Elevai / Regen Suppliers", "warning-card",
             "CAUTION: US IV channel is high-risk (12+ FDA warning letters). Cosmetic topical / aesthetic channel ONLY. "
             "OEM white-label for medspas and post-laser protocols. No therapeutic claims. GMP documentation essential. "
             "B2B target: $150–275/vial (20B)."),
            ("🌏 SEA — Vanguard Aesthetics (Philippines)", "signal-card",
             "Use Philippines as ASEAN gateway. Jan 2026 PH FDA cosmetic notification validates ASEAN entry blueprint. "
             "B2B target: $75–125/vial (10B particles)."),
        ]
        for title, cls, text in approaches:
            st.markdown(f'<div class="{cls}"><strong>{title}</strong><br>{text}</div>', unsafe_allow_html=True)

    # ── Distributor attractiveness matrix ────────────────────────
    st.markdown('<div class="section-header">Distributor Attractiveness Matrix — Pricing Ceiling Analysis</div>', unsafe_allow_html=True)
    attr_df = pd.DataFrame([
        {"Market":"Germany/EU",    "End-User Price (vial)":"$280–450",  "Max B2B Distributor":"$140–225", "Max Mfr COGS (scale)":"<$80–100",  "Key Pitch":"BM-MSC clinical lit; CD73/CD90 markers; CoA with NTA data"},
        {"Market":"UAE/GCC",       "End-User Price (vial)":"$350–600",  "Max B2B Distributor":"$175–300", "Max Mfr COGS (scale)":"<$100–140", "Key Pitch":"'Longevity module' angle; high-dose IV protocols"},
        {"Market":"Mexico/LATAM",  "End-User Price (vial)":"$200–350",  "Max B2B Distributor":"$100–175", "Max Mfr COGS (scale)":"<$60–90",   "Key Pitch":"Lyophilized format; ANVISA-COFEPRIS MoU compliance"},
        {"Market":"Thailand",      "End-User Price (vial)":"$180–300",  "Max B2B Distributor":"$90–150",  "Max Mfr COGS (scale)":"<$55–80",   "Key Pitch":"Thai FDA cosmetic notification support; ASEAN docs"},
        {"Market":"Philippines/SEA","End-User Price (vial)":"$150–250", "Max B2B Distributor":"$75–125",  "Max Mfr COGS (scale)":"<$50–70",   "Key Pitch":"PH FDA notification gateway; ASEAN cosmetic directive"},
        {"Market":"USA (aesthetic)","End-User Price (vial)":"$300–550", "Max B2B Distributor":"$150–275", "Max Mfr COGS (scale)":"<$90–130",  "Key Pitch":"CoA with CD63/CD81; no therapeutic claims; GMP docs"},
        {"Market":"Australia",     "End-User Price (vial)":"$350–600",  "Max B2B Distributor":"$175–300", "Max Mfr COGS (scale)":"<$100–140", "Key Pitch":"TGA compliance documentation; Biogenix-style model"},
    ])
    st.dataframe(attr_df, hide_index=True, use_container_width=True)

    # ── B2B price waterfall ──────────────────────────────────────
    st.markdown('<div class="section-header">B2B Price Range by Market (per 10B particles)</div>', unsafe_allow_html=True)
    b2b_df = pd.DataFrame({
        "Market":   ["Germany/EU","UAE/GCC","USA","Australia","Mexico/LATAM","Thailand","Philippines/SEA"],
        "Low":      [140, 175, 150, 175, 100, 90, 75],
        "High":     [225, 300, 275, 300, 175, 150, 125],
    })
    b2b_df["Mid"] = (b2b_df["Low"] + b2b_df["High"]) / 2
    b2b_df["Spread"] = b2b_df["High"] - b2b_df["Low"]
    b2b_df = b2b_df.sort_values("Mid", ascending=True)

    fig_b2b = go.Figure()
    fig_b2b.add_trace(go.Bar(
        x=b2b_df["Mid"], y=b2b_df["Market"], orientation="h",
        marker_color="#2e6da4", name="Midpoint B2B",
        error_x=dict(
            type="data",
            symmetric=False,
            array=b2b_df["High"] - b2b_df["Mid"],
            arrayminus=b2b_df["Mid"] - b2b_df["Low"],
            color="#1e3a5f", thickness=2,
        ),
        text=[f"${int(v):,}" for v in b2b_df["Mid"]],
        textposition="outside",
    ))
    fig_b2b.update_layout(
        height=320, margin=dict(t=10, b=10),
        xaxis_title="B2B Price per 10B-particle vial (USD)",
        yaxis_title="", showlegend=False,
    )
    st.plotly_chart(fig_b2b, use_container_width=True)

# ════════════════════════════════════════════════════════════════
# TAB 4 — REGULATION
# ════════════════════════════════════════════════════════════════
with tabs[3]:
    st.markdown('<div class="section-header">Global Regulatory Framework (March 2026)</div>', unsafe_allow_html=True)

    reg_df = pd.DataFrame([
        {"Territory":"USA",         "Body":"FDA",          "Topical/Cosmetic":"Permitted — no claims",       "Soft Indications":"Gray — physician discretion",    "IV/Therapeutic":"IND required — 12+ warning letters","Risk":"🔴 HIGH",    "Conf.":"🟢 80"},
        {"Territory":"EU",          "Body":"EMA",          "Topical/Cosmetic":"CE-IVD compliant",            "Soft Indications":"Cosmetic grade only",             "IV/Therapeutic":"ATMP required — 0 approved",        "Risk":"🔴 HIGH",    "Conf.":"🟢 80"},
        {"Territory":"Australia",   "Body":"TGA",          "Topical/Cosmetic":"Cosmetic — limited claims",   "Soft Indications":"TGA-registered only",             "IV/Therapeutic":"ATMP / PBAC risk-sharing",          "Risk":"🔴 HIGH",    "Conf.":"🟢 70"},
        {"Territory":"Germany",     "Body":"BfArM",        "Topical/Cosmetic":"Cosmetic — active market",    "Soft Indications":"Medical spa channel",             "IV/Therapeutic":"ATMP pathway",                     "Risk":"🟡 MEDIUM",  "Conf.":"🟢 75"},
        {"Territory":"France",      "Body":"ANSM",         "Topical/Cosmetic":"Cosmetic — active",           "Soft Indications":"Dermatology protocols",           "IV/Therapeutic":"ATMP pathway",                     "Risk":"🟡 MEDIUM",  "Conf.":"🟢 75"},
        {"Territory":"Switzerland", "Body":"Swissmedic",   "Topical/Cosmetic":"High-value cosmetic",         "Soft Indications":"Longevity clinics (private)",     "IV/Therapeutic":"Clinical registration",            "Risk":"🟡 MEDIUM",  "Conf.":"🟢 70"},
        {"Territory":"Brazil",      "Body":"ANVISA",       "Topical/Cosmetic":"RDC 949/2024 notification",  "Soft Indications":"IOR required",                    "IV/Therapeutic":"AFE license required",             "Risk":"🟡 MEDIUM",  "Conf.":"🟢 70"},
        {"Territory":"South Korea", "Body":"MFDS",         "Topical/Cosmetic":"K-beauty cosmetic framework","Soft Indications":"Hospital partnerships",           "IV/Therapeutic":"Clinical approval route",          "Risk":"🟡 MEDIUM",  "Conf.":"🟡 60"},
        {"Territory":"UAE",         "Body":"MOHAP/DHA",    "Topical/Cosmetic":"CE/FDA-cert device",         "Soft Indications":"Clinic-based IV protocols — active","IV/Therapeutic":"Strict cosmetic procedure standards","Risk":"🟡 MEDIUM","Conf.":"🟡 65"},
        {"Territory":"Mexico",      "Body":"COFEPRIS",     "Topical/Cosmetic":"Cosmetic compliant",          "Soft Indications":"Physician dispensing — active",   "IV/Therapeutic":"MoU reliance with ANVISA",         "Risk":"🟢 LOW",     "Conf.":"🟢 75"},
        {"Territory":"Thailand",    "Body":"Thai FDA",     "Topical/Cosmetic":"Cosmetic notif. + post-audit","Soft Indications":"Gray — active physician use",     "IV/Therapeutic":"Drug Act B.E. 2510 — no explicit guideline","Risk":"🟡 LOW-MED","Conf.":"🟢 80"},
        {"Territory":"Philippines", "Body":"PH FDA",       "Topical/Cosmetic":"✅ Notif. approved Jan 2026", "Soft Indications":"ASEAN compliant",                 "IV/Therapeutic":"Emerging",                         "Risk":"🟢 LOW",     "Conf.":"🟢 80"},
        {"Territory":"Malaysia",    "Body":"NPRA",         "Topical/Cosmetic":"ASEAN aligned",              "Soft Indications":"cGMP research active",             "IV/Therapeutic":"Early stage",                      "Risk":"🟢 LOW",     "Conf.":"🟢 75"},
        {"Territory":"Indonesia",   "Body":"BPOM",         "Topical/Cosmetic":"ASEAN cosmetic directive",   "Soft Indications":"Physician training pathway",       "IV/Therapeutic":"BPOM engaged",                     "Risk":"🟢 LOW",     "Conf.":"🟢 70"},
        {"Territory":"Colombia",    "Body":"INVIMA",       "Topical/Cosmetic":"2025 Regional Reform",       "Soft Indications":"LATAM integration",                "IV/Therapeutic":"Streamlined pathway",              "Risk":"🟢 LOW",     "Conf.":"🟡 60"},
        {"Territory":"Argentina",   "Body":"ANMAT",        "Topical/Cosmetic":"2025 Deregulation",          "Soft Indications":"Fast-track entry",                 "IV/Therapeutic":"Streamlined",                      "Risk":"🟢 LOW",     "Conf.":"🟡 60"},
    ])

    risk_filter = st.multiselect(
        "Filter by Risk Level",
        options=["🔴 HIGH","🟡 MEDIUM","🟡 LOW-MED","🟢 LOW"],
        default=["🔴 HIGH","🟡 MEDIUM","🟡 LOW-MED","🟢 LOW"],
    )
    st.dataframe(
        reg_df[reg_df["Risk"].isin(risk_filter)],
        hide_index=True, use_container_width=True, height=380,
    )
    st.caption("Conf. = Confidence score 0–100 based on validation against official sources. 🟢 70+ = High (govt/peer-reviewed); 🟡 50–69 = Medium (industry sources); 🔴 <50 = Low (unverified).")

    col_r1, col_r2 = st.columns(2)

    with col_r1:
        st.markdown('<div class="section-header">Regulatory Risk Distribution</div>', unsafe_allow_html=True)
        reg_df["Risk Level"] = reg_df["Risk"].str.extract(r"(HIGH|MEDIUM|LOW-MED|LOW)")
        risk_cnt = reg_df["Risk Level"].value_counts().reset_index()
        risk_cnt.columns = ["Risk Level", "Count"]
        fig_risk = px.pie(
            risk_cnt, names="Risk Level", values="Count",
            color="Risk Level",
            color_discrete_map={"HIGH":"#e05c2a","MEDIUM":"#f0c040","LOW-MED":"#90c040","LOW":"#4caf50"},
            hole=0.4,
        )
        fig_risk.update_layout(height=280, margin=dict(t=10, b=10))
        st.plotly_chart(fig_risk, use_container_width=True)

    with col_r2:
        st.markdown('<div class="section-header">Key Regulatory Milestones</div>', unsafe_allow_html=True)
        milestones = [
            ("✅ Jan 2026",  "signal-card",  "Philippines FDA cosmetic notification (UnicoCell) — ASEAN entry blueprint validated"),
            ("✅ Late 2025", "signal-card",  "ANVISA-COFEPRIS MoU operational — Brazil↔Mexico mutual recognition active"),
            ("✅ 2021",      "signal-card",  "Thai FDA launches HSA Reliance Route — Singapore approval fast-tracks SEA entry"),
            ("✅ Mar 2024",  "signal-card",  "Croma-Pharma × Aesthetic Mgmt Partners — confirms EU distribution appetite"),
            ("⚠️ May 2025", "warning-card", "FDA warning letter to Florida IV exosome clinic — US IV channel high risk"),
            ("⚠️ Ongoing",  "warning-card", "FDA 12+ warning letters total — US market = cosmetic channel only 2025–2028+"),
            ("⚠️ Ongoing",  "warning-card", "EU: <2 dozen ATMPs authorized, zero exosome-based — zero approved globally"),
            ("ℹ️ Jan 2025", "signal-card",  "Thai FDA drafting new health product import/export policy — favourable window now"),
        ]
        for date_str, cls, text in milestones:
            st.markdown(f'<div class="{cls}"><strong>{date_str}</strong> — {text}</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-header">ANVISA–COFEPRIS Strategic Alliance</div>', unsafe_allow_html=True)
    st.info(
        "🤝 Brazil and Mexico signed an MoU establishing mutual recognition for medicines, medical devices, and GMP. "
        "Mexico has designated ANVISA as a 'Reference Regulatory Authority'; Brazil recognizes COFEPRIS as an 'Equivalent "
        "Foreign Regulatory Authority'. Securing approval in one territory **cuts LATAM regulatory timeline by 40–60%**."
    )

    # ── Tab 4 Sources ────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">Regulation — Data Sources</div>', unsafe_allow_html=True)
    sources_tab4 = [
        ("FDA.gov", "Is It a Cosmetic, a Drug, or Both?", "Cosmetics cannot carry therapeutic claims; FDA cosmetics are not FDA-approved by definition"),
        ("FDA.gov", "Public Safety Notification on Exosome Products (updated 2025)", "12+ warning letters issued; allogeneic MSC exosomes classified as unlicensed biologics"),
        ("Atlantis Bioscience", "Regulatory Roadmap for Exosome-Based Therapeutics, Oct 2025", "FDA, EMA & ASEAN regulatory guide; warning letter database"),
        ("EMA", "Advanced Therapy Medicinal Products Authorization, 2022", "Fewer than 2 dozen ATMPs authorized total; zero exosome-based globally"),
        ("TGA Australia", "Regulation of Stem Cell Treatments — Information for Practitioners", "GMP licensing required for clinical exosome therapies; PBAC risk-sharing"),
        ("ANVISA / COFEPRIS", "DIA Global Forum Nov 2025 — MoU signed August 2025", "Mutual recognition for medicines, medical devices, and GMP between Brazil and Mexico"),
        ("UnicoCell Biomed / PH FDA", "Press Release Jan 2026; FDA Circular 2025-002", "Philippine FDA cosmetic notification approved; ASEAN Cosmetic Directive compliance"),
        ("HSA Singapore", "ASEAN Cosmetic Directive", "Harmonized cosmetics laws across ASEAN; Thai FDA HSA reliance route since 2021"),
        ("Siam Trade Development", "Cosmetic Product Registration Thailand (updated May 2024)", "Thai FDA post-market audit requirement for all cosmetic notifications"),
        ("ClinRegs NIAID", "Clinical Research Regulation for Thailand, Aug 2025", "Drug Act B.E. 2510 — no explicit exosome guideline as of March 2026"),
        ("PMC12007658", "Exosomes: A Comprehensive Review for the Practicing Dermatologist, 2025", "CD63 and CD81 confirmed as standard exosome surface markers"),
        ("PMC12371722", "Exploring Regulatory Frameworks for Exosome Therapy, 2025", "Global regulatory comparison; biomarker standards"),
    ]
    col_r_s1, col_r_s2 = st.columns(2)
    for i, (firm, title, detail) in enumerate(sources_tab4):
        col = col_r_s1 if i % 2 == 0 else col_r_s2
        col.markdown(
            f'<div class="signal-card" style="margin:3px 0;padding:6px 10px;">'
            f'<strong>{firm}</strong> — <em>{title}</em><br>'
            f'<span style="font-size:.82rem;color:#444;">{detail}</span></div>',
            unsafe_allow_html=True,
        )

# ════════════════════════════════════════════════════════════════
# TAB 5 — PRICING & COGS
# ════════════════════════════════════════════════════════════════
with tabs[4]:
    st.markdown("")

    subtabs = st.tabs([
        "🔬 Per-10B Particle Benchmark",
        "💊 Per-Treatment OOP (Validated)",
        "📦 B2B Derived from 10B Data",
        "🗺️ Market Ceiling Analysis",
        "🧮 BM-MSC COGS Breakdown",
    ])

    # ── Sub-tab 1: PER-10B PARTICLE BENCHMARK ────────────────────
    with subtabs[0]:
        st.markdown('<div class="section-header">Per-10B Particle Price — The Primary Benchmark</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="signal-card">📊 <strong>Why per-10B particles?</strong> '
            "Vial sizes, particle concentrations, and formats vary widely across products — making raw vial prices "
            "meaningless for comparison. Normalizing to 10 billion (10B) particles is the only way to compare "
            "pricing across products, markets, and channels on an equivalent basis. "
            "All observed prices below come from independent retail and supplier sources.</div>",
            unsafe_allow_html=True,
        )
        st.markdown("")

        # ── Per-10B observed data ─────────────────────────────────
        p10b_df = pd.DataFrame([
            {"Product":"EXOMIDE (Jolifill, Germany)",    "Source Type":"Retail",      "Vial Size":"5mL",       "Vial Price":"€115 (~$125)","10B Low":250,"10B High":250,"Confidence":"🟢 High","Source":"Jolifill.de — confirmed"},
            {"Product":"EXOGEN (HUK Aesthetics, UK)",    "Source Type":"Retail",      "Vial Size":"1mg+6mL",   "Vial Price":"£60 2-vial kit","10B Low":37,"10B High":75,"Confidence":"🟢 High","Source":"HUK Aesthetics — confirmed"},
            {"Product":"EXOXE Exosomes (50mg, EU/CEE)",  "Source Type":"Retail",      "Vial Size":"50mg",      "Vial Price":"~$85 (80 EUR)","10B Low":60,"10B High":90,"Confidence":"🟢 High","Source":"EU/CEE retail — confirmed"},
            {"Product":"Selastin Exo Plus (100mg, Poland)","Source Type":"Retail",    "Vial Size":"100mg liquid","Vial Price":"~$50 (46 EUR)","10B Low":35,"10B High":55,"Confidence":"🟢 High","Source":"Poland/CEE retail — confirmed"},
            {"Product":"EXOJUV (plant-derived)",         "Source Type":"Wholesale",   "Vial Size":"6B/vial",   "Vial Price":"$150–200","10B Low":250,"10B High":333,"Confidence":"🟡 Med","Source":"MedicaDepot wholesale"},
            {"Product":"EXOBLOOM (Dermax)",              "Source Type":"Wholesale",   "Vial Size":"5B+/vial",  "Vial Price":"$120–180","10B Low":240,"10B High":360,"Confidence":"🟡 Med","Source":"DermaxMed B2B"},
            {"Product":"ReBellaXO (UC-MSC, R3)",         "Source Type":"Wholesale",   "Vial Size":"15B/cc",    "Vial Price":"$300–450","10B Low":200,"10B High":300,"Confidence":"🟡 Med","Source":"R3 Stem Cell 2024"},
            {"Product":"Generic BM-MSC (Alibaba B2B)",   "Source Type":"B2B Bulk",    "Vial Size":"1mg≈10–15B","Vial Price":"$180–280/mg","10B Low":150,"10B High":280,"Confidence":"🟡 Med","Source":"Alibaba supplier data 2024–25"},
            {"Product":"BENEV (ExoCoBio US)",            "Source Type":"Professional","Vial Size":"20–30B est.","Vial Price":"$400–600","10B Low":160,"10B High":250,"Confidence":"🟡 Med","Source":"US professional channel est."},
        ])
        p10b_df["10B Mid"] = ((p10b_df["10B Low"] + p10b_df["10B High"]) / 2).astype(int)

        # ── Horizontal range bar chart — per-10B ─────────────────
        p10b_sorted = p10b_df.sort_values("10B Mid", ascending=True)
        fig_10b = go.Figure()
        conf_colors = {"🟢 High":"#3db07a","🟡 Med":"#f0a030"}
        for _, row in p10b_sorted.iterrows():
            spread = max(row["10B High"] - row["10B Low"], 1)
            fig_10b.add_trace(go.Bar(
                x=[spread], y=[row["Product"].split("(")[0].strip()],
                base=[row["10B Low"]],
                orientation="h",
                marker_color=conf_colors.get(row["Confidence"],"#2e6da4"),
                text=f'${row["10B Low"]}–${row["10B High"]}',
                textposition="inside",
                hovertemplate=(
                    f"<b>{row['Product']}</b><br>"
                    f"Per 10B: ${row['10B Low']}–${row['10B High']}<br>"
                    f"Vial: {row['Vial Price']} ({row['Vial Size']})<br>"
                    f"Confidence: {row['Confidence']}<br>"
                    f"Source: {row['Source']}<extra></extra>"
                ),
            ))

        # Add market zone annotations
        fig_10b.add_vrect(x0=150, x1=280, fillcolor="#fffbeb", opacity=0.4,
                          annotation_text="BM-MSC bulk zone", annotation_position="top left")
        fig_10b.add_vrect(x0=200, x1=360, fillcolor="#dbeafe", opacity=0.3,
                          annotation_text="Aesthetic wholesale zone", annotation_position="top right")

        fig_10b.update_layout(
            height=380, barmode="overlay", showlegend=False,
            xaxis_title="Price per 10 Billion Particles (USD)",
            yaxis_title="", margin=dict(t=40, b=10),
            title="Observed Market Prices per 10B Particles — the only valid cross-product comparison",
        )
        st.plotly_chart(fig_10b, use_container_width=True)
        st.caption("🟢 Green = independently confirmed by retail sources | 🟠 Amber = estimated from supplier/wholesale data")
        st.markdown("")

        # ── Full data table ───────────────────────────────────────
        st.markdown('<div class="section-header">Full Per-10B Particle Data Table</div>', unsafe_allow_html=True)
        display_cols = ["Product","Source Type","Vial Size","Vial Price","10B Low","10B High","10B Mid","Confidence","Source"]
        st.dataframe(
            p10b_df[display_cols].assign(**{
                "10B Low": p10b_df["10B Low"].apply(lambda x: f"${x:,}"),
                "10B High": p10b_df["10B High"].apply(lambda x: f"${x:,}"),
                "10B Mid": p10b_df["10B Mid"].apply(lambda x: f"${x:,}"),
            }),
            hide_index=True, use_container_width=True,
        )

        # ── Key takeaways ─────────────────────────────────────────
        st.markdown("")
        st.markdown('<div class="section-header">Key Takeaways from Per-10B Benchmark</div>', unsafe_allow_html=True)
        col_k1, col_k2 = st.columns(2)
        with col_k1:
            st.markdown('<div class="validated-card">📊 <strong>Observed market range:</strong> $37–360/10B particles across all product types. The confirmed retail range (EXOMIDE, EXOGEN) spans $37–250. The commercial aesthetic wholesale cluster sits at <strong>$150–333/10B</strong>.</div>', unsafe_allow_html=True)
            st.markdown('<div class="validated-card">🧬 <strong>BM-MSC positioning:</strong> Generic BM-MSC bulk (Alibaba) prices at $150–280/10B. A branded, GMP-certified BM-MSC product with full CoA should command <strong>$200–350/10B</strong> — justified by clinical literature superiority over plant-derived alternatives ($250–360/10B).</div>', unsafe_allow_html=True)
        with col_k2:
            st.markdown('<div class="unverified-card">⚠️ <strong>Research grade ≠ clinical:</strong> ZenBio research-grade BM-MSC EVs cost $4,000–8,000/10B — 10–20x commercial aesthetic pricing. These are not clinical-grade and not relevant to commercial channel positioning.</div>', unsafe_allow_html=True)
            st.markdown('<div class="signal-card">💡 <strong>Pricing recommendation:</strong> Use $200–350/10B as your target B2B range. This is consistent with observed aesthetics wholesale data, positions above generic bulk BM-MSC, and below research-grade pricing. It is <em>per-10B-particle normalized</em> — convert to per-vial price by multiplying by your vial particle count.</div>', unsafe_allow_html=True)

    # ── Sub-tab 2: PER-TREATMENT OOP ─────────────────────────────
    with subtabs[1]:
        st.markdown('<div class="section-header">Per-Treatment Patient OOP Pricing by Indication</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="signal-card">📊 Per-treatment prices include multiple vials + procedure fee + consultation. '
            "Sources: Bookimed (Mexico $3,000–5,000/treatment; Thailand $2,000–4,000); "
            "R3 Stem Cell Mexico (150B exosomes $3,950); BioInformant USA ($3,500–6,500); "
            "Miami/Las Vegas average $4,900/session.</div>",
            unsafe_allow_html=True,
        )
        st.markdown("")

        oop_df = pd.DataFrame([
            {"Indication":"Facial Skin Rejuvenation",    "Dose/Session":"5–10B",  "Sessions":"3",   "Mat. Cost Clinic":"$50–150",  "OOP Low":400,  "OOP High":900,  "Markets":"EU, SEA, UAE, TH",     "Conf":"🟢 High"},
            {"Indication":"Hair Restoration",            "Dose/Session":"10–20B", "Sessions":"3–6", "Mat. Cost Clinic":"$100–250", "OOP Low":900,  "OOP High":2300, "Markets":"UAE, US, EU, TH",       "Conf":"🟢 High"},
            {"Indication":"Wound Healing / Scar",        "Dose/Session":"10–30B", "Sessions":"1–3", "Mat. Cost Clinic":"$150–400", "OOP Low":500,  "OOP High":2000, "Markets":"MX, TH, SEA, AU",       "Conf":"🟡 Med"},
            {"Indication":"Joint Pain / Osteoarthritis", "Dose/Session":"30–50B", "Sessions":"1–2", "Mat. Cost Clinic":"$350–700", "OOP Low":1500, "OOP High":3500, "Markets":"MX, UAE, TH, SEA",      "Conf":"🟢 High"},
            {"Indication":"Systemic IV Longevity",       "Dose/Session":"50–100B","Sessions":"2–4", "Mat. Cost Clinic":"$700–1,500","OOP Low":3750, "OOP High":5500,"Markets":"UAE, AU, TH (premium)", "Conf":"🟢 High"},
            {"Indication":"Post-Procedure Recovery",     "Dose/Session":"5B",     "Sessions":"1",   "Mat. Cost Clinic":"$40–100",  "OOP Low":150,  "OOP High":400,  "Markets":"EU, SEA, US, TH",       "Conf":"🟡 Med"},
        ])
        oop_df["OOP Mid"] = ((oop_df["OOP Low"] + oop_df["OOP High"]) / 2).astype(int)

        fig_oop = go.Figure()
        colors = ["#1e3a5f","#2e6da4","#4a90d9","#7ec8e3","#b3dff0","#e05c2a"]
        for i, row in oop_df.iterrows():
            fig_oop.add_trace(go.Bar(
                name=row["Indication"], x=[row["Indication"]],
                y=[row["OOP High"] - row["OOP Low"]], base=[row["OOP Low"]],
                marker_color=colors[i % len(colors)],
                text=f'${row["OOP Low"]:,}–${row["OOP High"]:,}',
                textposition="inside",
                hovertemplate=f"<b>{row['Indication']}</b><br>${row['OOP Low']:,}–${row['OOP High']:,}<br>Markets: {row['Markets']}<br>Confidence: {row['Conf']}<extra></extra>",
            ))
        fig_oop.update_layout(
            showlegend=False, height=400, barmode="stack",
            yaxis_title="OOP Price to Patient (USD)",
            xaxis_tickangle=-20,
            title="Patient OOP Price Range by Indication (full treatment course)",
        )
        st.plotly_chart(fig_oop, use_container_width=True)
        st.dataframe(
            oop_df[["Indication","Dose/Session","Sessions","Mat. Cost Clinic","OOP Low","OOP High","Markets","Conf"]]
            .assign(**{"OOP Low": oop_df["OOP Low"].apply(lambda x: f"${x:,}"),
                       "OOP High": oop_df["OOP High"].apply(lambda x: f"${x:,}")}),
            hide_index=True, use_container_width=True,
        )
        st.caption("Sources: Bookimed clinic data (Mexico, Thailand); R3 Stem Cell Mexico pricing; BioInformant US market research; EDEN Aesthetics Dubai protocol data.")
        st.markdown("")

        # ── US vs CEE OOP comparison ──────────────────────────────
        st.markdown('<div class="section-header">🆕 OOP Price Comparison — US (FL/NV) vs CEE (Poland/Prague)</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="validated-card">✅ CEE prices confirmed from clinic sources: Poland LaserMe+ASCE+ ~2,000 PLN (~$500/session); '
            "Prague skin therapy ~7,500 CZK (~$320/session). US averages: Miami/Las Vegas single session ~$4,900; comprehensive plan up to $15,000.</div>",
            unsafe_allow_html=True,
        )
        cee_oop = pd.DataFrame([
            {"Indication":"Facial Skin Rejuvenation","US (FL/NV) Low":400, "US (FL/NV) High":900, "CEE (PL/CZ) Low":150,"CEE (PL/CZ) High":300},
            {"Indication":"Hair Restoration",        "US (FL/NV) Low":900, "US (FL/NV) High":2300,"CEE (PL/CZ) Low":400,"CEE (PL/CZ) High":650},
            {"Indication":"Joint Pain / Ortho",      "US (FL/NV) Low":1500,"US (FL/NV) High":3500,"CEE (PL/CZ) Low":600,"CEE (PL/CZ) High":1200},
            {"Indication":"Longevity IV Drip",       "US (FL/NV) Low":3750,"US (FL/NV) High":5500,"CEE (PL/CZ) Low":1200,"CEE (PL/CZ) High":2500},
        ])
        cee_oop["US Mid"]  = (cee_oop["US (FL/NV) Low"]  + cee_oop["US (FL/NV) High"])  / 2
        cee_oop["CEE Mid"] = (cee_oop["CEE (PL/CZ) Low"] + cee_oop["CEE (PL/CZ) High"]) / 2

        fig_cee = go.Figure()
        for indication, us_mid, cee_mid in zip(cee_oop["Indication"], cee_oop["US Mid"], cee_oop["CEE Mid"]):
            fig_cee.add_trace(go.Bar(name=f"US — {indication}", x=["US (FL/NV)"], y=[us_mid],
                marker_color="#1e3a5f", showlegend=False,
                text=f"${int(us_mid):,}", textposition="outside"))
            fig_cee.add_trace(go.Bar(name=f"CEE — {indication}", x=["CEE (PL/CZ)"], y=[cee_mid],
                marker_color="#7ec8e3", showlegend=False,
                text=f"${int(cee_mid):,}", textposition="outside"))

        # Cleaner grouped bar
        fig_cee2 = px.bar(
            cee_oop.melt(id_vars="Indication", value_vars=["US Mid","CEE Mid"],
                         var_name="Market", value_name="OOP ($)"),
            x="Indication", y="OOP ($)", color="Market", barmode="group",
            color_discrete_map={"US Mid":"#1e3a5f","CEE Mid":"#7ec8e3"},
            text_auto=",.0f",
            title="OOP Patient Price: US (Florida/Nevada) vs CEE (Poland/Czech Republic)",
        )
        fig_cee2.update_traces(textposition="outside")
        fig_cee2.update_layout(height=360, margin=dict(t=50,b=10), xaxis_tickangle=-15,
                               yaxis_title="OOP Price (USD)", legend_title="Market")
        st.plotly_chart(fig_cee2, use_container_width=True)
        st.caption("CEE pricing represents ~30–50% discount vs US. High-volume CEE channel compensates for lower per-session margin with throughput from W. European medical tourists.")

    # ── Sub-tab 3: B2B DERIVED FROM 10B DATA ─────────────────────
    with subtabs[2]:
        st.markdown('<div class="section-header">B2B Channel Pricing — Derived from Per-10B Benchmark</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="signal-card">📊 B2B price targets derived from observed per-10B market data ($150–360/10B). '
            "A distributor will accept a price if it allows a 30–50% markup and remains competitive. "
            "Convert to per-vial pricing by multiplying by your product's particle count per vial.</div>",
            unsafe_allow_html=True,
        )
        st.markdown("")

        # ── Per-10B to per-vial calculator ────────────────────────
        st.markdown('<div class="section-header">Per-Vial Price Calculator — Enter Your Particle Count</div>', unsafe_allow_html=True)
        col_calc1, col_calc2 = st.columns([1, 2])
        with col_calc1:
            particles_per_vial = st.number_input(
                "Particles per vial (Billions)",
                min_value=1, max_value=200, value=10, step=1,
                help="Enter how many billion particles your vial contains per NTA measurement"
            )
            price_per_10b = st.slider(
                "Your target price per 10B particles (USD)",
                min_value=50, max_value=500, value=220, step=10,
            )
            calc_vial_price = (price_per_10b / 10) * particles_per_vial
            st.markdown(
                f'<div class="validated-card">💰 <strong>Your per-vial price:</strong><br>'
                f'<span style="font-size:1.6rem;font-weight:700;color:#1e3a5f;">${calc_vial_price:,.0f}</span><br>'
                f'<span style="font-size:.85rem;">({particles_per_vial}B particles × ${price_per_10b}/10B)</span></div>',
                unsafe_allow_html=True,
            )

        with col_calc2:
            # ── B2B tier table using per-10B as anchor ────────────
            tier_df = pd.DataFrame([
                {"Channel Tier":"Premium Ortho/Medical","Vial Format":"Lyo 10–30B","Target per 10B":"$220–350","Derived from":"Upper range BM-MSC bulk + clinical lit premium","Max to Distributor":"$165–265/10B","Distributor Markup":"~30%","Conf":"🟡 Derived"},
                {"Channel Tier":"Aesthetic/Wellness",   "Vial Format":"Lyo 5–15B", "Target per 10B":"$180–280","Derived from":"Mid-range aesthetic wholesale observed ($200–333/10B)","Max to Distributor":"$130–210/10B","Distributor Markup":"~30%","Conf":"🟡 Derived"},
                {"Channel Tier":"Distributor/Wholesale","Vial Format":"Bulk lyo",   "Target per 10B":"$150–220","Derived from":"Lower observed aesthetic range; Alibaba B2B anchor ($150–280/10B)","Max to Distributor":"$110–165/10B","Distributor Markup":"~30%","Conf":"🟡 Derived"},
                {"Channel Tier":"CDMO / Bulk",          "Vial Format":"GMP lyo/frozen","Target per 10B":"$120–160","Derived from":"Below Alibaba B2B floor with GMP premium","Max to Distributor":"$90–120/10B","Distributor Markup":"~25%","Conf":"🟡 Derived"},
            ])
            st.dataframe(tier_df, hide_index=True, use_container_width=True)
            st.caption("'Max to Distributor' = price you can charge distributor and still allow them ~30% markup to reach observed market prices.")

        # ── Per-10B competitive positioning chart ─────────────────
        st.markdown('<div class="section-header">BM-MSC Positioning vs Observed Market per 10B Particles</div>', unsafe_allow_html=True)

        pos_df = pd.DataFrame({
            "Product/Tier": [
                "EXOGEN (UK retail, confirmed)",
                "Generic BM-MSC bulk (Alibaba)",
                "BENEV / ExoCoBio (US)",
                "ReBellaXO UC-MSC (R3)",
                "⭐ BM-MSC Aesthetic/Wellness target",
                "EXOMIDE (EU retail, confirmed)",
                "⭐ BM-MSC Premium Ortho target",
                "EXOJUV plant-derived",
                "EXOBLOOM plant-derived",
            ],
            "Low":  [37,  150, 160, 200, 180, 250, 220, 250, 240],
            "High": [75,  280, 250, 300, 280, 250, 350, 333, 360],
            "Type": ["Confirmed","Observed","Observed","Observed","BM-MSC Target","Confirmed","BM-MSC Target","Observed","Observed"],
        })
        pos_df["Mid"] = (pos_df["Low"] + pos_df["High"]) / 2
        pos_df = pos_df.sort_values("Mid", ascending=True)

        type_colors = {
            "Confirmed":   "#3db07a",
            "Observed":    "#2e6da4",
            "BM-MSC Target":"#e05c2a",
        }
        fig_pos = go.Figure()
        for _, row in pos_df.iterrows():
            fig_pos.add_trace(go.Bar(
                x=[row["High"] - row["Low"]],
                y=[row["Product/Tier"]],
                base=[row["Low"]],
                orientation="h",
                marker_color=type_colors.get(row["Type"],"#7ec8e3"),
                marker_line=dict(width=2 if "⭐" in row["Product/Tier"] else 0, color="#c62828"),
                text=f'${int(row["Low"])}–${int(row["High"])}',
                textposition="inside",
                hovertemplate=f"<b>{row['Product/Tier']}</b><br>${row['Low']}–${row['High']} per 10B<extra></extra>",
            ))
        fig_pos.update_layout(
            height=440, barmode="overlay", showlegend=False,
            xaxis_title="Price per 10B Particles (USD)",
            yaxis_title="", margin=dict(t=20, b=10),
            title="BM-MSC target pricing (⭐ orange) vs observed market (green = confirmed, blue = estimated)",
        )
        st.plotly_chart(fig_pos, use_container_width=True)
        st.caption("⭐ Orange bars = recommended BM-MSC target ranges derived from observed market data. These sit above generic bulk (Alibaba) and align with branded aesthetic products — justified by GMP certification and clinical literature.")

    # ── Sub-tab 4: MARKET CEILING ANALYSIS ───────────────────────
    with subtabs[3]:
        st.markdown('<div class="section-header">Distributor Attractiveness Matrix — Market Ceiling Analysis</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="signal-card">📊 End-user price ranges estimated from per-treatment OOP data divided by typical session counts. '
            "B2B ceilings and COGS targets are indicative — verify with direct market quotes before use.</div>",
            unsafe_allow_html=True,
        )
        st.markdown("")

        attr_df = pd.DataFrame([
            {"Market":"Germany/EU",     "Est. End-User/Vial":"$100–200 (est.)", "Max B2B":"$50–100 (est.)", "COGS Target":"<$30–60",  "Key Pitch":"BM-MSC clinical lit; CD73/CD90 CoA; NTA data","Conf":"🟡 Estimate"},
            {"Market":"UAE/GCC",        "Est. End-User/Vial":"$180–350 (est.)", "Max B2B":"$90–175 (est.)", "COGS Target":"<$55–100", "Key Pitch":"Longevity angle; high-dose IV protocols",       "Conf":"🟡 Estimate"},
            {"Market":"Mexico/LATAM",   "Est. End-User/Vial":"$100–200 (est.)", "Max B2B":"$50–100 (est.)", "COGS Target":"<$30–60",  "Key Pitch":"Lyophilized; ANVISA-COFEPRIS MoU compliance",   "Conf":"🟡 Estimate"},
            {"Market":"Thailand",       "Est. End-User/Vial":"$80–180 (est.)",  "Max B2B":"$40–90 (est.)",  "COGS Target":"<$25–55",  "Key Pitch":"Thai FDA cosmetic notification; ASEAN docs",    "Conf":"🟡 Estimate"},
            {"Market":"Philippines/SEA","Est. End-User/Vial":"$60–120 (est.)",  "Max B2B":"$30–60 (est.)",  "COGS Target":"<$20–40",  "Key Pitch":"PH FDA notification gateway; ASEAN directive",  "Conf":"🟡 Estimate"},
            {"Market":"USA (aesthetic)","Est. End-User/Vial":"$150–300 (est.)", "Max B2B":"$75–150 (est.)", "COGS Target":"<$45–90",  "Key Pitch":"CoA CD63/CD81; no therapeutic claims; GMP",     "Conf":"🟡 Estimate"},
            {"Market":"Australia",      "Est. End-User/Vial":"$180–350 (est.)", "Max B2B":"$90–175 (est.)", "COGS Target":"<$55–100", "Key Pitch":"TGA compliance documentation",                  "Conf":"🟡 Estimate"},
        ])
        st.dataframe(attr_df, hide_index=True, use_container_width=True)

        # ── B2B mid-range chart ───────────────────────────────────
        st.markdown('<div class="section-header">Estimated B2B Price Midpoint by Market (per 10B particles)</div>', unsafe_allow_html=True)
        b2b_df = pd.DataFrame({
            "Market": ["Germany/EU","UAE/GCC","USA","Australia","Mexico/LATAM","Thailand","Philippines/SEA"],
            "Low":    [50,  90, 75, 90, 50, 40, 30],
            "High":   [100, 175,150,175,100, 90, 60],
        })
        b2b_df["Mid"] = (b2b_df["Low"] + b2b_df["High"]) / 2
        b2b_df = b2b_df.sort_values("Mid", ascending=True)

        fig_b2b = go.Figure()
        fig_b2b.add_trace(go.Bar(
            x=b2b_df["Mid"], y=b2b_df["Market"], orientation="h",
            marker_color="#2e6da4", name="Midpoint B2B (est.)",
            error_x=dict(type="data", symmetric=False,
                array=b2b_df["High"] - b2b_df["Mid"],
                arrayminus=b2b_df["Mid"] - b2b_df["Low"],
                color="#1e3a5f", thickness=2),
            text=[f"~${int(v):,}" for v in b2b_df["Mid"]],
            textposition="outside",
        ))
        fig_b2b.update_layout(
            height=300, margin=dict(t=20, b=10),
            xaxis_title="Estimated B2B Price per 10B-particle vial (USD)",
            yaxis_title="", showlegend=False,
            title="Estimated B2B Price Midpoint by Market (per 10B particles)",
        )
        st.plotly_chart(fig_b2b, use_container_width=True)
        st.caption("B2B price estimates derived from observed retail market range of $37–360/10B particles. Verify with direct market quotes.")

    # ── Sub-tab 5: COGS BREAKDOWN ─────────────────────────────────
    with subtabs[4]:
        st.markdown('<div class="section-header">BM-MSC Exosome COGS — Component Breakdown (per 10B-particle dose)</div>', unsafe_allow_html=True)
        st.markdown("")

        cogs_df = pd.DataFrame([
            {"Component":"BM-MSC donor procurement",    "2023 Low":800,  "2023 High":1200, "2026 Low":500,  "2026 High":800,  "2030 Low":200, "2030 High":350},
            {"Component":"Cell expansion media (GMP)",  "2023 Low":600,  "2023 High":900,  "2026 Low":400,  "2026 High":600,  "2030 Low":150, "2030 High":250},
            {"Component":"Bioreactor operation",        "2023 Low":400,  "2023 High":700,  "2026 Low":250,  "2026 High":400,  "2030 Low":80,  "2030 High":150},
            {"Component":"Isolation & purification",    "2023 Low":600,  "2023 High":1000, "2026 Low":350,  "2026 High":600,  "2030 Low":100, "2030 High":200},
            {"Component":"QC & characterization",       "2023 Low":400,  "2023 High":600,  "2026 Low":250,  "2026 High":400,  "2030 Low":80,  "2030 High":150},
            {"Component":"Lyophilization (optional)",   "2023 Low":200,  "2023 High":400,  "2026 Low":150,  "2026 High":250,  "2030 Low":50,  "2030 High":100},
            {"Component":"Batch release / regulatory",  "2023 Low":300,  "2023 High":500,  "2026 Low":200,  "2026 High":350,  "2030 Low":80,  "2030 High":150},
        ])

        year_sel = st.radio("Select year view", ["2023 (Baseline)", "2026 (Current)", "2030 (Target)"], horizontal=True)
        if "2023" in year_sel: lo, hi = "2023 Low", "2023 High"
        elif "2026" in year_sel: lo, hi = "2026 Low", "2026 High"
        else: lo, hi = "2030 Low", "2030 High"

        cogs_df["Mid"] = (cogs_df[lo] + cogs_df[hi]) / 2
        total_lo = cogs_df[lo].sum()
        total_hi = cogs_df[hi].sum()

        col_cg1, col_cg2 = st.columns([1, 1])
        with col_cg1:
            fig_cogs_bar = px.bar(
                cogs_df, x="Mid", y="Component", orientation="h",
                color="Mid", color_continuous_scale=["#b3dff0","#1e3a5f"],
                error_x=((cogs_df[hi] - cogs_df[lo]) / 2),
                title=f"COGS Breakdown — {year_sel}",
                text=[f"${int(v):,}" for v in cogs_df["Mid"]],
            )
            fig_cogs_bar.update_traces(textposition="outside")
            fig_cogs_bar.update_layout(
                height=380, margin=dict(t=40, b=10),
                coloraxis_showscale=False,
                xaxis_title="USD per dose", yaxis_title="",
            )
            fig_cogs_bar.add_vline(
                x=total_lo, line_dash="dot", line_color="#e05c2a",
                annotation_text=f"Total low: ${total_lo:,}", annotation_position="top right",
            )
            st.plotly_chart(fig_cogs_bar, use_container_width=True)

        with col_cg2:
            fig_cogs_pie = px.pie(
                cogs_df, names="Component", values="Mid",
                color_discrete_sequence=["#1e3a5f","#2e6da4","#4a90d9","#7ec8e3","#b3dff0","#e05c2a","#f0a07a"],
                hole=0.4, title=f"COGS Share — {year_sel}",
            )
            fig_cogs_pie.update_traces(textinfo="percent+label", textposition="outside")
            fig_cogs_pie.update_layout(height=380, margin=dict(t=40, b=80), showlegend=False)
            st.plotly_chart(fig_cogs_pie, use_container_width=True)

        st.markdown(
            f'<div class="signal-card">📊 <strong>Total COGS — {year_sel}:</strong> '
            f'<strong>${total_lo:,} – ${total_hi:,}</strong> per 10B-particle clinical dose. '
            f'2023: $3,100–4,900 | 2026: $1,950–3,150 | 2030 target: $690–1,050. '
            f'BM-MSC is ~15–25% higher than UC-MSC due to donor procurement complexity. '
            f'Sources: Astute Analytica 2035; RoosterBio 2025; Corning/RoosterBio roundtable Feb 2025.</div>',
            unsafe_allow_html=True,
        )

        st.markdown('<div class="section-header">COGS Trajectory — 2023 to 2030</div>', unsafe_allow_html=True)
        traj_df = pd.DataFrame({
            "Year":  [2023, 2024, 2026, 2028, 2030],
            "Low":   [3100, 2600, 1950, 1200, 690],
            "High":  [4900, 4200, 3150, 1900, 1050],
            "Scale": ["Research (<100 doses/mo)","Small batch","Commercial mid (500–2k/mo)","Scale-up","Industrial (>5k/mo)"],
        })
        traj_df["Mid"] = (traj_df["Low"] + traj_df["High"]) / 2

        fig_traj = go.Figure()
        fig_traj.add_trace(go.Scatter(x=traj_df["Year"], y=traj_df["High"],
            fill=None, mode="lines", line_color="#b3dff0", name="COGS High"))
        fig_traj.add_trace(go.Scatter(x=traj_df["Year"], y=traj_df["Low"],
            fill="tonexty", mode="lines", line_color="#7ec8e3",
            fillcolor="rgba(126,200,227,0.25)", name="COGS Range"))
        fig_traj.add_trace(go.Scatter(x=traj_df["Year"], y=traj_df["Mid"],
            mode="lines+markers+text",
            line=dict(color="#1e3a5f", width=3),
            marker=dict(size=10, color="#2e6da4"),
            text=[f"${int(v):,}" for v in traj_df["Mid"]],
            textposition="top center", name="COGS Midpoint"))
        fig_traj.update_layout(
            height=320, margin=dict(t=20, b=10),
            xaxis_title="Year", yaxis_title="COGS per 10B-particle dose (USD)",
            title="BM-MSC Exosome COGS Trajectory (with range band)",
            legend=dict(orientation="h", yanchor="bottom", y=1.01),
        )
        st.plotly_chart(fig_traj, use_container_width=True)

        st.markdown('<div class="section-header">BM-MSC vs Other MSC Sources — Cost Comparison</div>', unsafe_allow_html=True)
        src_df = pd.DataFrame([
            {"Parameter":"Raw material cost ($/mg purified)","BM-MSC":"$180–280","UC-MSC (WJ)":"$130–200","Adipose MSC":"$100–180"},
            {"Parameter":"Donor material cost",              "BM-MSC":"Higher — invasive harvest","UC-MSC (WJ)":"Lower — birth waste","Adipose MSC":"Moderate — liposuction"},
            {"Parameter":"Expansion difficulty",            "BM-MSC":"Moderate–High","UC-MSC (WJ)":"Lower","Adipose MSC":"Moderate"},
            {"Parameter":"Yield per bioreactor run",        "BM-MSC":"Lower relative yield","UC-MSC (WJ)":"Highest yield","Adipose MSC":"Moderate"},
            {"Parameter":"Exosome potency (ortho/neuro)",   "BM-MSC":"Highest evidence base","UC-MSC (WJ)":"High — most commercial","Adipose MSC":"Moderate"},
            {"Parameter":"Regulatory differentiation",      "BM-MSC":"Strong clinical lit.","UC-MSC (WJ)":"Most commercially available","Adipose MSC":"Lower clinical lit."},
        ])
        st.dataframe(src_df, hide_index=True, use_container_width=True)

    # ── Tab 5 Sources ────────────────────────────────────────────
    st.markdown("---")
    st.markdown('<div class="section-header">Pricing & COGS — Data Sources</div>', unsafe_allow_html=True)
    sources_tab5 = [
        ("Jolifill.de", "EXOMIDE Exosome 2-set box professional pricing, Mar 2026", "€115 (~$125) per 5mL vial — confirmed retail price"),
        ("HUK Aesthetics", "EXOGEN Exosomes 1mg + 6mL Vial", "£59.99 (~$75) for 2-vial kit — confirmed retail price"),
        ("MedicaDepot.com", "EXOJUV wholesale pricing, Mar 2026", "~$150–200/vial (6B particles); ~$250–333 per 10B"),
        ("DermaxMed.com", "EXOBLOOM B2B pricing and wholesale guide 2025", "~$120–180/vial (5B+ particles); ~$240–360 per 10B"),
        ("R3 Stem Cell / Regen Suppliers", "ReBellaXO product and pricing page 2024", "~$300–450/vial (15B/cc); ~$200–300 per 10B"),
        ("Alibaba B2B", "Exosome Producer Supplier Guide — B2B pricing benchmarks 2024–25", "Generic BM-MSC $180–280/mg; ~$150–280 per 10B"),
        ("Strategic Reconciliation Report", "BM-MSC Sector Analysis, March 2026", "EXOXE Exosomes (50mg) ~$85 (80 EUR) EU/CEE; Selastin Exo Plus (100mg) ~$50 (46 EUR) Poland"),
        ("Bookimed", "Exosome therapy in Mexico; Thailand 2026", "Mexico $3,000–5,000/treatment; Thailand $2,000–4,000/treatment"),
        ("R3 Stem Cell Mexico", "150 Billion Exosomes for $3,950 announcement", "Mexico OOP benchmark: 150B exosomes for $3,950"),
        ("BioInformant", "Exosome Therapy Costs 2025", "US typical full treatment $3,500–6,500; Miami/Las Vegas average $4,900/session"),
        ("Astute Analytica", "Exosome Therapy Market Size, Growth Trends Analysis 2035", "COGS trajectory: 2023 $3,100–4,900; 2026 $1,950–3,150; 2030 $690–1,050 per 10B particles"),
        ("RoosterBio", "Exosome Production Bioreactor Kits — BM, UC, AD-derived, 2025", "Component cost benchmarks; hollow-fiber bioreactor 60–70% media reduction"),
        ("Corning / Cell & Gene Therapy Insights", "MSC Manufacturing Expert Roundtable, Feb 2025", "BM-MSC donor procurement cost trends; bank pooling cost reductions"),
        ("QY Research", "Exosome Lyophilization Global Market Forecast 2026–2032", "Lyophilization segment $50–60M → low hundreds of millions by early 2030s"),
        ("Frontiers in Pharmacology", "Trends in MSC-EV Clinical Trials 2014–2024, Wang et al. 2025", "Dose estimates per indication; clinical trial dosing review"),
    ]
    col_p_s1, col_p_s2 = st.columns(2)
    for i, (firm, title, detail) in enumerate(sources_tab5):
        col = col_p_s1 if i % 2 == 0 else col_p_s2
        col.markdown(
            f'<div class="signal-card" style="margin:3px 0;padding:6px 10px;">'
            f'<strong>{firm}</strong> — <em>{title}</em><br>'
            f'<span style="font-size:.82rem;color:#444;">{detail}</span></div>',
            unsafe_allow_html=True,
        )
# ════════════════════════════════════════════════════════════════
# TAB 6 — SIGNALS & TRENDS
# ════════════════════════════════════════════════════════════════
with tabs[5]:
    # ── Signals table ────────────────────────────────────────────
    st.markdown('<div class="section-header">Key Market Signals (2023–2026)</div>', unsafe_allow_html=True)

    # ── Static baseline (fallback if live data unavailable) ──────
    STATIC_SIGNALS = pd.DataFrame([
        {"date":"Jan 2026",    "type":"Regulatory",  "event":"Philippine FDA Cosmetic Notification — UnicoCell",           "impact":"ASEAN gateway validated; blueprint for TH, MY, ID",            "sentiment":"🟢 Positive", "territory":"Philippines", "source":"UnicoCell Biomed press release, Jan 2026; CIRS Group — cirs-group.com/en/cosmetics/philippines-amends-asean-cosmetic-directive"},
        {"date":"May 2025",    "type":"Enforcement", "event":"FDA warning letter — Florida IV exosome clinic",             "impact":"US IV channel high risk; pivot to topical/cosmetic",            "sentiment":"🔴 Risk",     "territory":"USA",          "source":"HealthE1 Medical — healthe1.com; Atlantis Bioscience regulatory roadmap Oct 2025"},
        {"date":"Late 2025",   "type":"Regulatory",  "event":"ANVISA-COFEPRIS MoU fully operational",                     "impact":"Single approval pathway for Brazil and Mexico",                 "sentiment":"🟢 Positive", "territory":"LATAM",        "source":"DIA Global Forum, Nov 2025 — globalforum.diaglobal.org/issue/november-2025/anvisa-cofepris-strategy-and-vision"},
        {"date":"Feb 2025",    "type":"Investment",  "event":"ExoLab Italia raises EU5M Series A (plant-derived)",        "impact":"Plant-derived trend in EU; BM-MSC must emphasize superiority", "sentiment":"🟡 Neutral",  "territory":"EU",           "source":"ExoLab Italia press release, Feb 2025 (industry news)"},
        {"date":"Jan 2025",    "type":"Regulatory",  "event":"Thai FDA drafting new health product import/export policy", "impact":"Favourable regulatory window to enter Thailand now",            "sentiment":"🟢 Positive", "territory":"Thailand",     "source":"NutraIngredients, Jan 2025; ClinRegs Thailand Aug 2025 — clinregs.niaid.nih.gov"},
        {"date":"Mar 2024",    "type":"Partnership", "event":"Croma-Pharma x Aesthetic Management Partners (EU)",         "impact":"DACH region actively seeking new regenerative brands",          "sentiment":"🟢 Positive", "territory":"EU",           "source":"Croma-Pharma press release, Mar 2024 (industry news)"},
        {"date":"Ongoing 2025","type":"Enforcement", "event":"FDA: 12+ warning letters total on exosome products",        "impact":"US market = cosmetic channel only for next 3-5 years",          "sentiment":"🔴 Risk",     "territory":"USA",          "source":"Atlantis Bioscience Oct 2025 — FDA warning letter database; FDA Public Safety Notification on Exosome Products"},
        {"date":"Jul 2023",    "type":"M&A",         "event":"ExoCoBio acquires majority stake in US BENEV",              "impact":"Market consolidating; window to establish brand now",           "sentiment":"🟢 Positive", "territory":"USA",          "source":"ExoCoBio / BENEV press release, Jul 2023 (industry news)"},
        {"date":"2021",        "type":"Regulatory",  "event":"Thai FDA launches HSA Singapore Reliance Route",            "impact":"Singapore approval fast-tracks SEA/Thailand entry",             "sentiment":"🟢 Positive", "territory":"Thailand/SEA", "source":"HSA Singapore — hsa.gov.sg/cosmetic-products/asean-cosmetic-directive; Asia Actual Thailand guide"},
        {"date":"Ongoing",     "type":"Structural",  "event":"Lyophilisation segment $50-60M growing to $100M+ by 2030", "impact":"Cold-chain barrier eliminated globally",                        "sentiment":"🟢 Positive", "territory":"Global",       "source":"QY Research — Exosome Lyophilization Global Market Forecast 2026–2032"},
        {"date":"2024–2025",   "type":"Geographic",  "event":"CEE (Poland, Romania, Czech Republic) emerges as medical tourism hub for exosome aesthetics", "impact":"Romania $300.9M cosmetic surgery; Poland LaserMe+ASCE+ ~$500/session; Prague ~$320/session", "sentiment":"🟢 Positive", "territory":"CEE", "source":"Strategic reconciliation report 2026; Romanian cosmetic surgery market data; Polish aesthetic medicine estimates"},
        {"date":"Active",      "type":"Regulatory",  "event":"Florida Statute §456.47 — structured elective pathway for non-FDA-approved exosome use", "impact":"FL medspa market $1.2B (2024) → $2.5B (2034); South FL $199.51M → $1.09B by 2033 at 20.69% CAGR", "sentiment":"🟢 Positive", "territory":"USA — Florida", "source":"Strategic reconciliation report 2026; Florida medical spa market data"},
        {"date":"Active",      "type":"Regulatory",  "event":"Nevada SB128 + AB148 — licensed physicians may perform non-FDA-approved cell therapies", "impact":"Las Vegas established as destination hub for exosome anti-aging / performance protocols", "sentiment":"🟢 Positive", "territory":"USA — Nevada", "source":"Strategic reconciliation report 2026; Nevada state legislation"},
    ])

    # ── Merge live + static ───────────────────────────────────────
    if live_signals is not None and not live_signals.empty:
        ls = live_signals.copy()
        ls.columns = [c.lower().strip() for c in ls.columns]
        combined = pd.concat([ls, STATIC_SIGNALS], ignore_index=True)
        combined = combined.drop_duplicates(subset=["event"], keep="first")
        signals  = combined
        live_badge(True, last_run)
    else:
        signals = STATIC_SIGNALS
        live_badge(False, last_run)

    # Ensure column names are capitalised for display
    signals_display = signals.rename(columns={
        "date":"Date","type":"Type","event":"Event",
        "impact":"Impact","sentiment":"Sentiment","territory":"Territory",
        "source":"Source",
    })

    col_sm = st.columns(4)
    col_sm[0].metric("🟢 Positive Signals", len(signals_display[signals_display["Sentiment"].str.contains("Positive", na=False)]))
    col_sm[1].metric("🔴 Risk Signals",     len(signals_display[signals_display["Sentiment"].str.contains("Risk",     na=False)]))
    col_sm[2].metric("🟡 Neutral/Watch",    len(signals_display[signals_display["Sentiment"].str.contains("Neutral",  na=False)]))
    col_sm[3].metric("📋 Total Tracked",    len(signals_display))

    type_filter = st.multiselect(
        "Filter by Signal Type",
        options=sorted(signals_display["Type"].dropna().unique().tolist()),
        default=sorted(signals_display["Type"].dropna().unique().tolist()),
    )

    display_cols = [c for c in ["Date","Type","Event","Impact","Sentiment","Territory","Source"] if c in signals_display.columns]
    st.dataframe(
        signals_display[signals_display["Type"].isin(type_filter)][display_cols],
        hide_index=True, use_container_width=True, height=320,
    )
    st.caption("Source column shows citation for manually curated baseline signals. Auto-fetched signals include source URL from Google News RSS.")

    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.markdown('<div class="section-header">Signal Distribution</div>', unsafe_allow_html=True)
        sig_cnt = signals_display["Type"].value_counts().reset_index()
        sig_cnt.columns = ["Type", "Count"]
        fig_sig = px.bar(
            sig_cnt.sort_values("Count"), x="Count", y="Type", orientation="h",
            color="Count", color_continuous_scale=["#b3dff0","#1e3a5f"], text="Count",
        )
        fig_sig.update_traces(textposition="outside")
        fig_sig.update_layout(
            showlegend=False, height=280, margin=dict(t=10, b=10),
            coloraxis_showscale=False, xaxis_title="Number of Signals", yaxis_title="",
        )
        st.plotly_chart(fig_sig, use_container_width=True)


    with col_t2:
        st.markdown('<div class="section-header">Emerging Trends (2025–2030)</div>', unsafe_allow_html=True)
        trends = [
            ("❄️ Lyophilisation", "Eliminates cold-chain barrier for LATAM/SEA/ME. $50–60M segment growing to hundreds of millions by early 2030s."),
            ("🔬 Particle-Count Standardisation", "Distributors now demand NTA-verified particle counts with CoA. Non-negotiable for serious buyers."),
            ("🧬 BM-MSC vs UC-MSC Differentiation", "Buyers maturing — seeking source differentiation. BM-MSC carries deepest orthopedic/neuroprotective evidence base."),
            ("🤖 AI Exosome Profiling", "ML-integrated characterization accelerating biomarker discovery. Cargo profiles (miRNA, protein markers) command premium."),
            ("🌏 Thailand & SEA Medical Tourism", "Post-COVID recovery accelerating. High-value patients from US, EU, Middle East returning to Thailand/Singapore."),
            ("💊 COGS Collapse", "$2,500/dose (2026) → $500/dose (2030) — enter now before commoditization compresses margins."),
            ("🌿 Plant-Derived Exosomes", "EU investor interest rising as lower-risk cosmetic entry point — BM-MSC must actively counter with clinical evidence."),
            ("💉 Sexual Wellness Niche", "Vaginal rejuvenation + erectile function — high-demand in Dubai, Australia, and Thailand."),
        ]
        for icon_label, text in trends:
            st.markdown(f'<div class="signal-card"><strong>{icon_label}</strong> — {text}</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════
# TAB 7 — STRATEGY CHECKLIST
# ════════════════════════════════════════════════════════════════
with tabs[6]:
    st.markdown('<div class="section-header">Strategic Entry Checklist for BM-MSC Exosome Manufacturer</div>', unsafe_allow_html=True)

    checklist = [
        ("CRITICAL", "critical-card", "Obtain NTA-verified CoA",
         "Batch-level Certificate of Analysis with particle count, size distribution, and CD63/CD81/CD73/CD90 markers. Required by all serious distributors globally."),
        ("CRITICAL", "critical-card", "No therapeutic claims on cosmetic-grade products",
         "Comply with FDA/EU labeling enforcement. Any therapeutic claim on a cosmetic channel product risks immediate warning letter and market access loss."),
        ("HIGH",     "warning-card",  "Develop lyophilized format",
         "Opens Thailand, Philippines, Brazil, Mexico channels. Adds ~$150–250/dose cost but eliminates cold-chain barrier and significantly increases distributor appeal."),
        ("HIGH",     "warning-card",  "Obtain Philippine FDA cosmetic notification",
         "Use as ASEAN compliance signal. Jan 2026 UnicoCell approval validates the blueprint for TH, MY, and ID market entry."),
        ("HIGH",     "warning-card",  "Prepare Free Sale Certificate from country of origin",
         "Required for all Thai FDA imports of regulated products. Essential for Thailand entry."),
        ("HIGH",     "warning-card",  "Use ANVISA-COFEPRIS MoU for dual LATAM entry",
         "Register in one territory → gain reliance in the other. Cuts LATAM regulatory timeline by 40–60%."),
        ("HIGH",     "warning-card",  "Position BM-MSC vs UC-MSC clinical literature",
         "Orthopedic, neuroprotective, and wound-healing evidence base justifies 15–25% price premium to distributors."),
        ("MEDIUM",   "signal-card",   "Tiered distributor pricing with volume thresholds",
         "50/200/500+ vial tiers with cumulative discounts. Increases distributor commitment and stocking forecasting."),
        ("MEDIUM",   "signal-card",   "Engage HSA Singapore approval as ASEAN gateway",
         "Thai FDA reliance route (2021) recognizes HSA clearance. Fastest path to multiple ASEAN markets simultaneously."),
        ("MEDIUM",   "signal-card",   "Target DUBIMED (UAE) and Croma-Pharma (EU) as anchor distributors",
         "Both actively seeking new regenerative brands. DUBIMED: 40-year exclusive relationships; Croma-Pharma: signed new distribution deal Mar 2024."),
        ("MEDIUM",   "signal-card",   "US strategy: cosmetic topical + CDMO only",
         "OEM/white-label for medspas and post-laser protocols. Consider GMP supply to clinical-stage US biotech for Phase I/II trials."),
        ("MEDIUM",   "signal-card",   "US strategy: Florida + Nevada state-permissive model",
         "Florida §456.47 provides structured informed-consent pathway for elective physician use. Nevada SB128/AB148 similarly permits licensed physician use. Direct-to-clinic in FL/NV medspas captures the $1.2B Florida medspa market while remaining federally compliant — no therapeutic claims."),
        ("MEDIUM",   "signal-card",   "CEE (Poland, Romania, Czech Republic) as high-volume entry channel",
         "Target Teoxane Polska (already EPICEXOSOME distributor) and Romanian aesthetic distributors. CEE session prices ($320–800) vs US ($4,900) drive volume. Romania's $300.9M cosmetic surgery market attracts W. European medical tourists. LaserMe+ASCE+ Poland protocol active at ~$500/session."),
        ("MEDIUM",   "signal-card",   "Thailand: appoint local licensed importer",
         "All imports require locally registered Thai entity holding import license. Foreign manufacturers must appoint local representative."),
    ]

    priority_colors = {"CRITICAL": "#c62828", "HIGH": "#e05c2a", "MEDIUM": "#f0a030"}

    for priority, css_class, title, detail in checklist:
        color = priority_colors[priority]
        st.markdown(
            f'<div class="{css_class}">'
            f'<span style="background:{color};color:#fff;border-radius:4px;padding:2px 8px;font-size:.72rem;font-weight:700;margin-right:8px;">{priority}</span>'
            f'<strong>{title}</strong><br>'
            f'<span style="font-size:.88rem;">{detail}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    # ── Radar / priority overview ────────────────────────────────
    st.markdown("")
    st.markdown('<div class="section-header">Priority Summary</div>', unsafe_allow_html=True)
    pri_counts = {"CRITICAL": sum(1 for p, *_ in checklist if p=="CRITICAL"),
                  "HIGH":     sum(1 for p, *_ in checklist if p=="HIGH"),
                  "MEDIUM":   sum(1 for p, *_ in checklist if p=="MEDIUM")}
    fig_pri = px.bar(
        x=list(pri_counts.keys()), y=list(pri_counts.values()),
        color=list(pri_counts.keys()),
        color_discrete_map={"CRITICAL":"#c62828","HIGH":"#e05c2a","MEDIUM":"#f0a030"},
        text=list(pri_counts.values()),
    )
    fig_pri.update_traces(textposition="outside")
    fig_pri.update_layout(
        showlegend=False, height=220, margin=dict(t=10, b=10),
        xaxis_title="Priority Level", yaxis_title="Number of Actions",
    )
    st.plotly_chart(fig_pri, use_container_width=True)

# ── Footer ──────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    f"""<div style="text-align:center;color:#888;font-size:.78rem;padding:4px 0 12px;">
    🧬 Global Naive MSC Exosome Market Dashboard &nbsp;·&nbsp; Strategic Intelligence Edition {REPORT_DATE} &nbsp;·&nbsp; {DATA_VERSION}
    &nbsp;·&nbsp; Sources: InsightAce Analytic · Credence Research · CMI · TMR · FMI · DelveInsight · Astute Analytica · RoosterBio · Atlantis Bioscience · Jolifill.de · HUK Aesthetics · Bookimed · DIA Global Forum · FDA.gov · TGA.gov.au · HSA Singapore · PH FDA · Florida Statute §456.47 · Nevada SB128/AB148
    <br>⚠️ Market figures are summary-level intelligence only. Regulatory guidance is not legal advice. Consult qualified regulatory counsel before commercial launch.
    </div>""",
    unsafe_allow_html=True,
)

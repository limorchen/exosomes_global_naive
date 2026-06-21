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
def load_meta():
    df, err = load_csv("meta.csv")
    if err or df is None:
        return "Not yet run", ""
    last_run_row  = df[df["key"] == "last_run"]
    prev_run_row  = df[df["key"] == "prev_last_run"]
    last_run  = last_run_row["value"].values[0]  if not last_run_row.empty  else "Unknown"
    prev_run  = prev_run_row["value"].values[0]  if not prev_run_row.empty  else ""
    return last_run, prev_run

def load_last_run():
    last_run, _ = load_meta()
    return last_run

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
last_run, prev_last_run         = load_meta()

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
  .badge-new      { background:#7c3aed; color:#fff; border-radius:4px; padding:2px 7px; font-size:.75rem; font-weight:700; letter-spacing:.3px; }

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
    "<strong>wellness, aesthetics &amp; cosmeceutical channel — triangulated at ~$150M (2024)</strong> "
    "from 5 independent sources ($81M–$218M range), growing at 17–36% CAGR depending on scope. "
    "Secondary opportunity in soft indications via physician-dispensed channels in permissive jurisdictions "
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
    st.markdown('<div class="section-header">Global Market KPIs — Triangulated from 5 Independent Sources</div>', unsafe_allow_html=True)

    kpis = [
        ("$81M–$218M", "2024 Addressable Market",    "Professional/clinical channel — 5-source range"),
        ("~$150M",     "2024 Midpoint Estimate",      "Triangulated from InsightAce + Insight Partners"),
        ("17–36%",     "CAGR Range Across Sources",   "CMI 9.9% → InsightAce 35.9%"),
        ("$155–315",   "BM-MSC COGS/Dose (2026)",     "Commercial mid scale · Per 10B-particle dose · S1+G2"),
        ("$418M–$852M","Broader Skincare Market 2025","Incl. retail serums, creams, DTC"),
        ("$218M",      "Insight Partners 2024",       "Most specifically scoped to aesthetics"),
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
        st.markdown('<div class="section-header">Market Size Synthesis — 5 Independent Sources</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="signal-card">📊 <strong>Why sources disagree:</strong> Each measures a different slice of the market. '
            "A BM-MSC exosome vial manufacturer competes in the <strong>professional/clinical channel</strong> — "
            "not the retail serum or DTC cosmetic space. The relevant range is therefore "
            "<strong>$81M–$218M (2024)</strong>, with a triangulated midpoint of ~$150M. "
            "The $418M–$852M figures include retail skincare serums sold to consumers — "
            "revenue a bulk vial supplier does not capture directly.</div>",
            unsafe_allow_html=True,
        )
        st.markdown("")

        recon_df = pd.DataFrame([
            {"Research Firm":"The Insight Partners",    "Segment":"Aesthetic Exosomes (clinical)",          "2024/25 Value":"$218.3M (2024)", "2031/35 Forecast":"$669.9M (2031)", "CAGR":"17.4%","Scope":"Skin rejuvenation, post-procedure, hair restoration — clinical/medspa channel", "Relevant?":"✅ HIGH — closest scope"},
            {"Research Firm":"InsightAce Analytic",     "Segment":"Regen Aesthetics Exosomes",              "2024/25 Value":"$81.1M (2024)",  "2031/35 Forecast":"$1.69B (2034)",  "CAGR":"35.9%","Scope":"Regen aesthetics exosome products specifically", "Relevant?":"✅ HIGH — narrowly scoped"},
            {"Research Firm":"Coherent Market Insights","Segment":"Exosomes Skincare (broad)",              "2024/25 Value":"$417.8M (2025)", "2031/35 Forecast":"$809.5M (2032)", "CAGR":"9.9%", "Scope":"Serums, creams, masks, lotions — professional + retail", "Relevant?":"⚠️ PARTIAL — includes retail"},
            {"Research Firm":"Future Market Insights",  "Segment":"Exosome-Based Skincare",                 "2024/25 Value":"$852.3M (2025)", "2031/35 Forecast":"$3,952.7M (2035)","CAGR":"16.6%","Scope":"Full skincare incl. DTC consumer products, retail channels", "Relevant?":"⚠️ PARTIAL — broadest scope"},
            {"Research Firm":"BioInformant",            "Segment":"Exosome Cosmeceuticals",                 "2024/25 Value":"No hard figure", "2031/35 Forecast":"—",              "CAGR":"—",    "Scope":"Qualitative: hundreds of products in market; no FDA-approved; used by dermatologists, hair restoration, medspas", "Relevant?":"ℹ️ Qualitative context"},
            {"Research Firm":"Grand View Research",     "Segment":"Total Exosomes (all B2B)",               "2024/25 Value":"$177.4M (2024)", "2031/35 Forecast":"$794.2M (2030)", "CAGR":"28.7%","Scope":"All B2B: kits, reagents, isolation services — includes research/diagnostic", "Relevant?":"⚠️ PARTIAL — includes non-aesthetic"},
            {"Research Firm":"Precedence Research",     "Segment":"Exosome Therapy (full sector)",          "2024/25 Value":"$58,120M (2025)","2031/35 Forecast":"$307,040M (2035)","CAGR":"~35%","Scope":"Hospital labor + procedure fees + capital equipment — NOT product B2B", "Relevant?":"❌ NOT product market"},
        ])
        st.dataframe(recon_df, hide_index=True, use_container_width=True)
        st.markdown("")

        # ── Synthesis triangulation chart ─────────────────────────
        st.markdown('<div class="section-header">Triangulated Addressable Market — Professional Channel</div>', unsafe_allow_html=True)
        tri_df = pd.DataFrame({
            "Source":    ["InsightAce\n(Regen Aesthetics)", "The Insight Partners\n(Aesthetic Exosomes)", "Triangulated\nMidpoint"],
            "Low":       [81.1,  218.3, 81.1],
            "High":      [81.1,  218.3, 218.3],
            "Mid":       [81.1,  218.3, 149.7],
            "Type":      ["Source","Source","Synthesis"],
        })
        fig_tri = go.Figure()
        colors = {"Source":"#2e6da4","Synthesis":"#e05c2a"}
        for _, row in tri_df.iterrows():
            fig_tri.add_trace(go.Bar(
                x=[row["Source"]], y=[row["Mid"]],
                marker_color=colors[row["Type"]],
                text=f"${row['Mid']:.1f}M",
                textposition="outside",
                name=row["Type"],
                showlegend=False,
            ))
        fig_tri.add_hline(y=149.7, line_dash="dot", line_color="#e05c2a",
                          annotation_text="Triangulated midpoint ~$150M", annotation_position="top right")
        fig_tri.update_layout(
            height=300, margin=dict(t=20, b=10),
            yaxis_title="2024 Market Size (USD Million)",
            title="",
        )
        st.plotly_chart(fig_tri, use_container_width=True)
        st.caption("Orange = triangulated synthesis of two most specifically-scoped sources. Blue = individual source values. Broader retail market ($418M–$852M) excluded as it measures DTC consumer products, not B2B vial sales.")

        # ── Log-scale chart showing all sources ───────────────────
        st.markdown('<div class="section-header">All Sources — Full Range ($81M to $58B, log scale)</div>', unsafe_allow_html=True)
        recon_chart = pd.DataFrame({
            "Scope":  [
                "InsightAce\n(Regen Aesthetics)",
                "Insight Partners\n(Aesthetic Exosomes)",
                "Grand View\n(All Exosome B2B)",
                "CMI\n(Exosome Skincare)",
                "FMI\n(Exosome Skincare broad)",
                "Precedence\n(Therapy sector total)",
            ],
            "Value":  [81.1, 218.3, 177.4, 417.8, 852.3, 58120],
            "Type":   ["Clinical channel","Clinical channel","B2B broad","Retail incl.","Retail incl.","Service sector"],
        })
        fig_recon = px.bar(
            recon_chart, x="Scope", y="Value",
            color="Type",
            color_discrete_map={
                "Clinical channel": "#1e3a5f",
                "B2B broad":        "#2e6da4",
                "Retail incl.":     "#f0a030",
                "Service sector":   "#e05c2a",
            },
            text="Value",
            log_y=True,
            title="All market size estimates — log scale (dark blue = relevant to manufacturer)",
        )
        fig_recon.update_traces(texttemplate="%{text:,.0f}M", textposition="outside")
        fig_recon.update_layout(
            height=420, margin=dict(t=20, b=120), showlegend=True,
            yaxis_title="USD Million (log scale)", xaxis_title="",
            title="",
            legend=dict(orientation="h", yanchor="top", y=-0.28, xanchor="center", x=0.5, font=dict(size=9)),
        )
        st.plotly_chart(fig_recon, use_container_width=True)
        st.caption("Log scale required — values span $81M to $58,000M. Dark blue bars are the most relevant to a clinical-grade vial manufacturer. Each bar measures a different economic concept.")

        st.markdown('<div class="section-header">Addressable Market by Region (2024)</div>', unsafe_allow_html=True)
        st.caption("Regional figures scaled proportionally from triangulated $150M midpoint (InsightAce $81.1M + Insight Partners $218.3M). Regional shares: Credence Research 2025 (NA 45%, APAC 25%, Europe 20%). Sub-regional splits are author estimates.")
        addr_df = pd.DataFrame({
            "Region":    ["North America", "Europe (W)", "Rest of APAC*", "Southeast Asia", "CEE (PL/RO/CZ)", "Latin America", "UAE/GCC", "Thailand", "Australia", "Rest of World"],
            "2024 ($M)": [58,   25,   22,   12,   5,    8,    8,    5,    3,    4],
            "2030 ($M)": [206,  72,   93,   50,   16,   25,   30,   21,   9,    8],
            "CAGR":      ["23%","19%","27%","27%","22%","21%","24%","27%","20%","12%"],
            "Source":    [
                "45% of $150M triangulated midpoint; Credence, InsightAce, CMI confirm NA leading region",
                "20% of $150M; Credence 20% share; Dataintelo 25% share; market.us data",
                "Part of APAC 25% share; FMI: China 23.1% CAGR, Korea ExoCoBio 9.6% share",
                "ASEAN subset of APAC; PH FDA Jan 2026 gateway",
                "Romania $300.9M cosmetic surgery; Poland $4.8M est.; CEE CAGR 10.1%",
                "Credence: LATAM = 4.5% of $418M broader total; ANVISA-COFEPRIS MoU Aug 2025",
                "MEA subset; GloGrowthInsights MEA ~12% of broader market; UAE premium sub-segment",
                "Medical tourism hub; Thai FDA modernising; author estimate within APAC",
                "TGA-restricted; regenerative protocols only; author estimate within APAC",
                "Residual emerging markets",
            ],
        })
        st.markdown(
            '<div class="signal-card">📊 <strong>Total addressable market (professional/clinical channel): ~$150M (2024)</strong> — '
            "triangulated from InsightAce $81.1M (regen aesthetics) and The Insight Partners $218.3M (aesthetic exosomes clinical). "
            "Broader exosome skincare market including retail DTC: $418M–$852M (CMI, FMI) — "
            "this is not the addressable market for a B2B vial manufacturer.</div>",
            unsafe_allow_html=True,
        )
        st.markdown("")
        # Note: Rest of APAC includes Korea, Japan, China (not separately tracked in dashboard)
        fig_addr = px.bar(
            addr_df, x="Region", y=["2024 ($M)", "2030 ($M)"],
            barmode="group",
            color_discrete_sequence=["#2e6da4", "#7ec8e3"],
            title="Addressable Market: 2024 vs 2030 Forecast by Region ($M)",
            text_auto=".1f",
        )
        fig_addr.update_layout(height=340, margin=dict(t=20, b=10), legend_title="",
                                xaxis_tickangle=-35, yaxis_title="USD Million",
                                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
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
        fig_pie.update_traces(
            textposition="inside",
            textinfo="percent",
            insidetextorientation="radial",
            pull=[0.03]*10,
        )
        fig_pie.update_layout(
            margin=dict(t=10, l=10, r=160, b=10),
            showlegend=True,
            height=480,
            legend=dict(
                orientation="v",
                yanchor="top", y=1.0,
                xanchor="left", x=1.01,
                font=dict(size=10),
                tracegroupgap=2,
            ),
        )
        st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown('<div class="section-header">CAGR by Region</div>', unsafe_allow_html=True)
        cagr_df = addr_df.copy()
        cagr_df["CAGR_num"] = [23, 19, 27, 27, 22, 21, 24, 27, 20, 12]
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
        ("The Insight Partners", "Aesthetic Exosomes Market to 2031, Dec 2025 (TIPRE00041701)", "$218.3M (2024) → $669.9M (2031); CAGR 17.4%; clinical/medspa channel; North America dominant; APAC fastest-growing"),
        ("InsightAce Analytic", "Regenerative Aesthetics Exosome Products Market, Nov 2025", "$81.1M (2024); CAGR 35.9% (2025–2034); North America leading region; regen aesthetics specifically"),
        ("Coherent Market Insights", "Exosomes Skincare Market Size, Share and Forecast 2025–2032 (CMI7649)", "$417.8M (2025) → $809.5M (2032); CAGR 9.9%; NA 38.7%; APAC 32.0%; serums 42.6% of market; human-derived 35.6%"),
        ("Future Market Insights", "Exosome-Based Skincare Market 2025–2035, Sep 2025", "$852.3M (2025) → $3,952.7M (2035); CAGR 16.6%; anti-aging 53.5% share; $1,835.5M by 2030"),
        ("BioInformant", "The Rise of Exosome-Based Cosmeceuticals in 2026, Oct 2025", "Qualitative industry overview; hundreds of products in market; no FDA-approved products; professional use by dermatologists, hair restoration, medspas"),
        ("Grand View Research", "Exosomes Market Size and Share — Industry Report 2030, 2024", "$177.4M total exosome market (2024); $794.2M forecast (2030); B2B kits/reagents/isolation; all segments"),
        ("Precedence Research", "Exosome Therapeutics Market Size 2025–2034, Nov 2025", "$58.12B Exosome Therapy sector (2025) including procedure fees and hospital labor — service sector total, not product B2B"),
        ("DelveInsight", "Exosome Diagnostics Market Insights and Forecast 2034, 2025", "$119.3M diagnostics (2024); $2.56B (2032); IVD channel only"),
        ("Transparency Market Research", "Exosome Market for Cosmetic Applications, 2024", "$1.8B cosmetic applications (2024); $26.6B (2035); includes retail cosmeceuticals"),
        ("Statifacts / Precedence Research", "U.S. Exosome-Based Therapy Market, 2025", "$15.61M U.S.-specific therapeutic service revenues (2024); $79.67M (2034)"),
        ("Credence Research", "Exosomes Skincare Market Size, Share and Growth Report 2032", "Regional shares: NA 45%, APAC 25%, Europe 20%, LATAM $18.67M of $418M total"),
        ("Silva et al. 2025 / RoosterBio 2022+2025 / Ng et al. 2019", "COGS benchmarks — open-access peer-reviewed sources (PMC11913891, PMC6322973, PMC7552727)", "Research scale $6,800–12,100/10B (S3/S5); BM-MSC commercial mid $155–315/10B (S1+G2); Industrial $58–125/10B (extrapolated S2). Component splits: EV harvest >50% of COG (S2)."),
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
    # ── Choropleth world map ─────────────────────────────────────
    st.markdown('<div class="section-header">🗺️ Global Entry Map — Regulatory Risk by Country (B2B Cosmetic / Soft Medical Channel)</div>', unsafe_allow_html=True)
    st.caption(
        "Risk rating = regulatory risk for **non-IND, non-therapeutic** naive MSC exosome products "
        "(topical cosmetic, physician-dispensed aesthetic, soft medical use). "
        "⚠️ IV/injectable therapeutic use carries higher risk in all markets regardless of color shown here. "
        "Bubble size = 2030 market forecast (USD million)."
    )

    choropleth_df = pd.DataFrame([
        # USA: FDA 12+ warning letters target IV/injectable/drug-claim products ONLY.
        # Topical B2B cosmetic (no drug claims) operates legally — AnteAGE, BENEV, Stem Nova all active.
        # Risk for B2B cosmetic channel: MEDIUM (claims compliance required; IV = 🔴).
        {"Country":"United States",    "ISO":"USA","Risk":"Medium",  "Risk_Num":3,"2030_M":206,"Channel":"Cosmetic/topical B2B active; IV = 🔴 enforcement; no drug claims","Flag":"🇺🇸"},
        # Australia: TGA applies only when therapeutic claims are made.
        # Topical cosmetics regulated by ACCC (consumer law), not TGA.
        # Practitioner aesthetic channel active. Risk for B2B cosmetic: MEDIUM.
        {"Country":"Australia",        "ISO":"AUS","Risk":"Medium",  "Risk_Num":3,"2030_M":9,  "Channel":"Cosmetic = ACCC (not TGA); aesthetic practitioner channel active; IV = TGA-restricted","Flag":"🇦🇺"},
        # EU: Cosmetics Regulation EC 1223/2009 — clear pathway: notification + safety assessment + responsible person.
        {"Country":"Germany",          "ISO":"DEU","Risk":"Low-Med", "Risk_Num":2,"2030_M":18, "Channel":"EU Cosmetics Reg 1223/2009 — notification pathway; medical spa channel active","Flag":"🇩🇪"},
        {"Country":"France",           "ISO":"FRA","Risk":"Low-Med", "Risk_Num":2,"2030_M":14, "Channel":"EU Cosmetics Reg — notification pathway; dermatology / aesthetics active","Flag":"🇫🇷"},
        {"Country":"Switzerland",      "ISO":"CHE","Risk":"Medium",  "Risk_Num":3,"2030_M":5,  "Channel":"Cosmetic compliant; longevity clinics (private); Swissmedic for therapeutic","Flag":"🇨🇭"},
        {"Country":"Brazil",           "ISO":"BRA","Risk":"Medium",  "Risk_Num":3,"2030_M":12, "Channel":"ANVISA RDC 949/2024 notification pathway; IOR required for import","Flag":"🇧🇷"},
        # South Korea: 'exosome' term banned in cosmetic ads Jan 2025 — terminology compliance required.
        {"Country":"South Korea",      "ISO":"KOR","Risk":"Medium",  "Risk_Num":3,"2030_M":35, "Channel":"K-beauty cosmetic active; 'exosome' ad term banned Jan 2025 — rebranding needed","Flag":"🇰🇷"},
        {"Country":"United Arab Emirates","ISO":"ARE","Risk":"Low-Med","Risk_Num":2,"2030_M":30,"Channel":"Active IV longevity + cosmetic clinics; CE/FDA-cert devices accepted","Flag":"🇦🇪"},
        {"Country":"Mexico",           "ISO":"MEX","Risk":"Low",     "Risk_Num":1,"2030_M":13, "Channel":"Physician dispensing — active; COFEPRIS cosmetic compliant","Flag":"🇲🇽"},
        {"Country":"Thailand",         "ISO":"THA","Risk":"Low-Med", "Risk_Num":2,"2030_M":21, "Channel":"Cosmetic notification + physician grey area; no exosome-specific enforcement","Flag":"🇹🇭"},
        {"Country":"Philippines",      "ISO":"PHL","Risk":"Low",     "Risk_Num":1,"2030_M":8,  "Channel":"✅ ACD compliant; May 2026 enforcement deadline passed — clean channel","Flag":"🇵🇭"},
        {"Country":"Malaysia",         "ISO":"MYS","Risk":"Low",     "Risk_Num":1,"2030_M":5,  "Channel":"ASEAN cosmetic directive — compliant pathway","Flag":"🇲🇾"},
        {"Country":"Indonesia",        "ISO":"IDN","Risk":"Low",     "Risk_Num":1,"2030_M":5,  "Channel":"ASEAN cosmetic directive + BPOM pathway","Flag":"🇮🇩"},
        {"Country":"Singapore",        "ISO":"SGP","Risk":"Low-Med", "Risk_Num":2,"2030_M":8,  "Channel":"HSA: exosomes = therapeutic products; early engagement recommended","Flag":"🇸🇬"},
        {"Country":"Colombia",         "ISO":"COL","Risk":"Low",     "Risk_Num":1,"2030_M":4,  "Channel":"2025 LATAM reform — streamlined pathway","Flag":"🇨🇴"},
        {"Country":"Argentina",        "ISO":"ARG","Risk":"Low",     "Risk_Num":1,"2030_M":4,  "Channel":"2025 deregulation — fast-track entry","Flag":"🇦🇷"},
        {"Country":"Poland",           "ISO":"POL","Risk":"Low",     "Risk_Num":1,"2030_M":8,  "Channel":"CEE hub — LaserMe / Teoxane Polska; EU cosmetics framework","Flag":"🇵🇱"},
        {"Country":"Romania",          "ISO":"ROU","Risk":"Low",     "Risk_Num":1,"2030_M":5,  "Channel":"Medical tourism hub; $300M cos. surg.","Flag":"🇷🇴"},
        {"Country":"Czechia",          "ISO":"CZE","Risk":"Low",     "Risk_Num":1,"2030_M":4,  "Channel":"Clinical expansion in Prague",         "Flag":"🇨🇿"},
    ])
    choropleth_df["Risk_Label"] = choropleth_df["Risk"].map({
        "High":"🔴 High","Medium":"🟡 Medium","Low-Med":"🟡 Low-Med","Low":"🟢 Low",
    })

    risk_color_map = {"High":"#c62828","Medium":"#f0a030","Low-Med":"#a0c040","Low":"#3db07a"}
    choropleth_df["Color"] = choropleth_df["Risk"].map(risk_color_map)
    choropleth_df["Hover"] = (
        choropleth_df["Flag"] + " " + choropleth_df["Country"] +
        "<br>Risk: " + choropleth_df["Risk_Label"] +
        "<br>2030 market: $" + choropleth_df["2030_M"].astype(str) + "M" +
        "<br>Channel: " + choropleth_df["Channel"]
    )

    fig_choro = go.Figure()
    fig_choro.add_trace(go.Choropleth(
        locations=choropleth_df["ISO"],
        z=choropleth_df["Risk_Num"],
        text=choropleth_df["Hover"],
        hovertemplate="%{text}<extra></extra>",
        colorscale=[[0,"#3db07a"],[0.33,"#a0c040"],[0.66,"#f0a030"],[1,"#c62828"]],
        zmin=1, zmax=4,
        showscale=False,
        marker_line_color="#fff",
        marker_line_width=0.5,
    ))
    # Overlay bubble layer for tracked markets
    fig_choro.add_trace(go.Scattergeo(
        locations=choropleth_df["ISO"],
        mode="markers",
        marker=dict(
            size=choropleth_df["2030_M"] ** 0.5 * 2.2,
            color=choropleth_df["Color"],
            opacity=0.75,
            line=dict(color="#fff", width=1),
        ),
        text=choropleth_df["Hover"],
        hovertemplate="%{text}<extra></extra>",
        showlegend=False,
    ))
    fig_choro.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            coastlinecolor="#ccc",
            projection_type="natural earth",
            bgcolor="#f7f9fc",
            landcolor="#f0f4f8",
            oceancolor="#e8f4f8",
            showocean=True,
            showlakes=False,
            lakecolor="#e8f4f8",
        ),
        height=420,
        margin=dict(t=10, b=10, l=0, r=0),
        paper_bgcolor="#f7f9fc",
    )
    st.plotly_chart(fig_choro, use_container_width=True)

    # Legend for the choropleth
    leg_cols = st.columns(4)
    for col, (risk, color, desc) in zip(leg_cols, [
        ("🔴 High",     "#c62828", "IV/injectable therapeutic only — cosmetic channel not established"),
        ("🟡 Medium",   "#f0a030", "Cosmetic B2B viable with claims compliance / terminology care"),
        ("🟡 Low-Med",  "#a0c040", "Clear cosmetic pathway + active physician soft-indication channel"),
        ("🟢 Low",      "#3db07a", "Permissive — cosmetic notification; physician dispensing active"),
    ]):
        col.markdown(
            f'<div style="border-left:4px solid {color};background:#fff;padding:6px 10px;'
            f'border-radius:4px;font-size:.78rem;"><strong>{risk}</strong><br>{desc}</div>',
            unsafe_allow_html=True,
        )
    st.markdown("")

    # ── Sortable country table with quick reference ────────────────
    st.markdown('<div class="section-header">Country Quick-Reference</div>', unsafe_allow_html=True)
    choro_display = choropleth_df[["Flag","Country","Risk_Label","2030_M","Channel"]].copy()
    choro_display.columns = ["","Country","Reg. Risk","2030 Forecast ($M)","Channel / Entry Status"]
    choro_display = choro_display.sort_values("2030 Forecast ($M)", ascending=False)
    st.dataframe(choro_display, hide_index=True, use_container_width=True, height=300)
    st.markdown("")

    st.markdown('<div class="section-header">Market Opportunity vs Regulatory Risk (All Regions)</div>', unsafe_allow_html=True)
    st.markdown("")

    geo_df = pd.DataFrame([
        {"Region":"North America", "Stage":"Active",        "Segment":"Cosmetic / Aesthetic",  "Reg Risk":"Medium", "CAGR":23,"OOP":False,"2024 ($M)":58,  "2030 ($M)":206, "Note":"Largest market — topical B2B active (AnteAGE, BENEV, Stem Nova); IV = 🔴; FL medspa $1.2B; Nevada SB128/AB148"},
        {"Region":"Europe (W)",    "Stage":"Established",   "Segment":"Aesthetic/Wellness",   "Reg Risk":"Medium", "CAGR":19,"OOP":True, "2024 ($M)":25,  "2030 ($M)":72,  "Note":"20% regional share (Credence); Germany, France, Italy lead"},
        {"Region":"CEE",           "Stage":"Emerging",      "Segment":"Medical Tourism Hub",  "Reg Risk":"Low",    "CAGR":22,"OOP":True, "2024 ($M)":5,   "2030 ($M)":16,  "Note":"Romania $300.9M cosmetic surgery; Poland $4.8M; Prague sessions ~$320"},
        {"Region":"Rest of APAC",  "Stage":"Emerging",      "Segment":"K-Beauty/Hospital",    "Reg Risk":"Medium", "CAGR":27,"OOP":True, "2024 ($M)":22,  "2030 ($M)":93,  "Note":"Korea ExoCoBio 9.6% share; China 23.1% CAGR (FMI)"},
        {"Region":"Southeast Asia","Stage":"Emerging",      "Segment":"K-Beauty/Aesthetic",   "Reg Risk":"Low",    "CAGR":27,"OOP":True, "2024 ($M)":12,  "2030 ($M)":50,  "Note":"ASEAN gateway; PH FDA Jan 2026 approved"},
        {"Region":"Latin America", "Stage":"Growing",       "Segment":"Medical Tourism",      "Reg Risk":"Medium", "CAGR":21,"OOP":True, "2024 ($M)":8,   "2030 ($M)":25,  "Note":"4.5% of broader market (Credence); ANVISA-COFEPRIS MoU Aug 2025"},
        {"Region":"UAE/GCC",       "Stage":"Niche/Premium", "Segment":"Longevity/Luxury",     "Reg Risk":"Low-Med","CAGR":24,"OOP":True, "2024 ($M)":8,   "2030 ($M)":30,  "Note":"Premium MEA subset; luxury longevity channel"},
        {"Region":"Thailand",      "Stage":"Emerging",      "Segment":"Medical Tourism",      "Reg Risk":"Low-Med","CAGR":27,"OOP":True, "2024 ($M)":5,   "2030 ($M)":21,  "Note":"Medical tourism hub; Thai FDA modernising 2025"},
        {"Region":"Australia",     "Stage":"Established",   "Segment":"Cosmetic / Aesthetic",  "Reg Risk":"Medium", "CAGR":20,"OOP":False,"2024 ($M)":3,   "2030 ($M)":9,   "Note":"Cosmetic = ACCC not TGA; practitioner aesthetic channel active; IV/therapeutic = TGA-restricted"},
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

        st.markdown('<div class="section-header">🇺🇸 US State-Permissive Markets — Florida, Nevada & Utah</div>', unsafe_allow_html=True)
        us_state_df = pd.DataFrame([
            {"State":"Florida",                   "Market":"Medspa (statewide 2024)","Size":"$1.2B",  "2034 Forecast":"$2.5B",  "CAGR":"7.8%",   "Key Legislation":"FL Statute §456.47 — informed consent; structured elective pathway for ALL exosome products"},
            {"State":"Florida — South FL cluster","Market":"Miami-Dade/Broward/Palm Beach","Size":"$199.5M","2033 Forecast":"$1.09B","CAGR":"20.69%","Key Legislation":"Same §456.47; highest concentration of exosome-ready medspas in US"},
            {"State":"Nevada",                    "Market":"Anti-aging / performance hub","Size":"Emerging","2034 Forecast":"High growth","CAGR":"est. 15%+","Key Legislation":"SB128 + AB148 — licensed physicians may perform non-FDA-approved cell-derived therapies"},
            {"State":"Utah",                      "Market":"Regenerative / wellness hub","Size":"Active","2034 Forecast":"Growing","CAGR":"est. 12%+","Key Legislation":"SB 199 (eff. May 1, 2024) — non-FDA-approved PLACENTAL/PERINATAL cell therapies with informed consent. ⚠️ BM-MSC not explicitly covered"},
        ])
        st.dataframe(us_state_df, hide_index=True, use_container_width=True)

        col_fl1, col_fl2 = st.columns(2)
        with col_fl1:
            st.markdown(
                '<div class="success-card">🌴 <strong>Florida §456.47 — Why it matters:</strong><br>'
                "Requires physicians to obtain informed consent advising patients that exosome products are not FDA-approved — "
                "but critically, it <em>creates</em> a structured, state-monitored pathway for elective clinical use. "
                "It does not prohibit use; it regulates it. Covers exosome products explicitly — broadest US state pathway for a BM-MSC supplier. "
                "South Florida's 20.69% CAGR medspa market is the most actionable US sub-market. "
                "Entry strategy: post-procedure recovery topical; no therapeutic claims.</div>",
                unsafe_allow_html=True,
            )
        with col_fl2:
            st.markdown(
                '<div class="success-card">🎰 <strong>Nevada SB128 + AB148 — Why it matters:</strong><br>'
                "Allows licensed physicians to perform non-FDA-approved cell-derived therapies. "
                "Las Vegas has established itself as a destination hub for exosome anti-aging and performance protocols. "
                "Average single session: <strong>$4,900 in Miami/Las Vegas</strong>; comprehensive plans up to <strong>$15,000</strong>. "
                "Entry strategy: direct-to-clinic premium positioning; performance and longevity angle; no therapeutic claims on labeling.</div>",
                unsafe_allow_html=True,
            )

        st.markdown(
            '<div class="warning-card">🏔️ <strong>Utah SB 199 (eff. May 1, 2024) — Partial opportunity for BM-MSC:</strong><br>'
            "Utah's law explicitly covers <strong>placental and perinatal</strong> cell therapies — not bone marrow-derived MSC exosomes. "
            "This is a critical distinction: BM-MSC exosomes are <em>not</em> explicitly protected under SB 199. "
            "The law creates an informed-consent pathway and requires provider disclosure that therapies are not FDA-approved. "
            "However, Utah has a thriving active clinic ecosystem (Utah Stem Cells, R3 Stem Cell SLC, Movement Clinic, The Stem Cell Club — St. George/Park City) "
            "with strong wellness culture and medical tourism from Park City luxury visitors. "
            "<strong>Strategy for BM-MSC:</strong> Utah cosmetic topical channel (same as all US states) is viable. "
            "IV/injection of BM-MSC exosomes does NOT benefit from SB 199 protection — higher federal enforcement risk vs Florida. "
            "Consider Utah as a <em>cosmetic topical + post-procedure</em> entry point, not an elective injection hub. "
            "Source: Utah SB 199 signed March 2024; Celmedica state guide; ipscell.com legal analysis Apr 2024.</div>",
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
        ("Utah SB 199", "Utah State Legislature — signed March 2024, eff. May 1 2024", "Non-FDA-approved placental/perinatal cell therapies permitted with informed consent. Does NOT explicitly cover BM-MSC exosomes"),
        ("Celmedica", "Stem Cell & Regenerative Medicine in Utah: What's Legal, 2024", "Active clinic ecosystem: Utah Stem Cells, R3 Stem Cell SLC, Movement Clinic, The Stem Cell Club (St. George/Park City)"),
        ("ipscell.com / Prof. Paul Knoepfler", "Utah set to legalize non-FDA-approved placental cell therapies, March 2024", "SB 199 creates FDA conflict; covers placental/perinatal only; exosome and BM-MSC sourcing not explicitly addressed"),
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
    st.markdown('<div class="section-header">Global Regulatory Framework — B2B Cosmetic & Soft Medical Channel (May 2026)</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="signal-card">📋 <strong>Channel context:</strong> Risk ratings reflect the <em>non-IND, non-therapeutic</em> channel — '
        'topical cosmetic B2B, physician-dispensed aesthetic, and soft medical (no drug claims). '
        'IV/injectable therapeutic use carries 🔴 HIGH risk in <em>all</em> markets regardless of overall rating shown. '
        'See the IV/Therapeutic column for territory-specific therapeutic risk.</div>',
        unsafe_allow_html=True,
    )

    reg_df_static = pd.DataFrame([
        {"Territory":"USA",         "Body":"FDA",          "Topical/Cosmetic":"✅ Active B2B market — no drug claims; AnteAGE/BENEV/Stem Nova operate legally","Soft Indications":"Physician discretion (grey); no IV drug claims","IV/Therapeutic":"🔴 IND required; 12+ warning letters; DOJ active — IV/injectable only","Risk":"🟡 MEDIUM",  "Conf.":"🟢 90","Source URL":"https://www.armstrongbradylyons.com/library/fda-warning-letters-exosome-product"},
        {"Territory":"EU",          "Body":"EMA",          "Topical/Cosmetic":"✅ EU Cosmetics Reg 1223/2009 — notification + safety assessment + responsible person","Soft Indications":"Cosmetic grade — dermatology, aesthetics active","IV/Therapeutic":"🔴 ATMP required — 0 exosome-based approved globally; EMA Jul 2025 guideline","Risk":"🟡 LOW-MED","Conf.":"🟢 85","Source URL":"https://www.regulatoryrapporteur.org/industry-news/ema-accepts-new-guidelines-on-investigational-atmps/843.article"},
        {"Territory":"Australia",   "Body":"TGA/ACCC",     "Topical/Cosmetic":"✅ Cosmetics = ACCC (consumer law), not TGA — no registration required","Soft Indications":"Practitioner aesthetic channel active — cosmetic claims only","IV/Therapeutic":"🔴 TGA-restricted; ATMP / PBAC risk-sharing model","Risk":"🟡 MEDIUM",  "Conf.":"🟢 80","Source URL":"https://www.atlantisbioscience.com/blog/commercialising-exosome-therapeutics-key-regulatory-pathways/"},
        {"Territory":"Germany",     "Body":"BfArM",        "Topical/Cosmetic":"✅ EU cosmetics notification — active medical spa market","Soft Indications":"Medical spa / aesthetic clinic channel active","IV/Therapeutic":"ATMP pathway; EMA Jul 2025 guideline applies","Risk":"🟡 LOW-MED","Conf.":"🟢 80","Source URL":"https://www.regulatoryrapporteur.org/industry-news/ema-accepts-new-guidelines-on-investigational-atmps/843.article"},
        {"Territory":"France",      "Body":"ANSM",         "Topical/Cosmetic":"✅ EU cosmetics notification — dermatology & aesthetics active","Soft Indications":"Dermatology protocols active","IV/Therapeutic":"ATMP pathway; EMA Jul 2025 guideline applies","Risk":"🟡 LOW-MED","Conf.":"🟢 80","Source URL":"https://www.regulatoryrapporteur.org/industry-news/ema-accepts-new-guidelines-on-investigational-atmps/843.article"},
        {"Territory":"Switzerland", "Body":"Swissmedic",   "Topical/Cosmetic":"High-value cosmetic",         "Soft Indications":"Longevity clinics (private)",     "IV/Therapeutic":"Clinical registration",            "Risk":"🟡 MEDIUM",  "Conf.":"🟢 70","Source URL":"https://www.atlantisbioscience.com/blog/commercialising-exosome-therapeutics-key-regulatory-pathways/"},
        {"Territory":"Brazil",      "Body":"ANVISA",       "Topical/Cosmetic":"RDC 949/2024 notification",  "Soft Indications":"IOR required",                    "IV/Therapeutic":"AFE license required",             "Risk":"🟡 MEDIUM",  "Conf.":"🟢 70","Source URL":"https://www.emergobyul.com/news/brazil-anvisa-announces-priorities-2026-2027-year"},
        {"Territory":"South Korea", "Body":"MFDS",         "Topical/Cosmetic":"K-beauty cosmetic framework","Soft Indications":"Hospital partnerships",           "IV/Therapeutic":"Clinical approval route",          "Risk":"🟡 MEDIUM",  "Conf.":"🟡 60","Source URL":"https://stylestory.com.au/blogs/podcast/why-korea-banned-exosome-skincare-ads-and-what-it-means-for-the-industry"},
        {"Territory":"UAE",         "Body":"MOHAP/DHA",    "Topical/Cosmetic":"CE/FDA-cert device",         "Soft Indications":"Clinic-based IV protocols — active","IV/Therapeutic":"Strict cosmetic procedure standards","Risk":"🟡 MEDIUM","Conf.":"🟡 65","Source URL":"https://www.atlantisbioscience.com/blog/commercialising-exosome-therapeutics-key-regulatory-pathways/"},
        {"Territory":"Mexico",      "Body":"COFEPRIS",     "Topical/Cosmetic":"Cosmetic compliant",          "Soft Indications":"Physician dispensing — active",   "IV/Therapeutic":"MoU reliance with ANVISA",         "Risk":"🟢 LOW",     "Conf.":"🟢 75","Source URL":"https://www.atlantisbioscience.com/blog/commercialising-exosome-therapeutics-key-regulatory-pathways/"},
        {"Territory":"Thailand",    "Body":"Thai FDA",     "Topical/Cosmetic":"Cosmetic notif. + post-audit","Soft Indications":"Gray — active physician use",     "IV/Therapeutic":"Drug Act B.E. 2510 — no explicit guideline","Risk":"🟡 LOW-MED","Conf.":"🟢 80","Source URL":"https://www.cirs-group.com/en/cosmetics/global-cosmetics-regulatory-updates-vol-32-october-2025"},
        {"Territory":"Philippines", "Body":"PH FDA",       "Topical/Cosmetic":"✅ Notif. approved Jan 2026", "Soft Indications":"ASEAN compliant",                 "IV/Therapeutic":"Emerging",                         "Risk":"🟢 LOW",     "Conf.":"🟢 80","Source URL":"https://www.fda.gov.ph/fda-circular-no-2025-002-updates-and-amendments-to-the-asean-cosmetic-directive-acd-as-adopted-during-the-39th-asean-cosmetic-committee-acc-meeting-and-its-related-meetings/"},
        {"Territory":"Malaysia",    "Body":"NPRA",         "Topical/Cosmetic":"ASEAN aligned",              "Soft Indications":"cGMP research active",             "IV/Therapeutic":"Early stage",                      "Risk":"🟢 LOW",     "Conf.":"🟢 75","Source URL":"https://www.atlantisbioscience.com/blog/commercialising-exosome-therapeutics-key-regulatory-pathways/"},
        {"Territory":"Indonesia",   "Body":"BPOM",         "Topical/Cosmetic":"ASEAN cosmetic directive",   "Soft Indications":"Physician training pathway",       "IV/Therapeutic":"BPOM engaged",                     "Risk":"🟢 LOW",     "Conf.":"🟢 70","Source URL":"https://www.atlantisbioscience.com/blog/commercialising-exosome-therapeutics-key-regulatory-pathways/"},
        {"Territory":"Colombia",    "Body":"INVIMA",       "Topical/Cosmetic":"2025 Regional Reform",       "Soft Indications":"LATAM integration",                "IV/Therapeutic":"Streamlined pathway",              "Risk":"🟢 LOW",     "Conf.":"🟡 60","Source URL":"https://www.atlantisbioscience.com/blog/commercialising-exosome-therapeutics-key-regulatory-pathways/"},
        {"Territory":"Argentina",   "Body":"ANMAT",        "Topical/Cosmetic":"2025 Deregulation",          "Soft Indications":"Fast-track entry",                 "IV/Therapeutic":"Streamlined",                      "Risk":"🟢 LOW",     "Conf.":"🟡 60","Source URL":"https://www.atlantisbioscience.com/blog/commercialising-exosome-therapeutics-key-regulatory-pathways/"},
    ])

    # ── Live data wiring ──────────────────────────────────────────
    reg_df, reg_is_live = get_live_or_static(live_regulatory, reg_df_static)
    # Normalise column names from CSV (may be lowercase/different case)
    if reg_is_live:
        col_map = {c.lower(): c for c in reg_df_static.columns}
        reg_df = reg_df.rename(columns={c: col_map.get(c.lower(), c) for c in reg_df.columns})
        # Ensure all expected columns exist; fall back to static if not
        expected = set(reg_df_static.columns)
        if not expected.issubset(set(reg_df.columns)):
            reg_df = reg_df_static
            reg_is_live = False
    live_badge(reg_is_live, last_run)

    risk_filter = st.multiselect(
        "Filter by Risk Level",
        options=["🔴 HIGH","🟡 MEDIUM","🟡 LOW-MED","🟢 LOW"],
        default=["🔴 HIGH","🟡 MEDIUM","🟡 LOW-MED","🟢 LOW"],
    )
    st.dataframe(
        reg_df[reg_df["Risk"].isin(risk_filter)],
        hide_index=True, use_container_width=True, height=380,
        column_config={
            "Source URL": st.column_config.LinkColumn("Source", display_text="🔗 Link"),
        },
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

    with st.expander("📋 What changed in June 2026 — click to expand", expanded=False):
        st.markdown(
            "**This update corrects the COGS component allocation and adds the NurExone optimized "
            "manufacturing track, based on three new peer-reviewed TEA sources.**"
        )
        st.markdown("")

        col_wc1, col_wc2 = st.columns(2)

        with col_wc1:
            st.markdown(
                '<div class="signal-card">'
                '<strong>🧮 COGS Breakdown — component allocation rebalanced</strong><br>'
                'Three independent TEA sources confirm the correct cost structure: '
                '<strong>cell expansion media ≈ 50% of total COG</strong>, all upstream combined ≈ 90%, '
                'downstream processing (TFF + polishing) ≈ 10%.<br><br>'
                'The previous version overstated downstream at ~30% and understated media at ~13%. '
                'The totals ($155–315/10B at 2026 commercial mid) are <strong>unchanged</strong>.<br><br>'
                '"Isolation &amp; purification" has been split into two rows: '
                '<strong>EV harvest / cell collection (USP)</strong> (~8%) and '
                '<strong>Downstream purification (TFF + polish)</strong> (~10%). '
                'This split applies to all three scale years (2022 · 2026 · 2030).</div>',
                unsafe_allow_html=True,
            )

        with col_wc2:
            st.markdown(
                '<div class="signal-card">'
                '<strong>📈 New: 3D Optimized ATMP track</strong><br>'
                'The COGS trajectory chart now shows two tracks on a log scale:<br>'
                '• <strong>Blue band</strong> — standard BM-MSC clinical GMP ($155–315/10B in 2026)<br>'
                '• <strong>Orange band</strong> — 3D optimized ATMP-grade, NurExone-style (≈$25–60/10B in 2026), '
                'anchored to the RoosterBio optimized 3D benchmark (&lt;$25/10B) plus ATMP overhead.<br><br>'
                'In the <strong>Margin Scenario Modeler</strong>, select '
                '"🔬 3D Optimized ATMP-grade (BM-MSC, NurExone-style)" to model margins '
                'at the optimized cost level.<br><br>'
                '<strong>Sources added:</strong> RoosterBio 2024 bioprocess TEA abstract · '
                'IST Lisbon 2025 operational analysis · PMC5895685 hMSC manufacturing review · '
                'RoosterBio DSP blog 2025. See the Sources section at the bottom of this tab.</div>',
                unsafe_allow_html=True,
            )

    subtabs = st.tabs([
        "🔬 Per-10B Particle Benchmark",
        "💊 Per-Treatment OOP (Validated)",
        "📦 B2B Derived from 10B Data",
        "🗺️ Market Ceiling Analysis",
        "🧮 BM-MSC COGS Breakdown",
        "📈 Margin Scenario Modeler",
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
        p10b_df_static = pd.DataFrame([
            {"Product":"EXOMIDE (Jolifill, Germany)",    "Source Type":"Retail",      "Vial Size":"5mL",       "Vial Price":"€115 (~$125)","10B Low":250,"10B High":250,"Confidence":"🟢 High","Source":"Jolifill.de — confirmed","Source URL":"https://jolifill.de"},
            {"Product":"EXOGEN (HUK Aesthetics, UK)",    "Source Type":"Retail",      "Vial Size":"1mg+6mL",   "Vial Price":"£60 2-vial kit","10B Low":37,"10B High":75,"Confidence":"🟢 High","Source":"HUK Aesthetics — confirmed","Source URL":"https://huk-aesthetics.com"},
            {"Product":"EXOXE Exosomes (50mg, EU/CEE)",  "Source Type":"Retail",      "Vial Size":"50mg",      "Vial Price":"~$85 (80 EUR)","10B Low":60,"10B High":90,"Confidence":"🟢 High","Source":"EU/CEE retail — confirmed","Source URL":"https://www.medicadepot.com/exosomes.html"},
            {"Product":"Selastin Exo Plus (100mg, Poland)","Source Type":"Retail",    "Vial Size":"100mg liquid","Vial Price":"~$50 (46 EUR)","10B Low":35,"10B High":55,"Confidence":"🟢 High","Source":"Poland/CEE retail — confirmed","Source URL":"https://www.medicadepot.com/exosomes.html"},
            {"Product":"EXOJUV (plant-derived)",         "Source Type":"Wholesale",   "Vial Size":"6B/vial",   "Vial Price":"$150–200","10B Low":250,"10B High":333,"Confidence":"🟡 Med","Source":"MedicaDepot wholesale","Source URL":"https://www.medicadepot.com/exojuv.html"},
            {"Product":"EXOBLOOM (Dermax)",              "Source Type":"Wholesale",   "Vial Size":"5B+/vial",  "Vial Price":"$120–180","10B Low":240,"10B High":360,"Confidence":"🟡 Med","Source":"DermaxMed B2B","Source URL":"https://www.medicadepot.com/exosomes.html"},
            {"Product":"ReBellaXO (UC-MSC, R3)",         "Source Type":"Wholesale",   "Vial Size":"15B/cc",    "Vial Price":"$300–450","10B Low":200,"10B High":300,"Confidence":"🟡 Med","Source":"R3 Stem Cell 2024","Source URL":"https://r3stemcell.com"},
            {"Product":"Generic BM-MSC (Alibaba B2B)",   "Source Type":"B2B Bulk",    "Vial Size":"1mg≈10–15B","Vial Price":"$180–280/mg","10B Low":150,"10B High":280,"Confidence":"🟡 Med","Source":"Alibaba supplier data 2024–25","Source URL":"https://www.alibaba.com/trade/search?SearchText=exosome+MSC"},
            {"Product":"BENEV (ExoCoBio US)",            "Source Type":"Professional","Vial Size":"20–30B est.","Vial Price":"$400–600","10B Low":160,"10B High":250,"Confidence":"🟡 Med","Source":"US professional channel est.","Source URL":"https://benev.com"},
        ])
        # ── Live pricing data wiring ──────────────────────────────
        p10b_df, pricing_is_live = get_live_or_static(live_pricing, p10b_df_static)
        if pricing_is_live:
            # Normalise column names from CSV
            col_map_p = {c.lower().replace(" ","_"): c for c in p10b_df_static.columns}
            p10b_df = p10b_df.rename(columns={c: col_map_p.get(c.lower().replace(" ","_"), c) for c in p10b_df.columns})
            expected_p = {"10B Low","10B High","Product"}
            if not expected_p.issubset(set(p10b_df.columns)):
                p10b_df = p10b_df_static
                pricing_is_live = False
            else:
                p10b_df["10B Low"]  = pd.to_numeric(p10b_df["10B Low"],  errors="coerce").fillna(0).astype(int)
                p10b_df["10B High"] = pd.to_numeric(p10b_df["10B High"], errors="coerce").fillna(0).astype(int)
        live_badge(pricing_is_live, last_run)
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
            height=400, barmode="overlay", showlegend=False,
            xaxis_title="Price per 10 Billion Particles (USD)",
            yaxis_title="", margin=dict(t=50, b=10),
            title="",
        )
        st.plotly_chart(fig_10b, use_container_width=True)
        st.caption("🟢 Green = independently confirmed by retail sources | 🟠 Amber = estimated from supplier/wholesale data")
        st.markdown("")

        # ── Full data table ───────────────────────────────────────
        st.markdown('<div class="section-header">Full Per-10B Particle Data Table</div>', unsafe_allow_html=True)
        display_cols = ["Product","Source Type","Vial Size","Vial Price","10B Low","10B High","10B Mid","Confidence","Source","Source URL"]
        avail_cols = [c for c in display_cols if c in p10b_df.columns]
        st.dataframe(
            p10b_df[avail_cols].assign(**{
                "10B Low": p10b_df["10B Low"].apply(lambda x: f"${x:,}"),
                "10B High": p10b_df["10B High"].apply(lambda x: f"${x:,}"),
                "10B Mid": p10b_df["10B Mid"].apply(lambda x: f"${x:,}"),
            }),
            hide_index=True, use_container_width=True,
            column_config={
                "Source URL": st.column_config.LinkColumn("Source", display_text="🔗 Link"),
            },
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

        # Mat. Cost Clinic = total course dose × clinic purchase price per 10B
        # Clinic purchase range assumed $92–250/10B (Stem Nova confirmed low → mid-market aesthetic wholesale)
        # ⚠️ Previous version understated material costs by 2–7x vs per-10B benchmark
        oop_df = pd.DataFrame([
            # Facial: 5–10B × 3 sessions = 15–30B total. @$92–200/10B → $138–600
            {"Indication":"Facial Skin Rejuvenation",    "Dose/Session":"5–10B",   "Sessions":"3",   "Mat. Cost Clinic":"$150–600",   "OOP Low":400,  "OOP High":900,   "Markets":"EU, SEA, UAE, TH",      "OOP Conf":"🟢 Sourced",   "Mat. Method":"🟢 Calc"},
            # Hair: 10–20B × 3–4 sessions typical = 30–80B total. @$100–200/10B → $300–1,200
            {"Indication":"Hair Restoration",            "Dose/Session":"10–20B",  "Sessions":"3–6", "Mat. Cost Clinic":"$300–1,200",  "OOP Low":900,  "OOP High":2300,  "Markets":"UAE, US, EU, TH",       "OOP Conf":"🟢 Sourced",   "Mat. Method":"🟢 Calc"},
            # Wound: 10–30B × 1–3 sessions = 15–60B typical. @$100–200/10B → $150–800 (⚠️ note: OOP range may be tight at high dose)
            {"Indication":"Wound Healing / Scar",        "Dose/Session":"10–30B",  "Sessions":"1–3", "Mat. Cost Clinic":"$200–800",    "OOP Low":600,  "OOP High":2200,  "Markets":"MX, TH, SEA, AU",       "OOP Conf":"🟡 Estimated", "Mat. Method":"🟢 Calc"},
            # Joint: 30–50B × 1–2 sessions = 30–100B. @$150–250/10B → $450–1,500 (⚠️ was $350–700 — too low)
            {"Indication":"Joint Pain / Osteoarthritis", "Dose/Session":"30–50B",  "Sessions":"1–2", "Mat. Cost Clinic":"$500–1,500",  "OOP Low":1500, "OOP High":3500,  "Markets":"MX, UAE, TH, SEA",      "OOP Conf":"🟢 Sourced",   "Mat. Method":"🟢 Calc"},
            # IV Longevity: CORRECTED — realistic clinic protocol is 1–2 sessions of 25–50B (not 2–4 × 50–100B).
            # Prior entry (2–4 sessions × 50–100B = 100–400B total) implied mat cost >$10,000 vs OOP $3,750–5,500: mathematically impossible.
            # Premium longevity IV at UAE/AU/TH premium clinics: $5,000–15,000 per protocol (Bookimed, EDEN Aesthetics data).
            {"Indication":"Systemic IV Longevity",       "Dose/Session":"25–50B",  "Sessions":"1–2", "Mat. Cost Clinic":"$500–2,500",  "OOP Low":5000, "OOP High":15000, "Markets":"UAE, AU, TH (premium)", "OOP Conf":"🟡 Estimated", "Mat. Method":"🟡 Derived"},
            # Post-procedure: 5B × 1 session. @$92–200/10B → $46–100. Minor adjustment.
            {"Indication":"Post-Procedure Recovery",     "Dose/Session":"5B",      "Sessions":"1",   "Mat. Cost Clinic":"$50–120",     "OOP Low":150,  "OOP High":400,   "Markets":"EU, SEA, US, TH",       "OOP Conf":"🟡 Estimated", "Mat. Method":"🟢 Calc"},
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
                hovertemplate=f"<b>{row['Indication']}</b><br>${row['OOP Low']:,}–${row['OOP High']:,}<br>Mat. cost to clinic: {row['Mat. Cost Clinic']}<br>Markets: {row['Markets']}<br>OOP confidence: {row['OOP Conf']}<extra></extra>",
            ))
        fig_oop.update_layout(
            showlegend=False, height=400, barmode="stack",
            yaxis_title="OOP Price to Patient (USD)",
            xaxis_tickangle=-20,
            title="Patient OOP Price Range by Indication (full treatment course)",
        )
        st.plotly_chart(fig_oop, use_container_width=True)
        st.dataframe(
            oop_df[["Indication","Dose/Session","Sessions","Mat. Cost Clinic","Mat. Method","OOP Low","OOP High","Markets","OOP Conf"]]
            .assign(**{"OOP Low": oop_df["OOP Low"].apply(lambda x: f"${x:,}"),
                       "OOP High": oop_df["OOP High"].apply(lambda x: f"${x:,}")}),
            hide_index=True, use_container_width=True,
            column_config={
                "Mat. Method": st.column_config.TextColumn(
                    "Mat. Basis",
                    help="🟢 Calc = calculated from per-10B benchmark × dose | 🟡 Derived = estimated from indirect data"
                ),
                "OOP Conf": st.column_config.TextColumn(
                    "OOP Conf",
                    help="🟢 Sourced = from clinic/aggregator pricing data (Bookimed, R3, BioInformant) | 🟡 Estimated = modeled from adjacent markets"
                ),
            },
        )
        st.caption(
            "Mat. Basis: 🟢 Calc = total course dose × clinic purchase price ($92–250/10B from per-10B benchmark). "
            "OOP Conf: 🟢 Sourced = Bookimed/R3/BioInformant clinic data; 🟡 Estimated = modeled from adjacent markets. "
            "⚠️ Systemic IV Longevity corrected to 1–2 sessions of 25–50B (prior 2–4 × 50–100B was inconsistent with observed OOP prices)."
        )
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
        fig_cee2.update_layout(height=380, margin=dict(t=20, b=70), xaxis_tickangle=-15,
                               yaxis_title="OOP Price (USD)", legend_title="",
                               title="",
                               legend=dict(orientation="h", yanchor="top", y=-0.18, xanchor="center", x=0.5))
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

        # B2B prices from S6 (MedicaDepot/Maylips verified 2026). COGS target = max COGS for 40% gross margin
        # at B2B midpoint. S1 UC-MSC commercial mid COGS $135–252; BM-MSC +15–25% = $155–315.
        # Cosmetic grade ~40% lower = $90–190. Source: Exosome_COGS_Model_Sourced.xlsx, Sheet 3.
        attr_df = pd.DataFrame([
            {"Market":"Germany/EU",     "B2B Range (S6)":"$140–225/10B",  "Max COGS for 40% Margin":"<$84–135",  "Grade Needed":"Clinical GMP or cosmetic", "Key Pitch":"BM-MSC clinical lit; CD73/CD90 CoA; NTA data","Source":"S6 MedicaDepot EU pricing"},
            {"Market":"UAE/GCC",        "B2B Range (S6)":"$175–300/10B",  "Max COGS for 40% Margin":"<$105–180", "Grade Needed":"Clinical GMP",             "Key Pitch":"Longevity angle; high-dose IV protocols",       "Source":"S6 EDEN Aesthetics/DUBIMED est."},
            {"Market":"USA (aesthetic)","B2B Range (S6)":"$150–275/10B",  "Max COGS for 40% Margin":"<$90–165",  "Grade Needed":"Cosmetic/professional",    "Key Pitch":"CoA CD63/CD81; no therapeutic claims; GMP",     "Source":"S6 Stem Nova/BENEV pricing"},
            {"Market":"Australia",      "B2B Range (S6)":"$175–300/10B",  "Max COGS for 40% Margin":"<$105–180", "Grade Needed":"Clinical GMP (TGA)",       "Key Pitch":"TGA compliance documentation; Biogenix model",  "Source":"S6 derived from AU premium channel"},
            {"Market":"Mexico/LATAM",   "B2B Range (S6)":"$100–175/10B",  "Max COGS for 40% Margin":"<$60–105",  "Grade Needed":"Cosmetic grade",           "Key Pitch":"Lyophilized; ANVISA-COFEPRIS MoU compliance",   "Source":"S6 LATAM wholesale est."},
            {"Market":"Thailand",       "B2B Range (S6)":"$90–150/10B",   "Max COGS for 40% Margin":"<$54–90",   "Grade Needed":"Cosmetic grade",           "Key Pitch":"Thai FDA cosmetic notification; ASEAN docs",    "Source":"S6 TH clinic pricing"},
            {"Market":"Philippines/SEA","B2B Range (S6)":"$75–125/10B",   "Max COGS for 40% Margin":"<$45–75",   "Grade Needed":"Cosmetic grade",           "Key Pitch":"PH FDA notification gateway; ASEAN directive",  "Source":"S6 SEA wholesale est."},
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
        st.caption("B2B price ranges from S6 (MedicaDepot/Maylips/Stem Nova verified wholesale listings, 2026). COGS targets derived from S1 (Silva et al. 2025) + G2 derivation for BM-MSC premium. See Exosome_COGS_Model_Sourced.xlsx for full sourcing.")

    # ── Sub-tab 5: COGS BREAKDOWN ─────────────────────────────────
    with subtabs[4]:
        st.markdown('<div class="section-header">BM-MSC Exosome COGS — Component Breakdown (per 10B-particle dose)</div>', unsafe_allow_html=True)
        st.markdown("")

        # ── SOURCED COGS DATA (updated Jun 2026) ──────────────────────────────
        # 2022/Research scale: S3 (RoosterBio 2022) + S5 (Lembong 2020) — $1M/lot of 5×10¹² EVs
        #   = ~$8,000/dose at 125 doses/lot (research scale). BM-MSC +15–25% over UC-MSC (G2).
        # 2026/Commercial mid: S1 (Silva et al. 2025, PMC11913891) UC-MSC selling price
        #   €166–309 / 1.36 ROI × 1.11 USD/EUR = $135–252 COGS. BM-MSC +15–25% → $155–315.
        #   Component % splits from S2 (Ng et al. 2019, PMC6322973): EV harvest >50% of COG,
        #   labor dominates; media base $150/L; labor $200/hr.
        # 2030/Industrial: Extrapolated ~50% reduction per further scale-up (S2).
        # Component allocation anchored to RoosterBio 2024 bioprocess TEA + IST Lisbon 2025 + Ng et al. 2019:
        # Upstream ≈90% (media ≈50%, labor+bioreactor ≈18%, harvest ≈8%, donor ≈6%); downstream ≈10%.
        # Totals unchanged: 2022 $6,800–12,100 (S3/S5), 2026 $155–315 (S1+G2), 2030 $58–125 (extrapolated S2).
        cogs_df = pd.DataFrame([
            {"Component":"Cell expansion media (GMP)",            "2022 Low":3060, "2022 High":5445, "2026 Low":70, "2026 High":142, "2030 Low":26, "2030 High":56},
            {"Component":"Upstream labor + bioreactor ops",       "2022 Low":1224, "2022 High":2178, "2026 Low":28, "2026 High":57,  "2030 Low":10, "2030 High":23},
            {"Component":"BM-MSC donor procurement",              "2022 Low":408,  "2022 High":726,  "2026 Low":9,  "2026 High":19,  "2030 Low":4,  "2030 High":7},
            {"Component":"EV harvest / cell collection (USP)",    "2022 Low":544,  "2022 High":968,  "2026 Low":12, "2026 High":25,  "2030 Low":5,  "2030 High":10},
            {"Component":"Downstream purification (TFF + polish)","2022 Low":680,  "2022 High":1210, "2026 Low":16, "2026 High":32,  "2030 Low":6,  "2030 High":12},
            {"Component":"QC & characterization",                 "2022 Low":340,  "2022 High":605,  "2026 Low":8,  "2026 High":16,  "2030 Low":3,  "2030 High":6},
            {"Component":"Lyophilization (optional)",             "2022 Low":272,  "2022 High":484,  "2026 Low":6,  "2026 High":12,  "2030 Low":2,  "2030 High":6},
            {"Component":"Batch release / regulatory",            "2022 Low":272,  "2022 High":484,  "2026 Low":6,  "2026 High":12,  "2030 Low":2,  "2030 High":5},
        ])

        year_sel = st.radio("Select scale view", ["2022 (Research <100/mo) — S3/S5", "2026 (Commercial mid 500–2k/mo) — S1+G2", "2030 (Industrial >5k/mo) — Extrapolated"], horizontal=True)
        if "2022" in year_sel: lo, hi = "2022 Low", "2022 High"
        elif "2026" in year_sel: lo, hi = "2026 Low", "2026 High"
        else: lo, hi = "2030 Low", "2030 High"

        cogs_df["Mid"] = (cogs_df[lo] + cogs_df[hi]) / 2
        total_lo = cogs_df[lo].sum()
        total_hi = cogs_df[hi].sum()

        st.markdown(
            '<div class="signal-card">📐 <strong>Cost structure — confirmed by 3 independent TEA sources '
            '(RoosterBio 2024 · IST Lisbon 2025 · Ng et al. 2019):</strong> '
            'Upstream ≈ <strong>90%</strong> of total COG &nbsp;|&nbsp; '
            'Cell expansion media alone ≈ <strong>50%</strong> of total COG &nbsp;|&nbsp; '
            'Downstream (TFF + polishing) ≈ <strong>10%</strong> of total COG. '
            'Media cost is the single largest lever for COG reduction at any scale. '
            'Downstream DSP decisions matter for yield and purity but are <em>not</em> the dominant cost driver.</div>',
            unsafe_allow_html=True,
        )
        st.markdown("")

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
                height=380, margin=dict(t=20, b=10),
                coloraxis_showscale=False,
                xaxis_title="USD per dose", yaxis_title="",
                title="",
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
            f'<strong>${total_lo:,} – ${total_hi:,}</strong> per 10B-particle BM-MSC dose. '
            f'Research scale ($6,800–12,100/10B) → Commercial mid ($155–315/10B) → Industrial ($58–125/10B, extrapolated). '
            f'<strong>Cost structure (3-source consensus):</strong> upstream ≈90% '
            f'(media ≈50% · labor+bioreactor ≈18% · harvest ≈8% · donor ≈6%) | downstream (TFF + polish) ≈10%. '
            f'Sources: RoosterBio 2024 bioprocess TEA abstract; IST Lisbon 2025 operational analysis; Ng et al. 2019 (PMC6322973). '
            f'Commercial mid anchor: Silva et al. 2025 (PMC11913891) UC-MSC <em>selling price</em> €166–309 ÷ 1.36 ROI × 1.11 USD/EUR = $135–252 COGS; BM-MSC +15–25% (G2) → $155–315. '
            f'Research scale anchor: RoosterBio 2022 + Lembong 2020 (PMC7552727): $1M/lot of 5×10¹² EVs = ~$8,000/dose. '
            f'RoosterBio optimized 3D benchmark: <strong>&lt;$25/10B EV</strong>; '
            f'NurExone-style ATMP overhead → <strong>≈$25–60/10B</strong> (research synthesis, Jun 2026). '
            f'<strong>⚠️ Standard clinical GMP track = $155–315/10B. 3D Optimized ATMP-grade (NurExone-style) = $25–60/10B. '
            f'Select the correct context in the Margin Scenario Modeler tab.</strong></div>',
            unsafe_allow_html=True,
        )

        st.markdown('<div class="section-header">COGS Trajectory — Standard GMP vs 3D Optimized ATMP Track (per 10B-particle dose)</div>', unsafe_allow_html=True)
        st.caption(
            "Blue band = standard BM-MSC clinical GMP trajectory (S1+G2 anchor, Silva et al. 2025 + RoosterBio 2022). "
            "Orange band = 3D-optimized ATMP-grade trajectory (RoosterBio 2024 optimized benchmark + NurExone ATMP overhead, Jun 2026 synthesis). "
            "Log scale used so both tracks are readable across the $25–$12,000 range. "
            "Sources: S1 (Silva et al. 2025, PMC11913891), S3 (RoosterBio 2022), RoosterBio 2024 bioprocess TEA abstract (ScienceDirect), S2 (Ng et al. 2019, PMC6322973)."
        )
        traj_df = pd.DataFrame({
            "Year":  [2022, 2024, 2026, 2028, 2030],
            "Low":   [6800, 3500, 155,  92,   58],
            "High":  [12100,6250, 315,  190,  125],
            "Scale": ["Research (<100/mo) — S3/S5","Small batch — interpolated","Commercial mid (500–2k/mo) — S1+G2","Scale-up — extrapolated S2","Industrial (>5k/mo) — extrapolated S2"],
        })
        traj_df["Mid"] = (traj_df["Low"] + traj_df["High"]) / 2

        # 3D Optimized track: RoosterBio <$25/10B + ATMP overhead → ≈$25–60/10B (NurExone-style, Jun 2026)
        traj_opt_df = pd.DataFrame({
            "Year":  [2024, 2026, 2028, 2030],
            "Low":   [80,   25,   18,   12],
            "High":  [200,  60,   38,   25],
            "Scale": ["Early 3D optimization","3D Optimized ATMP (NurExone-style) — Jun 2026 synthesis","Scale-up — extrapolated","Industrial — extrapolated"],
        })
        traj_opt_df["Mid"] = (traj_opt_df["Low"] + traj_opt_df["High"]) / 2

        fig_traj = go.Figure()
        # Standard GMP band (blue)
        fig_traj.add_trace(go.Scatter(x=traj_df["Year"], y=traj_df["High"],
            fill=None, mode="lines", line_color="#b3dff0", name="Standard GMP — High", showlegend=False))
        fig_traj.add_trace(go.Scatter(x=traj_df["Year"], y=traj_df["Low"],
            fill="tonexty", mode="lines", line_color="#7ec8e3",
            fillcolor="rgba(126,200,227,0.25)", name="Standard GMP range"))
        fig_traj.add_trace(go.Scatter(x=traj_df["Year"], y=traj_df["Mid"],
            mode="lines+markers+text",
            line=dict(color="#1e3a5f", width=3),
            marker=dict(size=10, color="#2e6da4"),
            text=[f"${int(v):,}" for v in traj_df["Mid"]],
            textposition="top center", name="Standard GMP midpoint"))
        # 3D Optimized ATMP band (orange)
        fig_traj.add_trace(go.Scatter(x=traj_opt_df["Year"], y=traj_opt_df["High"],
            fill=None, mode="lines", line_color="#f0c090", name="3D Optimized — High", showlegend=False))
        fig_traj.add_trace(go.Scatter(x=traj_opt_df["Year"], y=traj_opt_df["Low"],
            fill="tonexty", mode="lines", line_color="#e05c2a",
            fillcolor="rgba(224,92,42,0.15)", name="3D Optimized range"))
        fig_traj.add_trace(go.Scatter(x=traj_opt_df["Year"], y=traj_opt_df["Mid"],
            mode="lines+markers+text",
            line=dict(color="#c62828", width=3, dash="dash"),
            marker=dict(size=10, color="#e05c2a", symbol="diamond"),
            text=[f"${int(v):,}" for v in traj_opt_df["Mid"]],
            textposition="bottom center", name="3D Optimized midpoint"))
        fig_traj.update_layout(
            height=420, margin=dict(t=20, b=90),
            xaxis_title="Year",
            yaxis=dict(title="COGS per 10B-particle dose (USD, log scale)", type="log"),
            title="",
            legend=dict(orientation="h", yanchor="top", y=-0.20, xanchor="center", x=0.5),
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

    # ── Sub-tab 6: MARGIN SCENARIO MODELER ───────────────────────
    with subtabs[5]:
        st.markdown('<div class="section-header">Margin & Viability Scenario Modeler</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="signal-card">📊 <strong>How to use:</strong> Select your target market and production scale. '
            "The modeler computes your B2B ceiling price (derived from observed per-10B market data), "
            "your COGS at the selected production year/scale, and whether you can hit your target gross margin. "
            "Adjust sliders to find the conditions under which the market becomes profitable.</div>",
            unsafe_allow_html=True,
        )
        st.markdown("")

        # ── Market reference data (per 10B particles) ─────────────
        # Aesthetic/wellness markets: B2B prices from observed retail/wholesale benchmark data.
        # Therapeutic markets: back-calculated from clinical OOP pricing and industry estimates.
        # These are SEPARATE channels — match product grade to the correct market tier.
        MARKET_REF = {
            # ── Aesthetic / wellness channel ─────────────────────────
            "🧴 Germany / EU (aesthetic)":       {"b2b_lo": 130, "b2b_hi": 210, "end_user_lo": 100, "end_user_hi": 200, "flag": "🇩🇪", "tier": "aesthetic"},
            "🧴 UAE / GCC (aesthetic)":          {"b2b_lo": 160, "b2b_hi": 270, "end_user_lo": 180, "end_user_hi": 350, "flag": "🇦🇪", "tier": "aesthetic"},
            "🧴 USA (aesthetic wholesale)":      {"b2b_lo": 140, "b2b_hi": 260, "end_user_lo": 150, "end_user_hi": 300, "flag": "🇺🇸", "tier": "aesthetic"},
            "🧴 Australia (aesthetic)":          {"b2b_lo": 160, "b2b_hi": 270, "end_user_lo": 180, "end_user_hi": 350, "flag": "🇦🇺", "tier": "aesthetic"},
            "🧴 Mexico / LATAM (aesthetic)":     {"b2b_lo": 95,  "b2b_hi": 165, "end_user_lo": 100, "end_user_hi": 200, "flag": "🇲🇽", "tier": "aesthetic"},
            "🧴 Thailand (aesthetic)":           {"b2b_lo": 80,  "b2b_hi": 140, "end_user_lo": 80,  "end_user_hi": 180, "flag": "🇹🇭", "tier": "aesthetic"},
            "🧴 Philippines / SEA (aesthetic)":  {"b2b_lo": 65,  "b2b_hi": 115, "end_user_lo": 60,  "end_user_hi": 120, "flag": "🇵🇭", "tier": "aesthetic"},
            # ── Therapeutic / clinical channel ────────────────────────
            # Sources: Bookimed premium IV longevity ($5,000–15,000/treatment at 25–50B/session = $500–3,000/10B);
            # R3 Stem Cell orthopedic ($3,950 for 150B = $263/10B at clinic cost, B2B ~$150–400/10B);
            # NurExone ExoPTEN compassionate/Phase II: estimated $1,500–5,000/10B based on comparable
            # therapeutic biologics (Spinraza $125K/dose; AVONEX $50K/year) discounted for early market.
            "💊 IV Longevity / Premium Wellness": {"b2b_lo": 500,  "b2b_hi": 1500, "end_user_lo": 1000, "end_user_hi": 3000, "flag": "🌐", "tier": "therapeutic"},
            "💊 Orthopedic / Joint (therapeutic)":{"b2b_lo": 300,  "b2b_hi": 800,  "end_user_lo": 600,  "end_user_hi": 1500, "flag": "🌐", "tier": "therapeutic"},
            "💊 Neurological / SCI (Phase II)":   {"b2b_lo": 1500, "b2b_hi": 5000, "end_user_lo": 3000, "end_user_hi": 10000,"flag": "🌐", "tier": "therapeutic"},
        }

        # ── COGS by product grade (per 10B particles) ──────────────
        # ROOT CAUSE OF PREVIOUS -900% MARGIN: prior model applied clinical therapeutic GMP COGS
        # ($1,400–3,150/10B) to aesthetic market prices ($65–270/10B). These are different product
        # categories and should never be compared in the same scenario without explicit labeling.
        #
        # Sources:
        # • Cosmetic/aesthetic grade: back-calculated from AnteAGE MDX (14B/vial, ~$150–250/vial
        #   wholesale from US ISO Class 5 facility → 50–60% gross margin → COGS $45–90/10B).
        # • Professional US (bioreactor): Stem Nova 3DExo+ confirmed $92/10B wholesale →
        #   implied COGS $35–55/10B at commercial scale (40–60% gross margin).
        # • Asian commercial GMP: back-calculated from Alibaba B2B ($150–280/10B wholesale,
        #   20–40% gross margin → COGS $90–220/10B). Alibaba suppliers must be profitable.
        # • Clinical therapeutic GMP: RoosterBio 2025, Astute Analytica 2035, Corning Feb 2025.
        #   $150K release testing per lot + $50K/day GMP labor. Correct for ExoPTEN/IND-enabling.
        COGS_BY_CONTEXT = {
            "🧴 Cosmetic / aesthetic grade (ISO Class 7–8)": {
                "note": "Cosmetic-grade exosome manufacturing — ISO Class 7–8 cleanroom, basic NTA characterization, "
                        "lyophilized fill/finish. Matches the products in the Per-10B Benchmark table (EXOMIDE, EXOGEN, "
                        "Selastin etc). Source: AnteAGE MDX US manufacturing back-calculation "
                        "(14B/vial, ~$150–250/vial wholesale, 50–60% gross margin → COGS $45–90/10B). "
                        "✅ VIABLE in aesthetic wholesale channel at commercial scale.",
                "color": "#3db07a",
                "scales": {
                    "2026 — Small batch (<500 doses/mo)":  {"mid": 95,  "lo": 60,  "hi": 130},
                    "2026 — Commercial mid (500–5k/mo)":   {"mid": 55,  "lo": 35,  "hi": 75},
                    "2026 — Scale-up (5k–20k/mo)":         {"mid": 32,  "lo": 20,  "hi": 44},
                    "2030 — Industrial (>20k/mo)":         {"mid": 18,  "lo": 10,  "hi": 26},
                },
            },
            "⚡ Professional US grade (ISO Class 5, 3D bioreactor)": {
                "note": "US-based ISO Class 5 manufacturing with bioreactor expansion, TFF, SEC, full NTA "
                        "characterization and lyophilization (AnteAGE MDX, Stem Nova, BENEV model). "
                        "Source: Stem Nova 3DExo+ confirmed $92/10B wholesale (60B/vial, $550) → "
                        "implies COGS $35–55/10B at scale assuming 40–60% gross margin. "
                        "✅ VIABLE in professional aesthetic and soft-indication channels.",
                "color": "#2e6da4",
                "scales": {
                    "2026 — Early commercial (500–2k/mo)": {"mid": 120, "lo": 80,  "hi": 160},
                    "2026 — Commercial mid (2k–10k/mo)":   {"mid": 65,  "lo": 42,  "hi": 88},
                    "2028 — Scale-up (10k–30k/mo)":        {"mid": 40,  "lo": 26,  "hi": 54},
                    "2030 — Industrial (>30k/mo)":         {"mid": 22,  "lo": 14,  "hi": 30},
                },
            },
            "🌏 Asian commercial GMP (KR/CN/SG, ASEAN compliant)": {
                "note": "Korean / Chinese / Singapore GMP manufacturing. "
                        "Back-calculated: Alibaba B2B suppliers sell at $150–280/10B wholesale and must be profitable → "
                        "COGS ~$90–220/10B assuming 20–40% gross margin. "
                        "ASEAN cosmetic GMP compliant. Lower CAPEX than US/EU but higher per-unit cost than bioreactor models. "
                        "⚠️ May not satisfy FDA/EMA for therapeutic claims.",
                "color": "#f0a030",
                "scales": {
                    "2026 — Small batch (<500 doses/mo)":  {"mid": 200, "lo": 130, "hi": 270},
                    "2026 — Commercial mid (500–5k/mo)":   {"mid": 140, "lo": 90,  "hi": 190},
                    "2026 — Scale-up (5k–20k/mo)":         {"mid": 90,  "lo": 58,  "hi": 122},
                    "2030 — Industrial (>20k/mo)":         {"mid": 50,  "lo": 30,  "hi": 70},
                },
            },
            "💊 Clinical therapeutic GMP — BM-MSC (IND-enabling, FDA/EMA)": {
                "note": "Full pharmaceutical-grade GMP — validated processes. "
                        "SOURCED: Research scale anchor from S3 (RoosterBio 2022) + S5 (Lembong et al. 2020, PMC7552727): "
                        "$1M/lot of 5×10¹² EVs = ~$8,000/dose at 125 doses/lot. "
                        "Commercial mid anchor from S1 (Silva et al. 2025, PMC11913891): UC-MSC selling price €166–309 "
                        "÷ 1.36 ROI × 1.11 USD/EUR = $135–252 COGS; BM-MSC +15–25% (G2) → $155–315. "
                        "Component splits from S2 (Ng et al. 2019, PMC6322973): EV harvest >50% of COG; $150K/lot release testing (S4). "
                        "⚠️ MUST be paired with therapeutic market tiers (💊) — NOT aesthetic pricing. "
                        "Correct for NurExone ExoPTEN / IND-enabling therapeutic applications.",
                "color": "#e05c2a",
                "scales": {
                    "2022 — Research (<100 doses/mo) — S3/S5":      {"mid": 9500, "lo": 6800, "hi": 12100},
                    "2024 — Small batch (100–500 doses/mo) — interpolated": {"mid": 4700, "lo": 3500, "hi": 6250},
                    "2026 — Commercial mid (500–2k/mo) — S1+G2":    {"mid": 225,  "lo": 155,  "hi": 315},
                    "2030 — Industrial (>5k/mo) — extrapolated S2":  {"mid": 82,   "lo": 58,   "hi": 125},
                },
            },
            "🔬 3D Optimized ATMP-grade (BM-MSC, NurExone-style)": {
                "note": "3D bioreactor optimized BM-MSC EV process with ATMP-grade QA/QMS documentation overhead. "
                        "Anchored to RoosterBio optimized benchmark (<$25/10B EV at 10¹¹/dose), adjusted upward for "
                        "ATMP-grade regulatory + release testing overhead (~$10–35/10B additional). "
                        "Research synthesis (Jun 2026): ≈$25–60/10B for a 4–5×10L 3D bioreactor setup. "
                        "Matches NurExone's current process position per Jun 2026 COG research synthesis. "
                        "✅ VIABLE in therapeutic (💊) and premium aesthetic (🧴) markets at commercial scale.",
                "color": "#166534",
                "scales": {
                    "2026 — Early ATMP commercial (200–1k doses/mo)": {"mid": 42, "lo": 25, "hi": 60},
                    "2028 — Scale-up ATMP (1k–5k doses/mo)":         {"mid": 28, "lo": 18, "hi": 38},
                    "2030 — Industrial ATMP (>5k doses/mo)":         {"mid": 18, "lo": 12, "hi": 25},
                },
            },
            "✏️ Custom — enter your COGS below": {
                "note": "Enter your own COGS estimate based on your specific manufacturing setup.",
                "color": "#7ec8e3",
                "scales": {"Custom": {"mid": None, "lo": None, "hi": None}},
            },
        }

        # ── Product grade / market tier guidance ──────────────────
        st.markdown(
            '<div class="signal-card">'
            "📊 <strong>How to use this modeler correctly:</strong> Match your <em>product grade</em> to the <em>market tier</em>. "
            "🧴 Cosmetic/professional grade → select aesthetic markets (🧴). "
            "💊 Clinical therapeutic GMP → select therapeutic markets (💊). "
            "Mixing clinical COGS with aesthetic prices will always show negative margins — "
            "these are fundamentally different products in different channels."
            "</div>",
            unsafe_allow_html=True,
        )
        st.markdown("")

        col_inp1, col_inp2 = st.columns([1, 1])
        with col_inp1:
            st.markdown('<div class="section-subheader">🎛 Inputs</div>', unsafe_allow_html=True)
            market_sel = st.selectbox(
                "Target market",
                list(MARKET_REF.keys()),
                help="Select the market you are entering. B2B ceiling is derived from observed per-10B retail/wholesale data.",
            )
            mfg_context_sel = st.selectbox(
                "Product grade / manufacturing context",
                list(COGS_BY_CONTEXT.keys()),
                index=0,
                help="Match to the market tier you selected. 🧴 aesthetic markets → cosmetic/professional grade. 💊 therapeutic markets → clinical GMP.",
            )
            ctx = COGS_BY_CONTEXT[mfg_context_sel]
            st.markdown(
                f'<div class="signal-card" style="font-size:0.82rem;padding:8px 12px;">'
                f'ℹ️ {ctx["note"]}</div>',
                unsafe_allow_html=True,
            )
            st.markdown("")
            cogs_scale_sel = st.selectbox(
                "Production scale / year",
                list(ctx["scales"].keys()),
                index=min(1, len(ctx["scales"]) - 1),
                help="Select your production scale within the chosen manufacturing context.",
            )
            scale_vals = ctx["scales"][cogs_scale_sel]
            if scale_vals["mid"] is None:
                custom_cogs = st.number_input(
                    "Your COGS per 10B particles (USD)",
                    min_value=10, max_value=5000, value=500, step=10,
                )
                cogs_mid = custom_cogs
                cogs_lo  = int(custom_cogs * 0.85)
                cogs_hi  = int(custom_cogs * 1.15)
            else:
                cogs_mid = scale_vals["mid"]
                cogs_lo  = scale_vals["lo"]
                cogs_hi  = scale_vals["hi"]

            target_margin = st.slider(
                "Target gross margin %",
                min_value=20, max_value=80, value=50, step=5,
                help="Gross margin = (B2B price − COGS) / B2B price × 100",
            )
            particles_per_vial_sc = st.number_input(
                "Vial particle count (Billions) — for per-vial output",
                min_value=1, max_value=100, value=10, step=1,
            )

        with col_inp2:
            st.markdown('<div class="section-subheader">📊 Results</div>', unsafe_allow_html=True)
            mkt    = MARKET_REF[market_sel]
            # Warn if product grade and market tier are mismatched
            mkt_tier  = mkt.get("tier", "aesthetic")
            is_therapeutic_cogs = "Clinical therapeutic" in mfg_context_sel
            is_therapeutic_mkt  = mkt_tier == "therapeutic"
            if is_therapeutic_cogs and not is_therapeutic_mkt:
                st.markdown(
                    '<div class="warning-card">⚠️ <strong>Tier mismatch:</strong> Clinical therapeutic GMP COGS paired with an aesthetic market. '
                    'Switch to a 💊 therapeutic market or a lower-cost product grade for a meaningful comparison.</div>',
                    unsafe_allow_html=True,
                )
            elif not is_therapeutic_cogs and is_therapeutic_mkt:
                st.markdown(
                    '<div class="signal-card">ℹ️ <strong>Note:</strong> Cosmetic/professional grade COGS in a therapeutic market — '
                    'this is optimistic; therapeutic buyers typically require clinical GMP documentation.</div>',
                    unsafe_allow_html=True,
                )
            b2b_lo = mkt["b2b_lo"]
            b2b_hi = mkt["b2b_hi"]
            b2b_mid = (b2b_lo + b2b_hi) / 2

            # Actual margin at current COGS
            actual_margin_pct = ((b2b_mid - cogs_mid) / b2b_mid * 100) if b2b_mid > 0 else -999

            # COGS required to hit target margin at this B2B price
            req_cogs_for_margin = b2b_mid * (1 - target_margin / 100)

            # B2B price needed to hit target margin at current COGS
            req_b2b_for_margin = cogs_mid / (1 - target_margin / 100) if target_margin < 100 else float("inf")

            # Per-vial values
            vial_b2b_mid = (b2b_mid / 10) * particles_per_vial_sc
            vial_cogs    = (cogs_mid / 10) * particles_per_vial_sc

            # Viability assessment
            is_viable  = actual_margin_pct >= target_margin
            gap_to_viable = req_cogs_for_margin - cogs_mid  # positive = need to reduce COGS

            if is_viable:
                result_cls  = "success-card"
                result_icon = "✅"
                result_msg  = f"<strong>Viable at this scale.</strong> Actual margin ({actual_margin_pct:.1f}%) exceeds target ({target_margin}%)."
            elif actual_margin_pct > 0:
                result_cls  = "warning-card"
                result_icon = "⚠️"
                result_msg  = (
                    f"<strong>Profitable but below target margin.</strong> "
                    f"Actual margin: {actual_margin_pct:.1f}% vs target {target_margin}%. "
                    f"Reduce COGS by ${abs(gap_to_viable):,.0f}/10B to hit target."
                )
            else:
                result_cls  = "critical-card"
                result_icon = "🔴"
                result_msg  = (
                    f"<strong>Not yet profitable at this scale.</strong> "
                    f"COGS (${cogs_mid:,}/10B) exceeds B2B ceiling (${b2b_mid:,.0f}/10B). "
                    f"Need to reduce COGS by ${abs(gap_to_viable):,.0f}/10B to break even, "
                    f"${abs(cogs_mid - req_cogs_for_margin):,.0f}/10B to reach {target_margin}% margin."
                )

            st.markdown(
                f'<div class="{result_cls}">{result_icon} {result_msg}</div>',
                unsafe_allow_html=True,
            )
            st.markdown("")

            # ── KPI cards ────────────────────────────────────────
            kpi_r = [
                (f"${b2b_lo}–${b2b_hi}", "B2B Ceiling/10B", f"{mkt['flag']} {market_sel}"),
                (f"${cogs_mid:,}", "Your COGS/10B", cogs_scale_sel.split("(")[0].strip()[:28]),
                (f"{actual_margin_pct:.1f}%", "Actual Gross Margin", "at B2B midpoint"),
                (f"${req_cogs_for_margin:,.0f}", f"COGS Needed for {target_margin}% Margin", "per 10B particles"),
                (f"${vial_b2b_mid:,.0f}", f"B2B per vial ({particles_per_vial_sc}B)", "at market midpoint"),
                (f"${req_b2b_for_margin:,.0f}", f"B2B Needed for {target_margin}% Margin", "per 10B particles"),
            ]
            kpi_cols = st.columns(3)
            for i, (val, label, sub) in enumerate(kpi_r):
                kpi_cols[i % 3].markdown(
                    f'<div class="metric-card" style="margin-bottom:8px;">'
                    f'<div class="metric-value" style="font-size:1.4rem;">{val}</div>'
                    f'<div class="metric-label">{label}</div>'
                    f'<div class="metric-sub">{sub}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        # ── Waterfall: COGS → B2B → End-user price ────────────────
        st.markdown("")
        st.markdown('<div class="section-header">Price Waterfall — COGS to End-User</div>', unsafe_allow_html=True)
        end_lo = mkt["end_user_lo"]
        end_hi = mkt["end_user_hi"]
        end_mid = (end_lo + end_hi) / 2

        waterfall_df = pd.DataFrame({
            "Stage":   ["Your COGS/10B", f"B2B to Distributor\n({market_sel})", "Distributor Markup\n(~30%)", f"End-User/Vial\n({market_sel})"],
            "Value":   [cogs_mid, b2b_mid, b2b_mid * 0.3, end_mid],
            "Color":   ["#e05c2a", "#2e6da4", "#7ec8e3", "#1e3a5f"],
        })
        fig_wf = go.Figure(go.Bar(
            x=waterfall_df["Stage"],
            y=waterfall_df["Value"],
            marker_color=waterfall_df["Color"],
            text=[f"${v:,.0f}" for v in waterfall_df["Value"]],
            textposition="outside",
        ))
        fig_wf.update_layout(
            height=360, margin=dict(t=20, b=20),
            yaxis_title="USD per 10B particles", showlegend=False,
        )
        st.plotly_chart(fig_wf, use_container_width=True)
        st.caption("Distributor markup (30%) is indicative. End-user price per vial is an estimate from per-treatment OOP data ÷ typical session counts. COGS will vary with production scale.")

        # ── Break-even COGS trajectory ────────────────────────────
        st.markdown('<div class="section-header">All Markets — Break-Even COGS Required for Target Margin</div>', unsafe_allow_html=True)
        bev_rows = []
        for mkt_name, mkt_vals in MARKET_REF.items():
            b2b_m = (mkt_vals["b2b_lo"] + mkt_vals["b2b_hi"]) / 2
            req   = b2b_m * (1 - target_margin / 100)
            curr_margin = ((b2b_m - cogs_mid) / b2b_m * 100) if b2b_m > 0 else -999
            bev_rows.append({
                "Market": f"{mkt_vals['flag']} {mkt_name}",
                "B2B Mid ($/10B)":  round(b2b_m),
                f"COGS Needed for {target_margin}% Margin": round(req),
                "Your COGS": cogs_mid,
                "Margin Gap": round(req - cogs_mid),
                "Current Margin %": round(curr_margin, 1),
                "Status": "✅ Viable" if curr_margin >= target_margin else ("🟡 Below target" if curr_margin > 0 else "🔴 Loss"),
            })
        bev_df = pd.DataFrame(bev_rows).sort_values("B2B Mid ($/10B)", ascending=False)

        fig_bev = go.Figure()
        colors_bev = ["#3db07a" if r["Current Margin %"] >= target_margin
                      else ("#f0a030" if r["Current Margin %"] > 0 else "#c62828")
                      for _, r in bev_df.iterrows()]
        fig_bev.add_trace(go.Bar(
            x=bev_df[f"COGS Needed for {target_margin}% Margin"],
            y=bev_df["Market"],
            orientation="h",
            marker_color=colors_bev,
            text=[f"${v:,}" for v in bev_df[f"COGS Needed for {target_margin}% Margin"]],
            textposition="outside",
            name="Required COGS",
        ))
        fig_bev.add_vline(
            x=cogs_mid, line_dash="dash", line_color="#1e3a5f", line_width=2,
            annotation_text=f"Your COGS: ${cogs_mid:,}/10B",
            annotation_position="top right",
            annotation_font_color="#1e3a5f",
        )
        fig_bev.update_layout(
            height=340, margin=dict(t=20, b=20),
            xaxis_title=f"Required COGS to achieve {target_margin}% gross margin (USD/10B)",
            yaxis_title="", showlegend=False,
            title=f"Markets where your COGS (${cogs_mid:,}/10B) is left of the bar are profitable",
        )
        st.plotly_chart(fig_bev, use_container_width=True)

        st.dataframe(
            bev_df[["Market","B2B Mid ($/10B)", f"COGS Needed for {target_margin}% Margin",
                    "Your COGS", "Margin Gap", "Current Margin %", "Status"]],
            hide_index=True, use_container_width=True,
        )
        st.caption(
            f"🔵 Vertical line = your current COGS. Markets where the bar extends past the line can support "
            f"a {target_margin}% gross margin at current pricing. 🟢 = Viable | 🟡 = Below target | 🔴 = Loss-making. "
            f"Improve profitability by increasing production scale (reduces COGS) or entering higher-ceiling markets first."
        )

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
        ("Silva RM et al.", "Enabling MSC and MSC-EVs Clinical Availability — J Extracell Biol 2025 (PMC11913891)", "Primary COGS anchor: UC-MSC selling price €166–309/10¹⁰ dose; COGS = selling price ÷ 1.36 ROI = $135–252. BM-MSC +15–25% → $155–315. Open-access TECoA."),
        ("Ng KS et al.", "Bioprocess decision support tool for scalable EV manufacture — Biotechnol Bioeng 2019 (PMC6322973)", "EV harvest >50% of total COG; labor dominates harvest costs; media base $150/L; labor $200/hr; biological yield = strongest cost driver."),
        ("Lembong J et al.", "Bioreactor Parameters for Microcarrier-Based MSC Expansion — Bioengineering 2020 (PMC7552727)", "Primary source for $1M/lot of 5×10¹² EVs = ~$8,000/dose at 125 doses/lot (research scale)."),
        ("RoosterBio (Lenzini)", "EV/Exosome Upstream Process Development blog, Apr 2022", "Research-scale anchor: $1M/lot, 125 dose regimens, ~$8,000/dose. Labor $200/hr. Suite $200K–$1M/month."),
        ("RoosterBio (Candiello & Takacs)", "Balancing the Scale from the Cellular Bank blog, Aug 2025", "GMP labor $50K/operational day; $150K/lot release testing; Phase I GMP <$1M total; cell bank build $1.5–3M."),
        ("Corning / Cell & Gene Therapy Insights", "MSC Manufacturing Expert Roundtable, Mar 2025 (recorded Feb 13 2025)", "Qualitative: MSC manufacturing COGs are a key barrier; media, bioreactor, and potency assay costs discussed. No specific cost figures published."),
        ("QY Research", "Exosome Lyophilization Global Market Forecast 2026–2032", "Lyophilization segment $50–60M → low hundreds of millions by early 2030s"),
        ("Frontiers in Pharmacology", "Trends in MSC-EV Clinical Trials 2014–2024, Wang et al. 2025", "Dose estimates per indication; clinical trial dosing review"),
        ("RoosterBio (Lenzini et al.)", "EV Bioprocess Design and Economic Modeling — Cytotherapy 2024 abstract (ScienceDirect S1465-3249(24)002238)", "Downstream (TFF + AEX polishing) ≈10% of total COG; upstream ≈90%; media ≈50% of upstream cost. 15% EV recovery at 1,000 EVs/MSC modeled across 2–150L scales. Key driver: cell expansion media + labor."),
        ("IST Lisbon (Silva RM et al.)", "Operational and economic evaluation of future MSC-EV therapies — ibb.tecnico.ulisboa.pt, 2025", "Facility and labor are non-negligible contributors alongside media/consumables. COG and therapy price sensitive to dose definition, recovery, and scale. Confirms upstream-dominated cost structure."),
        ("PMC5895685", "Manufacturing human mesenchymal stem cells at clinical scale — mini-review (Heathman et al.)", "Upstream hMSC expansion is the main cost driver; 3D bioreactor with microcarriers required for 10¹³-cell batches. Strongly supports media + labor dominating EV process COG even before DSP."),
        ("RoosterBio (Candiello)", "How DSP Decisions Shape Scale, Yield, and Cost of Goods in Exosome Preparation — blog 2025", "Legacy non-optimized: ≥$200/10B EV (≥$1M/lot of 5×10¹² EVs). Optimized 3D process: <$25/10B EV (<$250/dose at 10¹¹/dose). NurExone-style ATMP overhead adds ≈$10–35/10B → synthesis range ≈$25–60/10B (Jun 2026)."),
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
        {"date":"May 2024",    "type":"Regulatory",  "event":"Utah SB 199 — non-FDA-approved placental/perinatal cell therapies permitted with informed consent", "impact":"Booming clinic ecosystem in SLC/Sandy/Park City; active exosome use observed at R3 Stem Cell, Utah Stem Cells, Movement Clinic. ⚠️ BM-MSC not explicitly covered — higher risk than FL", "sentiment":"🟡 Neutral",  "territory":"USA — Utah", "source":"Utah SB 199 signed by Gov. Cox March 2024, eff. May 1 2024; Celmedica state guide; ipscell.com legal analysis"},
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
        "source":"Source","date_added":"Date Added",
    })

    # ── NEW flag: mark signals added after prev_last_run ─────────
    def _is_new(row):
        da = str(row.get("Date Added", "") or "").strip()
        if not da or not prev_last_run:
            return False
        try:
            import datetime as _dt
            added = _dt.date.fromisoformat(da[:10])
            prev  = _dt.date.fromisoformat(prev_last_run[:10])
            return added > prev
        except Exception:
            return False

    signals_display["🆕"] = signals_display.apply(_is_new, axis=1).map(
        {True: "🆕 NEW", False: ""}
    )
    new_count = (signals_display["🆕"] == "🆕 NEW").sum()

    col_sm = st.columns(5)
    col_sm[0].metric("🟢 Positive Signals", len(signals_display[signals_display["Sentiment"].str.contains("Positive", na=False)]))
    col_sm[1].metric("🔴 Risk Signals",     len(signals_display[signals_display["Sentiment"].str.contains("Risk",     na=False)]))
    col_sm[2].metric("🟡 Neutral/Watch",    len(signals_display[signals_display["Sentiment"].str.contains("Neutral",  na=False)]))
    col_sm[3].metric("📋 Total Tracked",    len(signals_display))
    col_sm[4].metric("🆕 New This Update",  int(new_count))

    type_filter = st.multiselect(
        "Filter by Signal Type",
        options=sorted(signals_display["Type"].dropna().unique().tolist()),
        default=sorted(signals_display["Type"].dropna().unique().tolist()),
    )

    display_cols = [c for c in ["🆕","Date","Type","Event","Impact","Sentiment","Territory","Source"] if c in signals_display.columns]
    st.dataframe(
        signals_display[signals_display["Type"].isin(type_filter)][display_cols],
        hide_index=True, use_container_width=True, height=320,
    )
    st.caption("🆕 NEW = added since last auto-update run. Flag clears automatically on the next update cycle. Source column shows citation for manually curated baseline signals.")

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
            ("💊 COGS Collapses with Scale", "Research scale $9,500/dose → Commercial mid $225/dose (2026, S1+G2) → Industrial $80/dose (2030) — scale-up is the primary lever, not time."),
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
         "Florida §456.47 provides structured informed-consent pathway for elective physician use — explicitly covers exosome products. Nevada SB128/AB148 similarly permits licensed physician use. Direct-to-clinic in FL/NV medspas captures the $1.2B Florida medspa market while remaining federally compliant — no therapeutic claims. "
         "Utah SB 199 (eff. May 2024) also permits non-FDA-approved cell therapies but specifically covers placental/perinatal sources — BM-MSC exosomes are NOT explicitly covered. Utah's active wellness clinic ecosystem (SLC, Sandy, Park City) is accessible via the cosmetic topical channel only for BM-MSC."),
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

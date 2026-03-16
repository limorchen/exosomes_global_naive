"""
Global Naive MSC Exosome Market Dashboard
Run with: streamlit run market_dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(layout="wide", page_title="Global Exosome Market Dashboard", page_icon="🧬")

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #1e3a5f, #2e6da4);
        border-radius: 10px; padding: 16px; color: white; text-align: center;
    }
    .metric-value { font-size: 1.8rem; font-weight: bold; color: #7ec8e3; }
    .metric-label { font-size: 0.85rem; opacity: 0.85; margin-top: 4px; }
    .section-header {
        background: linear-gradient(90deg, #1e3a5f, #2e6da4);
        color: white; padding: 8px 16px; border-radius: 6px;
        font-size: 1.1rem; font-weight: bold; margin: 12px 0 8px 0;
    }
    .signal-card {
        border-left: 4px solid #2e6da4; background: #f0f6ff;
        padding: 10px 14px; border-radius: 4px; margin: 6px 0;
    }
    .warning-card {
        border-left: 4px solid #e05c2a; background: #fff3ee;
        padding: 10px 14px; border-radius: 4px; margin: 6px 0;
    }
</style>
""", unsafe_allow_html=True)

st.title("🧬 Global Naive MSC Exosome Market")
st.caption("Strategic mapping of regulatory architecture, distribution networks, and commercial entry points")

# ── Tab layout ────────────────────────────────────────────────────────────────
tabs = st.tabs([
    "📊 Market Overview",
    "🗺️ Geographic Analysis",
    "🏢 Distributors",
    "⚖️ Regulation",
    "💰 Pricing",
    "📡 Signals & Trends"
])

# ════════════════════════════════════════════════════════════════════════
# TAB 1 — MARKET OVERVIEW
# ════════════════════════════════════════════════════════════════════════
with tabs[0]:
    st.markdown('<div class="section-header">Global Market KPIs</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    kpis = [
        ("$177.4M", "Market Size (2024)"),
        ("$794.2M", "Projected Size (2030)"),
        ("28.73%", "CAGR 2025–2030"),
        ("~$2,500", "Cost/Dose (2026)"),
    ]
    for col, (val, label) in zip([c1,c2,c3,c4], kpis):
        col.markdown(f'<div class="metric-card"><div class="metric-value">{val}</div><div class="metric-label">{label}</div></div>', unsafe_allow_html=True)

    st.markdown("")

    # Regional share
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown('<div class="section-header">Regional Market Share</div>', unsafe_allow_html=True)
        region_df = pd.DataFrame({
            "Region": ["North America", "Europe", "Asia-Pacific", "Latin America", "Middle East & Africa"],
            "Share (%)": [56.55, 26.0, 24.0, 8.5, 5.0],
            "Key Driver": [
                "R&D infrastructure & funding",
                "Aesthetic & wellness adoption",
                "K-beauty & biotech investment",
                "Medical tourism & aesthetic procedures",
                "Luxury longevity & wellness clinics"
            ]
        })
        fig = px.pie(region_df, names="Region", values="Share (%)",
                     color_discrete_sequence=["#1e3a5f","#2e6da4","#7ec8e3"],
                     hole=0.4)
        fig.update_traces(textposition="outside", textinfo="percent+label")
        fig.update_layout(margin=dict(t=20,b=20), showlegend=False, height=300)
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(region_df, hide_index=True, use_container_width=True)

    with col_b:
        st.markdown('<div class="section-header">Market Segmentation by Product</div>', unsafe_allow_html=True)
        seg_df = pd.DataFrame({
            "Segment": ["Kits & Reagents", "Cancer Research", "Other Applications"],
            "Share (%)": [45.68, 32.76, 21.56]
        })
        fig2 = px.bar(seg_df, x="Share (%)", y="Segment", orientation="h",
                      color="Share (%)", color_continuous_scale=["#7ec8e3","#1e3a5f"],
                      text="Share (%)")
        fig2.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig2.update_layout(margin=dict(t=20,b=20), coloraxis_showscale=False,
                           height=300, yaxis_title="")
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown('<div class="section-header">COGS Trajectory</div>', unsafe_allow_html=True)
        cogs_df = pd.DataFrame({
            "Year": [2023, 2026, 2030],
            "Cost per Dose (USD)": [5000, 2500, 500]
        })
        fig3 = px.line(cogs_df, x="Year", y="Cost per Dose (USD)",
                       markers=True, color_discrete_sequence=["#2e6da4"])
        fig3.update_layout(margin=dict(t=10,b=10), height=200)
        st.plotly_chart(fig3, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════
# TAB 2 — GEOGRAPHIC ANALYSIS
# ════════════════════════════════════════════════════════════════════════
with tabs[1]:
    st.markdown('<div class="section-header">Market Maturity by Region</div>', unsafe_allow_html=True)

    geo_df = pd.DataFrame([
        {"Region": "Europe",         "Market Stage": "Established",  "Primary Segment": "Aesthetic/Wellness",  "Regulatory Risk": "Medium", "OOP Dominant": True,  "CAGR Est.": 18},
        {"Region": "Latin America",  "Market Stage": "Growing",      "Primary Segment": "Medical Tourism",      "Regulatory Risk": "Medium", "OOP Dominant": True,  "CAGR Est.": 24},
        {"Region": "Southeast Asia", "Market Stage": "Emerging",     "Primary Segment": "K-Beauty / Aesthetic", "Regulatory Risk": "Low",    "OOP Dominant": True,  "CAGR Est.": 28},
        {"Region": "UAE / GCC",      "Market Stage": "Niche/Premium","Primary Segment": "Longevity / Luxury",   "Regulatory Risk": "Low",    "OOP Dominant": True,  "CAGR Est.": 22},
        {"Region": "Australia",      "Market Stage": "Established",  "Primary Segment": "Medical",              "Regulatory Risk": "High",   "OOP Dominant": False, "CAGR Est.": 15},
        {"Region": "North America",  "Market Stage": "Restricted",   "Primary Segment": "Research",             "Regulatory Risk": "High",   "OOP Dominant": False, "CAGR Est.": 12},
    ])

    fig_geo = px.scatter(geo_df, x="CAGR Est.", y="Regulatory Risk",
                         size=[40]*6,
                         color="Market Stage",
                         text="Region",
                         color_discrete_sequence=["#1e3a5f","#2e6da4","#7ec8e3","#b3dff0","#e05c2a","#f0a07a"],
                         title="Market Opportunity vs Regulatory Risk")
    fig_geo.update_traces(textposition="top center", marker=dict(sizemode="diameter"))
    fig_geo.update_layout(height=420, xaxis_title="Estimated CAGR (%)", yaxis_title="Regulatory Barrier")
    st.plotly_chart(fig_geo, use_container_width=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<div class="section-header">Europe</div>', unsafe_allow_html=True)
        eur = pd.DataFrame([
            {"Country": "Germany",     "Maturity": "High",   "Key Segment": "Clinical Aesthetic",   "Entry Barrier": "Medium"},
            {"Country": "France",      "Maturity": "High",   "Key Segment": "Medical Spa",          "Entry Barrier": "Medium"},
            {"Country": "Switzerland", "Maturity": "Medium", "Key Segment": "Longevity Clinics",    "Entry Barrier": "High"},
            {"Country": "Austria",     "Maturity": "Medium", "Key Segment": "Aesthetic Devices",    "Entry Barrier": "Medium"},
            {"Country": "Italy",       "Maturity": "Medium", "Key Segment": "Specialist Networks",  "Entry Barrier": "Medium"},
            {"Country": "Poland/CEE",  "Maturity": "Low",    "Key Segment": "Emerging Aesthetics",  "Entry Barrier": "Low"},
        ])
        st.dataframe(eur, hide_index=True, use_container_width=True)

    with col2:
        st.markdown('<div class="section-header">Asia-Pacific & LATAM</div>', unsafe_allow_html=True)
        apac = pd.DataFrame([
            {"Territory": "Philippines",  "Region": "SEA",    "Maturity": "Emerging", "CAGR Note": "ASEAN gateway"},
            {"Territory": "Malaysia",     "Region": "SEA",    "Maturity": "Medium",   "CAGR Note": "16.2% research CAGR"},
            {"Territory": "Indonesia",    "Region": "SEA",    "Maturity": "Early",    "CAGR Note": "Clinic training focus"},
            {"Territory": "Australia",    "Region": "Pacific","Maturity": "High",     "CAGR Note": "TGA high standards"},
            {"Territory": "Brazil",       "Region": "LATAM",  "Maturity": "High",     "CAGR Note": "2nd largest aesthetic"},
            {"Territory": "Mexico",       "Region": "LATAM",  "Maturity": "High",     "CAGR Note": "Medical tourism hub"},
            {"Territory": "UAE / GCC",    "Region": "ME",     "Maturity": "Premium",  "CAGR Note": "Luxury longevity"},
        ])
        st.dataframe(apac, hide_index=True, use_container_width=True)

    st.markdown('<div class="section-header">End User Profile by Region</div>', unsafe_allow_html=True)

    end_users = pd.DataFrame([
        {"Region": "Europe",         "Primary End User": "Dermatologists / Medical Spas",      "Secondary End User": "Aesthetic Chains",       "Application": "Post-procedure recovery"},
        {"Region": "Latin America",  "Primary End User": "Medical Tourism Clinics",             "Secondary End User": "Specialist Orthopedics", "Application": "Aesthetic + ortho"},
        {"Region": "SEA",            "Primary End User": "Aesthetic Clinics / K-beauty",        "Secondary End User": "Research Institutions",  "Application": "Skin rejuvenation"},
        {"Region": "UAE / GCC",      "Primary End User": "Luxury Longevity Clinics",            "Secondary End User": "High-Net-Worth Individuals","Application": "Systemic IV longevity"},
        {"Region": "Australia",      "Primary End User": "TGA-registered Clinics",              "Secondary End User": "Sports Medicine",         "Application": "Medical regenerative"},
    ])
    st.dataframe(end_users, hide_index=True, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════
# TAB 3 — DISTRIBUTORS
# ════════════════════════════════════════════════════════════════════════
with tabs[2]:
    st.markdown('<div class="section-header">Key Global Distributors</div>', unsafe_allow_html=True)

    dist_df = pd.DataFrame([
        {"Distributor": "Jolifill",              "Region": "Europe",    "Territory": "Germany",        "Brands": "EXOXE, EXOMIDE, EXOJUV",      "Approach": "Direct e-commerce + professional"},
        {"Distributor": "Croma-Pharma",          "Region": "Europe",    "Territory": "Austria/DACH",   "Brands": "Aesthetic Mgmt Partners",     "Approach": "Strategic regional partnerships"},
        {"Distributor": "Teoxane France",        "Region": "Europe",    "Territory": "France",         "Brands": "Teoxane proprietary",         "Approach": "Direct subsidiary model"},
        {"Distributor": "Taumedika S.r.l.",      "Region": "Europe",    "Territory": "Italy",          "Brands": "Karisma Exo Care",            "Approach": "Specialist aesthetic networks"},
        {"Distributor": "Teoxane Polska",        "Region": "Europe",    "Territory": "Poland/CEE",     "Brands": "EPICEXOSOME",                 "Approach": "Emerging market expansion"},
        {"Distributor": "Giostar Mexico",        "Region": "LATAM",     "Territory": "Mexico (Cancun)","Brands": "Multiple MSC brands",         "Approach": "Medical tourism + ortho"},
        {"Distributor": "PRMEDICA",              "Region": "LATAM",     "Territory": "Mexico (Cabos)", "Brands": "MSC exosomes",                "Approach": "Inflammatory modulation"},
        {"Distributor": "R3 Stem Cell Brazil",   "Region": "LATAM",     "Territory": "Brazil",         "Brands": "R3 proprietary",              "Approach": "Centers of Excellence"},
        {"Distributor": "Vanguard Aesthetics",   "Region": "SEA",       "Territory": "Philippines",    "Brands": "Innovative med-aesthetic",    "Approach": "ASEAN hub strategy"},
        {"Distributor": "MGRC / GGA Malaysia",   "Region": "SEA",       "Territory": "Malaysia",       "Brands": "cGMP MSC exosomes",           "Approach": "Research + diagnostics"},
        {"Distributor": "PT. Sel Regenerasi",    "Region": "SEA",       "Territory": "Indonesia",      "Brands": "Local brands",                "Approach": "Physician clinic training"},
        {"Distributor": "Biogenix / InterMed",   "Region": "Pacific",   "Territory": "Australia",      "Brands": "Cervos KeyPRP, Marrow Cell",  "Approach": "TGA-compliant partnership"},
        {"Distributor": "DUBIMED",               "Region": "UAE/GCC",   "Territory": "UAE/Qatar/Oman", "Brands": "Galderma, Mesoestetic",       "Approach": "Exclusive 40yr relationships"},
        {"Distributor": "Troya Aesthetics",      "Region": "UAE/GCC",   "Territory": "UAE",            "Brands": "Premium regional",            "Approach": "Dermatologist patient care"},
        {"Distributor": "EDEN AESTHETICS",       "Region": "UAE/GCC",   "Territory": "Dubai",          "Brands": "Integrative exosome protocol","Approach": "High-dose IV longevity"},
    ])

    region_filter = st.multiselect("Filter by Region", options=dist_df["Region"].unique(), default=list(dist_df["Region"].unique()))
    filtered = dist_df[dist_df["Region"].isin(region_filter)]
    st.dataframe(filtered, hide_index=True, use_container_width=True)

    st.markdown('<div class="section-header">Distributor Count by Region</div>', unsafe_allow_html=True)
    dist_count = dist_df.groupby("Region").size().reset_index(name="Count")
    fig_dist = px.bar(dist_count, x="Region", y="Count", color="Region",
                      color_discrete_sequence=["#1e3a5f","#2e6da4","#7ec8e3","#b3dff0","#e05c2a"],
                      text="Count")
    fig_dist.update_traces(textposition="outside")
    fig_dist.update_layout(showlegend=False, height=300, margin=dict(t=10,b=10))
    st.plotly_chart(fig_dist, use_container_width=True)

    st.markdown('<div class="section-header">How to Approach Key Distributors</div>', unsafe_allow_html=True)
    approach_data = {
        "🇦🇪 UAE — DUBIMED": "Emphasise clinical credibility + longevity angle. Offer a 'longevity module' fitting their existing aesthetic infrastructure. 40yr reputation means they value established brands.",
        "🇪🇺 Europe — Croma-Pharma / Teoxane": "Focus on premium aesthetic segment. Lead with 'clinically-inspired' post-procedure skin recovery data. Croma-Pharma actively seeking new regenerative brands.",
        "🌎 LATAM — Giostar / R3 Stem Cell": "Leverage medical tourism angle. Offer lyophilised products solving Mexican-Brazilian cold-chain logistics. Emphasise purity + potency exceeding FDA standards.",
        "🌏 SEA — Vanguard Aesthetics": "Use Philippines as initial hub. Philippine FDA cosmetic notification signals ASEAN compliance — makes product immediately attractive regionally.",
    }
    for title, text in approach_data.items():
        st.markdown(f'<div class="signal-card"><strong>{title}</strong><br>{text}</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════
# TAB 4 — REGULATION
# ════════════════════════════════════════════════════════════════════════
with tabs[3]:
    st.markdown('<div class="section-header">Regulatory Framework by Territory</div>', unsafe_allow_html=True)

    reg_df = pd.DataFrame([
        {"Territory": "EU",          "Body": "EMA",      "Classification": "ATMP (therapeutic) / Cosmetic",   "Key Regulation": "Reg. (EC) 1394/2007",        "Status": "No exosome ATMP authorized yet",      "Risk Level": "High"},
        {"Territory": "Germany",     "Body": "BfArM",    "Classification": "Cosmetic / Medical Device",        "Key Regulation": "EU Cosmetics Regulation",    "Status": "Active aesthetic market",             "Risk Level": "Medium"},
        {"Territory": "France",      "Body": "ANSM",     "Classification": "Cosmetic (topical)",               "Key Regulation": "No therapeutic claims",      "Status": "Medical spa adoption",                "Risk Level": "Medium"},
        {"Territory": "Switzerland", "Body": "Swissmedic","Classification": "Early clinical registration",     "Key Regulation": "Swiss MedDO",                "Status": "High-value niche market",             "Risk Level": "Medium"},
        {"Territory": "Brazil",      "Body": "ANVISA",   "Classification": "Medical / Cosmetic Grade",         "Key Regulation": "RDC 751/2022; RDC 949/2024", "Status": "Requires AFE + local IOR",            "Risk Level": "Medium"},
        {"Territory": "Mexico",      "Body": "COFEPRIS", "Classification": "Biologic / Complementary",         "Key Regulation": "GMP for Biologics",          "Status": "MoU reliance with ANVISA",            "Risk Level": "Low"},
        {"Territory": "Colombia",    "Body": "INVIMA",   "Classification": "Regional Reform",                  "Key Regulation": "2025 Reform",                "Status": "Aligning with LATAM integration",     "Risk Level": "Low"},
        {"Territory": "Argentina",   "Body": "ANMAT",    "Classification": "Streamlined",                      "Key Regulation": "2025 Deregulation",          "Status": "Fast-track market entry",             "Risk Level": "Low"},
        {"Territory": "Philippines", "Body": "Philippine FDA","Classification": "Cosmetic Notification",       "Key Regulation": "ASEAN Cosmetic Directive",   "Status": "✅ Approved (Jan 2026)",               "Risk Level": "Low"},
        {"Territory": "Malaysia",    "Body": "NPRA",     "Classification": "Research / Cosmetic",              "Key Regulation": "ASEAN aligned",              "Status": "cGMP production active",              "Risk Level": "Low"},
        {"Territory": "Indonesia",   "Body": "BPOM",     "Classification": "Medical Aesthetic",                "Key Regulation": "BPOM engaged",               "Status": "Physician training pathway",          "Risk Level": "Low"},
        {"Territory": "Australia",   "Body": "TGA",      "Classification": "Therapeutic Good / ATMP",         "Key Regulation": "TGA high standards",         "Status": "PBAC risk-sharing for ATMPs",         "Risk Level": "High"},
        {"Territory": "UAE",         "Body": "MOHAP/DHA","Classification": "Cosmetic + Advanced Procedures",  "Key Regulation": "DHCA guidelines",            "Status": "Strict cosmetic procedure standards", "Risk Level": "Medium"},
    ])

    risk_colors = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}
    reg_df["Risk"] = reg_df["Risk Level"].map(risk_colors) + " " + reg_df["Risk Level"]

    st.dataframe(reg_df[["Territory","Body","Classification","Key Regulation","Status","Risk"]], hide_index=True, use_container_width=True)

    col_r1, col_r2 = st.columns(2)

    with col_r1:
        st.markdown('<div class="section-header">Regulatory Risk Distribution</div>', unsafe_allow_html=True)
        risk_count = reg_df["Risk Level"].value_counts().reset_index()
        risk_count.columns = ["Risk Level", "Count"]
        fig_risk = px.pie(risk_count, names="Risk Level", values="Count",
                          color="Risk Level",
                          color_discrete_map={"High":"#e05c2a","Medium":"#f0c040","Low":"#4caf50"},
                          hole=0.4)
        fig_risk.update_layout(height=280, margin=dict(t=10,b=10))
        st.plotly_chart(fig_risk, use_container_width=True)

    with col_r2:
        st.markdown('<div class="section-header">Key Regulatory Milestones</div>', unsafe_allow_html=True)
        milestones = [
            ("✅ Jan 2026", "Philippines FDA cosmetic notification — validates ASEAN entry"),
            ("✅ Late 2025", "ANVISA-COFEPRIS MoU — streamlines Brazil↔Mexico approvals"),
            ("✅ Mar 2024", "Croma-Pharma distribution deal — confirms EU market appetite"),
            ("⚠️ 2025/26",  "FDA warning letters on 'hair loss' claims — shift to cosmetic labeling"),
            ("⚠️ Ongoing",  "EU: <2 dozen ATMPs authorized, zero exosome-based — gap to exploit"),
        ]
        for date, text in milestones:
            style = "warning-card" if "⚠️" in date else "signal-card"
            st.markdown(f'<div class="{style}"><strong>{date}</strong> — {text}</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-header">ANVISA–COFEPRIS Strategic Alliance</div>', unsafe_allow_html=True)
    st.info("🤝 Brazil and Mexico signed an MoU establishing mutual recognition for medicines, medical devices, and GMP. Mexico has designated ANVISA as a 'Reference Regulatory Authority'; Brazil recognizes COFEPRIS as an 'Equivalent Foreign Regulatory Authority'. Securing approval in one territory significantly streamlines entry into the other.")

# ════════════════════════════════════════════════════════════════════════
# TAB 5 — PRICING
# ════════════════════════════════════════════════════════════════════════
with tabs[4]:
    st.markdown('<div class="section-header">Pricing by Indication Segment (OOP, 2025)</div>', unsafe_allow_html=True)

    price_df = pd.DataFrame([
        {"Segment": "Longevity (Systemic IV)",  "Low": 5000, "High": 10000, "Midpoint": 7500,  "Primary Markets": "UAE, Australia, USA"},
        {"Segment": "Pure Medical (IV/Joint)",  "Low": 3750, "High": 5500,  "Midpoint": 4625,  "Primary Markets": "Mexico, Brazil, EU"},
        {"Segment": "Hair Restoration",         "Low": 900,  "High": 2300,  "Midpoint": 1600,  "Primary Markets": "UAE, SEA, EU"},
        {"Segment": "Aesthetics (Topical)",     "Low": 750,  "High": 1500,  "Midpoint": 1125,  "Primary Markets": "EU, SEA, UAE"},
        {"Segment": "Regen-Medical (Wounds)",   "Low": 1500, "High": 4000,  "Midpoint": 2750,  "Primary Markets": "EU, Australia"},
    ])

    fig_price = go.Figure()
    for _, row in price_df.iterrows():
        fig_price.add_trace(go.Bar(
            name=row["Segment"], x=[row["Segment"]],
            y=[row["High"] - row["Low"]],
            base=[row["Low"]],
            marker_color=["#1e3a5f","#2e6da4","#7ec8e3","#b3dff0","#e05c2a"][_ if isinstance(_, int) else 0],
            text=f'${row["Low"]:,}–${row["High"]:,}',
            textposition="inside",
        ))
    fig_price.update_layout(
        showlegend=False, height=380,
        yaxis_title="Price Range (USD)", xaxis_title="",
        title="OOP Price Ranges by Indication",
        barmode="stack"
    )
    # Simpler bar chart
    fig_p2 = px.bar(price_df, x="Segment", y="Midpoint",
                    color="Segment",
                    color_discrete_sequence=["#1e3a5f","#2e6da4","#7ec8e3","#b3dff0","#e05c2a"],
                    text="Midpoint",
                    error_y=[row["High"]-row["Midpoint"] for _,row in price_df.iterrows()],
                    error_y_minus=[row["Midpoint"]-row["Low"] for _,row in price_df.iterrows()])
    fig_p2.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
    fig_p2.update_layout(showlegend=False, height=380,
                         yaxis_title="Midpoint Price (USD)", xaxis_title="",
                         title="Midpoint OOP Price by Segment (with range bars)")
    st.plotly_chart(fig_p2, use_container_width=True)

    col_p1, col_p2 = st.columns(2)

    with col_p1:
        st.markdown('<div class="section-header">Pricing Details</div>', unsafe_allow_html=True)
        st.dataframe(price_df[["Segment","Low","High","Primary Markets"]]
                     .assign(Low=price_df["Low"].apply(lambda x: f"${x:,}"),
                             High=price_df["High"].apply(lambda x: f"${x:,}")),
                     hide_index=True, use_container_width=True)

    with col_p2:
        st.markdown('<div class="section-header">Payer Dynamics</div>', unsafe_allow_html=True)
        payer_data = [
            ("💳 OOP Dominant", "LATAM, UAE, SEA", "Stable cash-flow; no insurance dependency"),
            ("🏥 Partial Reimb.", "Australia (PBAC)", "Risk-sharing only for life-saving ATMPs"),
            ("❌ No Reimbursement", "Europe (most)", "Even authorized ATMPs rarely reimbursed (e.g. ChondroCelect in France/UK)"),
        ]
        for icon_label, markets, note in payer_data:
            st.markdown(f'<div class="signal-card"><strong>{icon_label}</strong> — <em>{markets}</em><br>{note}</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-header">COGS Reduction Roadmap</div>', unsafe_allow_html=True)
    cogs_df = pd.DataFrame({
        "Year": [2023, 2026, 2030],
        "Cost per Clinical Dose (USD)": [5000, 2500, 500],
        "Milestone": ["Baseline", "Current (lyophilisation advances)", "Target (microfluidics scale-up)"]
    })
    fig_cogs = px.line(cogs_df, x="Year", y="Cost per Clinical Dose (USD)",
                       text="Milestone", markers=True,
                       color_discrete_sequence=["#2e6da4"])
    fig_cogs.update_traces(textposition="top right")
    fig_cogs.update_layout(height=300, margin=dict(t=10,b=10))
    st.plotly_chart(fig_cogs, use_container_width=True)

# ════════════════════════════════════════════════════════════════════════
# TAB 6 — SIGNALS & TRENDS
# ════════════════════════════════════════════════════════════════════════
with tabs[5]:
    st.markdown('<div class="section-header">Key Market Signals (2024–2026)</div>', unsafe_allow_html=True)

    signals = pd.DataFrame([
        {"Date": "Mar 2024",  "Type": "Partnership",  "Event": "Croma-Pharma × Aesthetic Management Partners",          "Impact": "Expanded EU exosome marketplace",             "Sentiment": "🟢 Positive"},
        {"Date": "Jul 2023",  "Type": "M&A",          "Event": "ExoCoBio acquires majority stake in US BENEV",           "Impact": "Consolidation of aesthetic market dominance",  "Sentiment": "🟢 Positive"},
        {"Date": "Feb 2025",  "Type": "Investment",   "Event": "ExoLab Italia raises €5M Series A",                     "Impact": "Plant-derived exosome interest rising in EU",  "Sentiment": "🟢 Positive"},
        {"Date": "Jan 2026",  "Type": "Regulatory",   "Event": "Philippine FDA Cosmetic Notification (UnicoCell)",       "Impact": "Validates ASEAN entry blueprint",              "Sentiment": "🟢 Positive"},
        {"Date": "Late 2025", "Type": "Regulatory",   "Event": "ANVISA–COFEPRIS MoU signed",                            "Impact": "Streamlined LATAM dual-market approvals",     "Sentiment": "🟢 Positive"},
        {"Date": "2025/26",   "Type": "Warning",      "Event": "FDA enforcement on 'hair loss' claims",                 "Impact": "Shift to strict cosmetic labeling",           "Sentiment": "🔴 Risk"},
        {"Date": "Ongoing",   "Type": "Warning",      "Event": "FDA Warning Letters: XoGlo, EXO RNA, Invitra",          "Impact": "Manufacturers pivot to cosmetic / LatAm/SEA", "Sentiment": "🔴 Risk"},
        {"Date": "Ongoing",   "Type": "Structural",   "Event": "Lyophilisation segment ~$50-60M → $100M+ by 2030",      "Impact": "Cold-chain barrier eliminated globally",       "Sentiment": "🟢 Positive"},
    ])

    col_s1, col_s2, col_s3 = st.columns(3)
    col_s1.metric("🟢 Positive Signals", len(signals[signals["Sentiment"].str.contains("Positive")]))
    col_s2.metric("🔴 Risk Signals",     len(signals[signals["Sentiment"].str.contains("Risk")]))
    col_s3.metric("📋 Total Signals",    len(signals))

    type_filter = st.multiselect("Filter by Signal Type", options=signals["Type"].unique(), default=list(signals["Type"].unique()))
    st.dataframe(signals[signals["Type"].isin(type_filter)], hide_index=True, use_container_width=True)

    col_t1, col_t2 = st.columns(2)

    with col_t1:
        st.markdown('<div class="section-header">Signal Types Distribution</div>', unsafe_allow_html=True)
        sig_count = signals["Type"].value_counts().reset_index()
        sig_count.columns = ["Type", "Count"]
        fig_sig = px.bar(sig_count, x="Type", y="Count", color="Type",
                         color_discrete_sequence=["#1e3a5f","#2e6da4","#7ec8e3","#e05c2a"],
                         text="Count")
        fig_sig.update_traces(textposition="outside")
        fig_sig.update_layout(showlegend=False, height=280, margin=dict(t=10,b=10))
        st.plotly_chart(fig_sig, use_container_width=True)

    with col_t2:
        st.markdown('<div class="section-header">Emerging Trends (2025–2030)</div>', unsafe_allow_html=True)
        trends = [
            ("🤖 AI Diagnostics",       "AI/ML integration for exosome biomarker profiling — accelerating research-to-clinical transition"),
            ("🔬 Manufacturing Scale",  "Microfluidics-based isolation = fastest CAGR segment — addresses bottleneck in production scalability"),
            ("💊 COGS Collapse",        "Cost per dose: $5,000 (2023) → $500 (2030) — unlocks mass-market profitability"),
            ("🌿 Plant-Derived",        "Non-human exosomes gaining EU investor interest as lower-risk cosmetic entry point"),
            ("💉 Sexual Wellness",      "Vaginal rejuvenation + erectile function — high-demand niche in Dubai and Australia"),
            ("❄️ Lyophilisation",       "$50-60M segment today → low hundreds of millions by early 2030s — eliminates cold-chain barriers"),
        ]
        for icon, text in trends:
            st.markdown(f'<div class="signal-card"><strong>{icon}</strong> {text}</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-header">Strategic Entry Checklist</div>', unsafe_allow_html=True)
    checklist = [
        "✅ Certificate of Analysis (CoA) with CD63/CD81 exosome marker verification",
        "✅ Lyophilisation capability — position as primary format for cross-border logistics",
        "✅ Tiered distributor pricing — volume-based cumulative discounts",
        "✅ ANVISA-COFEPRIS MoU reliance — use for dual LATAM market entry",
        "✅ Philippines FDA notification — use as ASEAN compliance signal",
        "✅ Avoid medical claims on cosmetic-grade products — follow FDA warning letter guidance",
    ]
    for item in checklist:
        st.markdown(f"**{item}**")


import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import time

st.set_page_config(
    page_title="PharmaTrialIQ",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.stApp { background: linear-gradient(135deg, #0a0e1a 0%, #0d1b2a 50%, #0a0e1a 100%); color: #e0e6f0; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0d1b2a 0%, #112240 100%); border-right: 1px solid #1e3a5f; }
[data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] label { color: #a8c0d6 !important; }
.main-header { background: linear-gradient(90deg, #1565C0, #00BCD4, #1565C0); background-size: 200% auto; -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 3rem; font-weight: 800; text-align: center; letter-spacing: 2px; padding: 1rem 0 0.2rem 0; animation: shine 3s linear infinite; }
@keyframes shine { to { background-position: 200% center; } }
.sub-header { font-size: 0.95rem; color: #64b5f6; text-align: center; margin-bottom: 0.5rem; letter-spacing: 1px; }
.live-badge { display: inline-block; background: #00c853; color: white; font-size: 0.7rem; font-weight: 700; padding: 3px 10px; border-radius: 20px; letter-spacing: 1px; animation: pulse 2s infinite; }
@keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(0,200,83,0.5); } 70% { box-shadow: 0 0 0 8px rgba(0,200,83,0); } 100% { box-shadow: 0 0 0 0 rgba(0,200,83,0); } }
.metric-card { background: linear-gradient(135deg, #0d2137 0%, #112240 100%); border: 1px solid #1e3a5f; border-radius: 16px; padding: 1.4rem 1rem; text-align: center; position: relative; overflow: hidden; transition: transform 0.2s; }
.metric-card:hover { transform: translateY(-3px); border-color: #2196F3; }
.metric-card::before { content: ""; position: absolute; top: 0; left: 0; right: 0; height: 3px; border-radius: 16px 16px 0 0; }
.metric-card-blue::before { background: #2196F3; }
.metric-card-green::before { background: #00c853; }
.metric-card-orange::before { background: #FF9800; }
.metric-card-red::before { background: #f44336; }
.metric-number { font-size: 2.4rem; font-weight: 800; letter-spacing: 1px; margin-bottom: 0.3rem; }
.metric-number-blue { color: #64b5f6; }
.metric-number-green { color: #69f0ae; }
.metric-number-orange { color: #ffcc02; }
.metric-number-red { color: #ff5252; }
.metric-label { font-size: 0.78rem; color: #7a9abf; text-transform: uppercase; letter-spacing: 1.5px; font-weight: 600; }
.metric-icon { font-size: 1.5rem; margin-bottom: 0.5rem; }
.section-header { color: #64b5f6; font-size: 1.1rem; font-weight: 700; text-transform: uppercase; letter-spacing: 2px; border-left: 3px solid #2196F3; padding-left: 12px; margin: 1.5rem 0 1rem 0; }
.stTextInput input { background: #0d2137 !important; border: 1px solid #1e3a5f !important; color: #e0e6f0 !important; border-radius: 8px !important; }
.stDownloadButton button { background: linear-gradient(90deg, #1565C0, #0097A7) !important; color: white !important; border: none !important; border-radius: 8px !important; padding: 0.5rem 1.5rem !important; font-weight: 600 !important; }
hr { border-color: #1e3a5f !important; }
.footer { text-align: center; color: #3d5a73; font-size: 0.78rem; padding: 1rem 0; letter-spacing: 1px; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style="text-align:center; padding: 1rem 0 0 0;">
    <div class="main-header">PHARMATRIALIQ</div>
    <div class="sub-header">CLINICAL TRIAL INTELLIGENCE PLATFORM &nbsp;|&nbsp; POWERED BY NIH CLINICALTRIALS.GOV</div>
    <div style="margin-top: 0.5rem;"><span class="live-badge">LIVE DATA</span></div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

@st.cache_data
def load_data():
    url     = "https://clinicaltrials.gov/api/v2/studies"
    headers = {"Accept": "application/json", "User-Agent": "Mozilla/5.0"}
    all_trials = []
    next_token = None
    for batch in range(1, 6):
        params = {"query.cond": "cancer", "query.term": "Phase 3", "pageSize": 100, "format": "json"}
        if next_token:
            params["pageToken"] = next_token
        try:
            response   = requests.get(url, params=params, headers=headers, timeout=30)
            if response.status_code != 200:
                break
            data       = response.json()
            studies    = data.get("studies", [])
            next_token = data.get("nextPageToken", None)
            for study in studies:
                try:
                    id_mod      = study["protocolSection"]["identificationModule"]
                    status_mod  = study["protocolSection"]["statusModule"]
                    design_mod  = study["protocolSection"].get("designModule", {})
                    desc_mod    = study["protocolSection"].get("descriptionModule", {})
                    sponsor_mod = study["protocolSection"].get("sponsorCollaboratorsModule", {})
                    phases_raw  = design_mod.get("phases", [])
                    phase       = phases_raw[0] if phases_raw else "N/A"
                    all_trials.append({
                        "Trial ID"    : id_mod.get("nctId", "N/A"),
                        "Title"       : id_mod.get("briefTitle", "N/A"),
                        "Status"      : status_mod.get("overallStatus", "N/A").replace("_"," ").title(),
                        "Phase"       : phase.replace("PHASE","Phase "),
                        "Sponsor"     : sponsor_mod.get("leadSponsor",{}).get("name","N/A"),
                        "Sponsor Type": sponsor_mod.get("leadSponsor",{}).get("class","N/A"),
                        "Summary"     : desc_mod.get("briefSummary","N/A")[:300],
                        "Start Year"  : status_mod.get("startDateStruct",{}).get("date","N/A")[:4]
                    })
                except Exception:
                    pass
            time.sleep(0.5)
            if not next_token:
                break
        except Exception:
            break
    df = pd.DataFrame(all_trials)
    df = df[df["Title"] != "N/A"].reset_index(drop=True)
    return df

with st.spinner("Fetching live pharmaceutical data..."):
    df = load_data()

st.sidebar.markdown("""
<div style="text-align:center; padding: 1rem 0;">
    <div style="font-size:2rem;">💊</div>
    <div style="color:#64b5f6; font-weight:800; font-size:1.1rem; letter-spacing:2px;">PHARMATRIALIQ</div>
    <div style="color:#3d5a73; font-size:0.7rem; letter-spacing:1px; margin-top:4px;">INTELLIGENCE PLATFORM</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("<div style='color:#64b5f6; font-size:0.8rem; font-weight:700; letter-spacing:2px;'>FILTERS</div>", unsafe_allow_html=True)

all_statuses       = sorted(df["Status"].dropna().unique().tolist())
selected_statuses  = st.sidebar.multiselect("Trial Status",  options=all_statuses,      default=all_statuses)
all_phases         = sorted(df["Phase"].dropna().unique().tolist())
selected_phases    = st.sidebar.multiselect("Trial Phase",   options=all_phases,        default=all_phases)
all_sponsor_types  = sorted(df["Sponsor Type"].dropna().unique().tolist())
selected_sponsor_types = st.sidebar.multiselect("Sponsor Type", options=all_sponsor_types, default=all_sponsor_types)

df_filtered = df[
    (df["Status"].isin(selected_statuses)) &
    (df["Phase"].isin(selected_phases)) &
    (df["Sponsor Type"].isin(selected_sponsor_types))
]

st.sidebar.markdown("---")
st.sidebar.markdown(f"""
<div style="background:#0d2137; border:1px solid #1e3a5f; border-radius:10px; padding:1rem; text-align:center;">
    <div style="color:#64b5f6; font-size:1.8rem; font-weight:800;">{len(df_filtered)}</div>
    <div style="color:#3d5a73; font-size:0.75rem; letter-spacing:1px; text-transform:uppercase;">Trials Loaded</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("""
<div style="color:#3d5a73; font-size:0.7rem; text-align:center; margin-top:1rem;">
    Data Source: ClinicalTrials.gov<br>National Institutes of Health<br>Updated: Live
</div>
""", unsafe_allow_html=True)

total      = len(df_filtered)
completed  = len(df_filtered[df_filtered["Status"].str.contains("Complet",  na=False)])
recruiting = len(df_filtered[df_filtered["Status"].str.contains("Recruit",  na=False)])
terminated = len(df_filtered[df_filtered["Status"].str.contains("Terminat", na=False)])
comp_pct   = round(completed  / total * 100, 1) if total > 0 else 0
rec_pct    = round(recruiting / total * 100, 1) if total > 0 else 0
term_pct   = round(terminated / total * 100, 1) if total > 0 else 0

st.markdown("<div class='section-header'>EXECUTIVE DASHBOARD</div>", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""<div class="metric-card metric-card-blue">
        <div class="metric-icon">🔬</div>
        <div class="metric-number metric-number-blue">{total}</div>
        <div class="metric-label">Total Trials</div></div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="metric-card metric-card-green">
        <div class="metric-icon">✅</div>
        <div class="metric-number metric-number-green">{comp_pct}%</div>
        <div class="metric-label">Completion Rate</div></div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class="metric-card metric-card-orange">
        <div class="metric-icon">🔵</div>
        <div class="metric-number metric-number-orange">{rec_pct}%</div>
        <div class="metric-label">Recruiting Now</div></div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""<div class="metric-card metric-card-red">
        <div class="metric-icon">⚠️</div>
        <div class="metric-number metric-number-red">{term_pct}%</div>
        <div class="metric-label">Termination Rate</div></div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

DARK_BG    = "#0d2137"
GRID_COLOR = "#1e3a5f"
TEXT_COLOR = "#a8c0d6"

def dark_chart_style(ax, fig):
    fig.patch.set_facecolor(DARK_BG)
    ax.set_facecolor(DARK_BG)
    ax.title.set_color(TEXT_COLOR)
    ax.xaxis.label.set_color(TEXT_COLOR)
    ax.yaxis.label.set_color(TEXT_COLOR)
    ax.tick_params(colors=TEXT_COLOR)
    ax.grid(True, color=GRID_COLOR, linewidth=0.5, alpha=0.7)
    for spine in ax.spines.values():
        spine.set_edgecolor(GRID_COLOR)

st.markdown("<div class='section-header'>TRIAL ANALYTICS</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("<div style='color:#a8c0d6; font-size:0.85rem; font-weight:600; margin-bottom:8px; letter-spacing:1px;'>TRIAL STATUS DISTRIBUTION</div>", unsafe_allow_html=True)
    status_counts = df_filtered["Status"].value_counts()
    fig1, ax1     = plt.subplots(figsize=(6, 4))
    dark_chart_style(ax1, fig1)
    status_colors = {"Completed":"#00c853","Recruiting":"#2196F3","Active Not Recruiting":"#FF9800","Terminated":"#f44336","Withdrawn":"#9C27B0","Suspended":"#FF5722"}
    bar_colors    = [status_colors.get(s, "#64b5f6") for s in status_counts.index]
    bars = ax1.bar(status_counts.index, status_counts.values, color=bar_colors, edgecolor=DARK_BG, linewidth=1.5)
    for bar, val in zip(bars, status_counts.values):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, str(val), ha="center", va="bottom", fontsize=9, fontweight="bold", color=TEXT_COLOR)
    ax1.set_ylabel("Number of Trials", color=TEXT_COLOR)
    plt.xticks(rotation=30, ha="right", fontsize=8)
    plt.tight_layout()
    st.pyplot(fig1)
    plt.close()

with col2:
    st.markdown("<div style='color:#a8c0d6; font-size:0.85rem; font-weight:600; margin-bottom:8px; letter-spacing:1px;'>SPONSOR TYPE BREAKDOWN</div>", unsafe_allow_html=True)
    sponsor_type_counts = df_filtered["Sponsor Type"].value_counts()
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    fig2.patch.set_facecolor(DARK_BG)
    ax2.set_facecolor(DARK_BG)
    pie_colors = ["#2196F3","#00c853","#FF9800","#9C27B0","#f44336"]
    wedges, texts, autotexts = ax2.pie(sponsor_type_counts.values, labels=sponsor_type_counts.index, autopct="%1.1f%%", colors=pie_colors[:len(sponsor_type_counts)], startangle=140, wedgeprops=dict(edgecolor=DARK_BG, linewidth=2), pctdistance=0.82)
    for text in texts:
        text.set_color(TEXT_COLOR); text.set_fontsize(9)
    for autotext in autotexts:
        autotext.set_color("white"); autotext.set_fontsize(9); autotext.set_fontweight("bold")
    plt.tight_layout()
    st.pyplot(fig2)
    plt.close()

col3, col4 = st.columns(2)

with col3:
    st.markdown("<div style='color:#a8c0d6; font-size:0.85rem; font-weight:600; margin-bottom:8px; letter-spacing:1px;'>TOP 10 SPONSORS</div>", unsafe_allow_html=True)
    top_sponsors = df_filtered["Sponsor"].value_counts().head(10)
    fig3, ax3    = plt.subplots(figsize=(6, 5))
    dark_chart_style(ax3, fig3)
    bar_colors3  = [plt.cm.Blues(0.4 + 0.6 * i / len(top_sponsors)) for i in range(len(top_sponsors))]
    ax3.barh(top_sponsors.index[::-1], top_sponsors.values[::-1], color=bar_colors3, edgecolor=DARK_BG, linewidth=1)
    for i, val in enumerate(top_sponsors.values[::-1]):
        ax3.text(val + 0.1, i, str(val), va="center", fontsize=9, fontweight="bold", color=TEXT_COLOR)
    ax3.set_xlabel("Number of Trials", color=TEXT_COLOR)
    plt.yticks(fontsize=7)
    plt.tight_layout()
    st.pyplot(fig3)
    plt.close()

with col4:
    st.markdown("<div style='color:#a8c0d6; font-size:0.85rem; font-weight:600; margin-bottom:8px; letter-spacing:1px;'>R&D INVESTMENT TREND (2000-2024)</div>", unsafe_allow_html=True)
    df_yr = df_filtered[df_filtered["Start Year"].str.isnumeric() == True].copy()
    df_yr["Start Year"] = df_yr["Start Year"].astype(int)
    df_yr = df_yr[(df_yr["Start Year"] >= 2000) & (df_yr["Start Year"] <= 2024)]
    year_counts = df_yr["Start Year"].value_counts().sort_index()
    fig4, ax4   = plt.subplots(figsize=(6, 4))
    dark_chart_style(ax4, fig4)
    ax4.plot(year_counts.index, year_counts.values, color="#00BCD4", linewidth=2.5, marker="o", markersize=5, markerfacecolor=DARK_BG, markeredgewidth=2, markeredgecolor="#00BCD4")
    ax4.fill_between(year_counts.index, year_counts.values, alpha=0.15, color="#00BCD4")
    ax4.set_xlabel("Year", color=TEXT_COLOR)
    ax4.set_ylabel("Trials Started", color=TEXT_COLOR)
    plt.xticks(range(2000, 2025, 4), rotation=45, fontsize=8)
    plt.tight_layout()
    st.pyplot(fig4)
    plt.close()

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<div class='section-header'>MARKET INTELLIGENCE</div>", unsafe_allow_html=True)

ind_pct     = round(df_filtered["Sponsor Type"].value_counts(normalize=True).get("INDUSTRY", 0) * 100, 1)
top_s_name  = df_filtered["Sponsor"].value_counts().index[0]  if len(df_filtered) > 0 else "N/A"
top_s_count = df_filtered["Sponsor"].value_counts().values[0] if len(df_filtered) > 0 else 0

if comp_pct >= 60:
    maturity = "HIGH";   maturity_color = "#00c853"; maturity_desc = "Mature therapy area - high commercial readiness"
elif comp_pct >= 40:
    maturity = "MEDIUM"; maturity_color = "#FF9800"; maturity_desc = "Developing space - moderate investment risk"
else:
    maturity = "LOW";    maturity_color = "#f44336"; maturity_desc = "Early stage - high risk, high reward potential"

m1, m2, m3 = st.columns(3)
with m1:
    st.markdown(f"""<div class="metric-card" style="text-align:left; padding:1.2rem;">
        <div style="color:#64b5f6; font-size:0.7rem; font-weight:700; letter-spacing:2px; margin-bottom:0.5rem;">MARKET LEADER</div>
        <div style="color:#e0e6f0; font-size:0.95rem; font-weight:700; margin-bottom:0.3rem;">{top_s_name[:30]}</div>
        <div style="color:#3d5a73; font-size:0.8rem;">{top_s_count} active trials</div>
        <div style="margin-top:0.8rem; color:#64b5f6; font-size:0.75rem;">Highest trial volume sponsor</div>
    </div>""", unsafe_allow_html=True)
with m2:
    st.markdown(f"""<div class="metric-card" style="text-align:left; padding:1.2rem;">
        <div style="color:#64b5f6; font-size:0.7rem; font-weight:700; letter-spacing:2px; margin-bottom:0.5rem;">INDUSTRY DOMINANCE</div>
        <div style="color:#69f0ae; font-size:1.8rem; font-weight:800; margin-bottom:0.3rem;">{ind_pct}%</div>
        <div style="color:#3d5a73; font-size:0.8rem;">Commercially funded trials</div>
        <div style="margin-top:0.8rem; color:#64b5f6; font-size:0.75rem;">High = strong commercial interest</div>
    </div>""", unsafe_allow_html=True)
with m3:
    st.markdown(f"""<div class="metric-card" style="text-align:left; padding:1.2rem;">
        <div style="color:#64b5f6; font-size:0.7rem; font-weight:700; letter-spacing:2px; margin-bottom:0.5rem;">THERAPY AREA MATURITY</div>
        <div style="color:{maturity_color}; f

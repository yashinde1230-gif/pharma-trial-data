
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import time

# ── PAGE CONFIG ──────────────────────────────────────────
# This must be the very first Streamlit command in the file
# Sets the browser tab title, icon, and layout
st.set_page_config(
    page_title="PharmaTrialIQ",
    page_icon="💊",
    layout="wide"          # "wide" uses the full screen width
)

# ── CUSTOM CSS ───────────────────────────────────────────
# We inject CSS to make the app look more professional
# st.markdown with unsafe_allow_html=True lets us write raw HTML/CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.4rem;
        font-weight: 700;
        color: #1565C0;
        text-align: center;
        padding: 1rem 0 0.2rem 0;
    }
    .sub-header {
        font-size: 1rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f0f4ff;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        border-left: 4px solid #1565C0;
    }
    .metric-number {
        font-size: 2rem;
        font-weight: 700;
        color: #1565C0;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #555;
        margin-top: 0.3rem;
    }
    </style>
""", unsafe_allow_html=True)

# ── HEADER ───────────────────────────────────────────────
st.markdown('<div class="main-header">💊 PharmaTrialIQ</div>', 
            unsafe_allow_html=True)
st.markdown('<div class="sub-header">AI-powered Clinical Trial Intelligence · Cancer Phase 3 Trials · ClinicalTrials.gov</div>', 
            unsafe_allow_html=True)

# A horizontal divider line
st.markdown("---")

# ── DATA LOADING FUNCTION ────────────────────────────────
# @st.cache_data is very important
# It means: run this function once, save the result
# If the user clicks something and the page refreshes,
# DON'T fetch from the API again — use the saved result
# This makes the app fast and avoids hitting API limits
@st.cache_data
def load_data():
    url = "https://clinicaltrials.gov/api/v2/studies"
    headers = {"Accept": "application/json", "User-Agent": "Mozilla/5.0"}
    all_trials = []
    next_token = None

    # Show a progress spinner while loading
    for batch in range(1, 6):
        params = {
            "query.cond": "cancer",
            "query.term": "Phase 3",
            "pageSize"  : 100,
            "format"    : "json"
        }
        if next_token:
            params["pageToken"] = next_token

        try:
            response = requests.get(url, params=params, 
                                    headers=headers, timeout=30)
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

                    phases_raw = design_mod.get("phases", [])
                    phase      = phases_raw[0] if phases_raw else "N/A"

                    all_trials.append({
                        "Trial ID"    : id_mod.get("nctId", "N/A"),
                        "Title"       : id_mod.get("briefTitle", "N/A"),
                        "Status"      : status_mod.get("overallStatus", "N/A")
                                            .replace("_"," ").title(),
                        "Phase"       : phase.replace("PHASE","Phase "),
                        "Sponsor"     : sponsor_mod.get("leadSponsor",{})
                                            .get("name","N/A"),
                        "Sponsor Type": sponsor_mod.get("leadSponsor",{})
                                            .get("class","N/A"),
                        "Summary"     : desc_mod.get("briefSummary","N/A")[:300],
                        "Start Year"  : status_mod.get("startDateStruct",{})
                                            .get("date","N/A")[:4]
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

# ── LOAD DATA WITH SPINNER ───────────────────────────────
# st.spinner shows a loading animation while the function runs
with st.spinner("📡 Fetching live data from ClinicalTrials.gov..."):
    df = load_data()

# ── SIDEBAR FILTERS ──────────────────────────────────────
# st.sidebar puts controls on the left panel
# This lets users filter the data without rewriting any code
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/3/3e/ClinicalTrials.gov_logo.svg/320px-ClinicalTrials.gov_logo.svg.png", 
                 width=200)
st.sidebar.markdown("## 🔧 Filters")
st.sidebar.markdown("Use filters to explore specific segments")

# Multiselect = dropdown where user can pick multiple options
# The default shows all unique statuses in the data
all_statuses = sorted(df["Status"].dropna().unique().tolist())
selected_statuses = st.sidebar.multiselect(
    "Trial Status",
    options=all_statuses,
    default=all_statuses   # all selected by default
)

all_phases = sorted(df["Phase"].dropna().unique().tolist())
selected_phases = st.sidebar.multiselect(
    "Trial Phase",
    options=all_phases,
    default=all_phases
)

all_sponsor_types = sorted(df["Sponsor Type"].dropna().unique().tolist())
selected_sponsor_types = st.sidebar.multiselect(
    "Sponsor Type",
    options=all_sponsor_types,
    default=all_sponsor_types
)

# Apply filters to the dataframe
# We only keep rows where the values match what the user selected
df_filtered = df[
    (df["Status"].isin(selected_statuses)) &
    (df["Phase"].isin(selected_phases)) &
    (df["Sponsor Type"].isin(selected_sponsor_types))
]

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Showing {len(df_filtered)} of {len(df)} trials**")

# ── KPI METRIC CARDS ─────────────────────────────────────
# KPI = Key Performance Indicator
# These are the headline numbers at the top of the dashboard
st.markdown("### 📊 Executive Summary")

total      = len(df_filtered)
completed  = len(df_filtered[df_filtered["Status"].str.contains("Complet",  na=False)])
recruiting = len(df_filtered[df_filtered["Status"].str.contains("Recruit",  na=False)])
terminated = len(df_filtered[df_filtered["Status"].str.contains("Terminat", na=False)])

comp_pct = round(completed  / total * 100, 1) if total > 0 else 0
rec_pct  = round(recruiting / total * 100, 1) if total > 0 else 0
term_pct = round(terminated / total * 100, 1) if total > 0 else 0

# st.columns(4) creates 4 equal columns side by side
# Like a 4-column table layout
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{total}</div>
            <div class="metric-label">Total Trials</div>
        </div>""", unsafe_allow_html=True)

with col2:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{comp_pct}%</div>
            <div class="metric-label">Completion Rate</div>
        </div>""", unsafe_allow_html=True)

with col3:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{rec_pct}%</div>
            <div class="metric-label">Currently Recruiting</div>
        </div>""", unsafe_allow_html=True)

with col4:
    st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{term_pct}%</div>
            <div class="metric-label">Termination Rate</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")

# ── CHARTS ROW 1 ─────────────────────────────────────────
st.markdown("### 📈 Trial Analysis")

# Two charts side by side using columns
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.markdown("**Trial Status Breakdown**")
    status_counts = df_filtered["Status"].value_counts()
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    colors = sns.color_palette("Blues_d", len(status_counts))
    bars = ax1.bar(status_counts.index, status_counts.values,
                   color=colors, edgecolor="white")
    for bar, val in zip(bars, status_counts.values):
        ax1.text(bar.get_x() + bar.get_width()/2,
                 bar.get_height() + 0.5,
                 str(val), ha="center", fontsize=9, fontweight="bold")
    ax1.set_ylabel("Number of Trials")
    plt.xticks(rotation=30, ha="right", fontsize=8)
    plt.tight_layout()
    # st.pyplot() displays a matplotlib chart inside Streamlit
    st.pyplot(fig1)
    plt.close()   # close the figure to free memory

with chart_col2:
    st.markdown("**Sponsor Type Distribution**")
    sponsor_counts = df_filtered["Sponsor Type"].value_counts()
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    colors2 = ["#2196F3","#4CAF50","#FF9800","#9C27B0","#F44336"]
    ax2.pie(sponsor_counts.values,
            labels=sponsor_counts.index,
            autopct="%1.1f%%",
            colors=colors2[:len(sponsor_counts)],
            startangle=140,
            wedgeprops=dict(edgecolor="white", linewidth=2))
    plt.tight_layout()
    st.pyplot(fig2)
    plt.close()

st.markdown("---")

# ── CHARTS ROW 2 ─────────────────────────────────────────
chart_col3, chart_col4 = st.columns(2)

with chart_col3:
    st.markdown("**Top 10 Trial Sponsors**")
    top_sponsors = df_filtered["Sponsor"].value_counts().head(10)
    fig3, ax3 = plt.subplots(figsize=(6, 5))
    colors3 = sns.color_palette("viridis", len(top_sponsors))
    ax3.barh(top_sponsors.index[::-1],
             top_sponsors.values[::-1],
             color=colors3, edgecolor="white")
    for i, val in enumerate(top_sponsors.values[::-1]):
        ax3.text(val + 0.1, i, str(val), va="center", fontsize=9)
    ax3.set_xlabel("Number of Trials")
    plt.tight_layout()
    st.pyplot(fig3)
    plt.close()

with chart_col4:
    st.markdown("**Trials Started Per Year**")
    df_yr = df_filtered[df_filtered["Start Year"].str.isnumeric() == True].copy()
    df_yr["Start Year"] = df_yr["Start Year"].astype(int)
    df_yr = df_yr[(df_yr["Start Year"] >= 2000) & (df_yr["Start Year"] <= 2024)]
    year_counts = df_yr["Start Year"].value_counts().sort_index()
    fig4, ax4 = plt.subplots(figsize=(6, 4))
    ax4.plot(year_counts.index, year_counts.values,
             color="#2196F3", linewidth=2.5,
             marker="o", markersize=5,
             markerfacecolor="white", markeredgewidth=2)
    ax4.fill_between(year_counts.index, year_counts.values,
                     alpha=0.15, color="#2196F3")
    ax4.set_xlabel("Year")
    ax4.set_ylabel("Trials Started")
    plt.xticks(rotation=45, fontsize=8)
    plt.tight_layout()
    st.pyplot(fig4)
    plt.close()

st.markdown("---")

# ── DATA TABLE ───────────────────────────────────────────
# Show the actual raw data at the bottom for transparency
st.markdown("### 🔍 Raw Trial Data")

# Text input for searching the data table
search = st.text_input("Search trials by keyword (e.g. immunotherapy, breast, lung)")

# Filter the table based on search term
if search:
    # Case-insensitive search across Title and Summary columns
    mask = (df_filtered["Title"].str.contains(search, case=False, na=False) |
            df_filtered["Summary"].str.contains(search, case=False, na=False))
    df_show = df_filtered[mask]
else:
    df_show = df_filtered

st.markdown(f"Showing **{len(df_show)}** trials")

# Display the dataframe as an interactive table
# use_container_width=True makes it fill the full width
st.dataframe(
    df_show[["Trial ID","Title","Status","Phase","Sponsor","Start Year"]],
    use_container_width=True,
    height=400
)

# ── DOWNLOAD BUTTON ──────────────────────────────────────
# Let the user download the filtered data as a CSV file
csv = df_show.to_csv(index=False)
st.download_button(
    label="⬇️ Download filtered data as CSV",
    data=csv,
    file_name="pharmatrialiq_export.csv",
    mime="text/csv"
)

# ── FOOTER ───────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center; color:#999; font-size:0.8rem'>
    PharmaTrialIQ · Data source: ClinicalTrials.gov (NIH) · 
    Built with Python & Streamlit · MBA Project
</div>
""", unsafe_allow_html=True)

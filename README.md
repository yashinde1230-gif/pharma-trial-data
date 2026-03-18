# 💊 PharmaTrialIQ

### AI-Powered Clinical Trial Intelligence Platform

An interactive web application that fetches and analyzes **500+ real clinical trials** 
from ClinicalTrials.gov and presents pharma business intelligence through live charts 
and KPI dashboards.

---

## 🔍 What it does

- Fetches live data from the official ClinicalTrials.gov API (NIH)
- Analyzes Phase 3 cancer trials across 5 key dimensions
- Displays real-time KPIs: completion rate, termination rate, recruiting status
- Interactive filters by trial phase, status, and sponsor type
- Keyword search across 500+ trial titles and summaries
- One-click CSV export of filtered data

## 📊 Key Insights Delivered

| Metric | Description |
|--------|-------------|
| Completion Rate | % of trials successfully completed |
| Termination Rate | % of trials stopped early (risk signal) |
| Sponsor Landscape | Industry vs Academic vs Government split |
| Top Sponsors | Companies running the most trials |
| R&D Trend | Trial volume growth from 2000 to 2024 |

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| Python | Core programming language |
| Streamlit | Web application framework |
| Pandas | Data processing and analysis |
| Matplotlib / Seaborn | Data visualization |
| ClinicalTrials.gov API | Real pharmaceutical data source |

## 🚀 How to Run Locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## 👤 About

Built as an MBA capstone project in Pharmaceutical Management.  
Demonstrates the application of AI and data analytics in pharma business intelligence.

**Data Source:** ClinicalTrials.gov — US National Institutes of Health (NIH)  
**Trials Analyzed:** 500+ Phase 3 Cancer Trials  
**Last Updated:** 2026

# northfit-analytics
# The 6pm Problem

I went to LA Fitness last Tuesday at 6pm. Waited 15 minutes for a treadmill. The guy next to me said he drives to a different location now because this one is always packed after work.

I started thinking about that on the drive home. LA Fitness knows exactly when every member walks through the door. Every check-in is timestamped. They have all the data. The question is whether anyone is actually using it.

So I built the analysis.

---

## What this is

A business analysis and operational analytics project for a fictional Canadian fitness chain called NorthFit. Twelve months of hourly check-in data across 5 GTA locations. Four member segments with different capacity experiences, different satisfaction scores, and different churn risks. A business case for a smarter member communication system that uses the data the gym already collects to improve the experience and protect revenue.

---

## Live app

[Launch the NorthFit Analytics Dashboard](https://northfit-analytics-2026.streamlit.app/)

---

## What the data showed

Nearly half of all weekday evening hours across the 5 locations run above 85% capacity. Members arriving between 5pm and 8pm face an average 7.4 minute equipment wait. Those same members have an NPS score of 42, almost 30 points below members who come at off-peak times.

The same gyms that are overcrowded at 6pm are running below 40% capacity between 9am and 3pm on the same weekdays. The capacity is there. The members just do not know about it.

| Segment | Members | Monthly Visits | NPS | Churn Risk |
|---------|---------|---------------|-----|-----------|
| Peak Warrior | 4,488 (38%) | 14 per month | 42 | Medium |
| Off-Peak Regular | 3,304 (28%) | 16 per month | 71 | Low |
| Weekend Warrior | 2,360 (20%) | 8 per month | 58 | Medium |
| Ghost Member | 1,628 (14%) | 1 per month | 18 | High |

Total annual revenue at risk across at-risk segments is $1.1 million. A member communication system that improves retention by 10% protects $552,000 per year. Estimated implementation cost is $180,000. Payback period is under 4 months.

---

## What the five tabs cover

The 6pm Problem tab shows the utilization heatmap by hour and day, the peak hour overcrowding rate, and the underutilised windows where capacity is sitting unused.

The Location Deep Dive tab lets you explore each of the 5 locations individually with a full hourly heatmap by day of week and a monthly trend line.

The Member Segments tab shows the four segment breakdown with NPS scores, visit frequency, and churn risk side by side.

The Churn Risk tab maps annual revenue at risk by segment and shows the relationship between NPS score and churn rate.

The Business Case tab shows the requirements for the recommended member communication system, the retention scenario model, and the financial case for building it.

---

## Files in this repo

| File | What it is |
|------|-----------|
| app.py | Streamlit app with five interactive tabs |
| checkin-data.csv | 34,770 hourly check-in records across 5 locations and 12 months |
| peak-analysis.csv | Average utilization and overcrowding rate by location and hour |
| member-segments.csv | Four segment profiles with NPS, churn rate, and revenue at risk |
| key-findings.json | Headline findings including revenue at risk and retention value |
| analysis-summary.csv | All key metrics in one place |
| ba-report.pdf | Full business analysis report with requirements register and business case |
| generate-data.py | Python script that built the synthetic dataset |
| requirements.txt | Package dependencies |

---

## Skills this project demonstrates

Operational data analysis. Member segmentation. Churn risk modelling. Business requirements writing with MoSCoW prioritisation. Business case development with scenario modelling. NPS analysis and interpretation. Python for data generation and analysis. Plotly heatmaps, scatter plots, and bar charts. Streamlit interactive dashboard design and deployment.

---

## About this project

Part of a portfolio series built while job searching in Canada after graduating from the University of Waterloo.

Prepared by Simran Saran. Targeting business analyst and marketing analyst roles across Canada.

All data is synthetic. NorthFit is fictional. Utilization patterns and member behaviour are modelled on publicly available fitness industry benchmarks.

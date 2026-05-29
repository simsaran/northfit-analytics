import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from pathlib import Path

st.set_page_config(
    page_title="NorthFit — Member Analytics",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    .block-container{padding:1.5rem 2rem}
    .kpi{background:white;border-radius:12px;padding:16px 20px;border:1px solid #E8E8E8;box-shadow:0 1px 4px rgba(0,0,0,0.05);margin-bottom:8px}
    .kpi-label{font-size:11px;color:#888;margin-bottom:4px;font-weight:500;text-transform:uppercase;letter-spacing:.04em}
    .kpi-value{font-size:26px;font-weight:700;color:#111;line-height:1.1}
    .kpi-note{font-size:11px;color:#888;margin-top:3px}
    .kpi-red .kpi-value{color:#C0392B}
    .kpi-green .kpi-value{color:#0A7540}
    .kpi-amber .kpi-value{color:#B7791F}
    .kpi-blue .kpi-value{color:#0C447C}
    .finding{background:#F0FBF6;border-left:3px solid #27AE60;border-radius:0 8px 8px 0;padding:11px 15px;font-size:13px;color:#1A5C35;margin:10px 0;line-height:1.6}
    .alert{background:#FDF2F2;border-left:3px solid #C0392B;border-radius:0 8px 8px 0;padding:11px 15px;font-size:13px;color:#7B1818;margin:10px 0;line-height:1.6}
    .warning{background:#FEF9EC;border-left:3px solid #F39C12;border-radius:0 8px 8px 0;padding:11px 15px;font-size:13px;color:#7D5A00;margin:10px 0;line-height:1.6}
    .section-title{font-size:15px;font-weight:600;color:#111;margin:18px 0 10px 0;padding-bottom:6px;border-bottom:1.5px solid #EBEBEB}
    footer{visibility:hidden}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load():
    base = Path(__file__).parent
    checkins  = pd.read_csv(base / "checkin-data.csv")
    peak      = pd.read_csv(base / "peak-analysis.csv")
    segments  = pd.read_csv(base / "member-segments.csv")
    with open(base / "key-findings.json") as f:
        findings = json.load(f)
    return checkins, peak, segments, findings

checkins, peak, segments, findings = load()

LOC_COLORS = {
    "Mississauga City Centre": "#E1306C",
    "Toronto Downtown":        "#4285F4",
    "Scarborough":             "#27AE60",
    "Brampton North":          "#F59E0B",
    "Etobicoke":               "#8B5CF6",
}

SEG_COLORS = {
    "Peak Warrior":     "#4285F4",
    "Off-Peak Regular": "#27AE60",
    "Weekend Warrior":  "#F59E0B",
    "Ghost Member":     "#C0392B",
}

st.markdown("## NorthFit Fitness Chain — Member and Operational Analytics")
st.markdown("**January 2024 to December 2024** &nbsp;|&nbsp; 5 GTA locations &nbsp;|&nbsp; 4 member segments &nbsp;|&nbsp; 34,770 hourly check-in records")
st.divider()

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "  The 6pm Problem  ",
    "  Location Deep Dive  ",
    "  Member Segments  ",
    "  Churn Risk  ",
    "  Business Case  ",
])

# ── TAB 1: THE 6PM PROBLEM ────────────────────────────────────────────────────
with tab1:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""<div class="kpi kpi-red">
            <div class="kpi-label">Peak hour overcrowding rate</div>
            <div class="kpi-value">{findings['peak_hour_overcrowded_pct']}%</div>
            <div class="kpi-note">Of 5pm to 8pm hours across all locations</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="kpi kpi-amber">
            <div class="kpi-label">Avg wait time at peak</div>
            <div class="kpi-value">{findings['avg_wait_at_peak']} min</div>
            <div class="kpi-note">Estimated equipment wait when overcrowded</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="kpi kpi-red">
            <div class="kpi-label">Peak Warrior NPS</div>
            <div class="kpi-value">42</div>
            <div class="kpi-note">vs 71 for Off-Peak Regular members</div>
        </div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""<div class="kpi kpi-blue">
            <div class="kpi-label">Worst hour across all locations</div>
            <div class="kpi-value">6:00 PM</div>
            <div class="kpi-note">Consistently highest utilization all year</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("")
    st.markdown('<div class="alert"><strong>The core finding:</strong> Nearly half of all peak hours across the 5 NorthFit locations run above 85% capacity. Members arriving between 5pm and 8pm on weekdays face an average 7.4 minute wait for equipment. Those same members have an NPS score of 42 — almost 30 points below members who come at off-peak times. The data connects overcrowding directly to lower satisfaction and higher churn risk.</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">Average utilization by hour — all locations combined</div>', unsafe_allow_html=True)
        hourly_avg = checkins.groupby("Hour")["Utilization %"].mean().reset_index()
        hourly_avg.columns = ["Hour", "Avg Utilization %"]
        hourly_avg["Is Peak"] = hourly_avg["Hour"].isin([17, 18, 19])
        fig_hour = px.bar(
            hourly_avg, x="Hour", y="Avg Utilization %",
            color="Is Peak",
            color_discrete_map={True: "#C0392B", False: "#94A3B8"},
        )
        fig_hour.add_hline(y=85, line_dash="dash", line_color="#C0392B", annotation_text="85% capacity threshold")
        fig_hour.update_layout(
            height=320, plot_bgcolor="white",
            yaxis=dict(title="Avg Utilization %", gridcolor="#F1F1F1", ticksuffix="%"),
            xaxis=dict(title="Hour of Day", tickmode="linear"),
            showlegend=False,
            margin=dict(t=10, b=20),
        )
        st.plotly_chart(fig_hour, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">Utilization by day of week at peak hours</div>', unsafe_allow_html=True)
        peak_only = checkins[checkins["Is Peak Hour"] == "Yes"]
        day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        day_avg = peak_only.groupby("Day of Week")["Utilization %"].mean().reset_index()
        day_avg["Day of Week"] = pd.Categorical(day_avg["Day of Week"], categories=day_order, ordered=True)
        day_avg = day_avg.sort_values("Day of Week")
        fig_day = px.bar(
            day_avg, x="Day of Week", y="Utilization %",
            color="Utilization %",
            color_continuous_scale=["#94A3B8", "#F59E0B", "#C0392B"],
        )
        fig_day.add_hline(y=85, line_dash="dash", line_color="#C0392B")
        fig_day.update_layout(
            height=320, plot_bgcolor="white",
            yaxis=dict(title="Avg Utilization %", gridcolor="#F1F1F1", ticksuffix="%"),
            xaxis=dict(title=""),
            coloraxis_showscale=False,
            margin=dict(t=10, b=20),
        )
        st.plotly_chart(fig_day, use_container_width=True)

    st.markdown('<div class="section-title">Underutilised windows — where capacity is available right now</div>', unsafe_allow_html=True)
    st.markdown('<div class="finding">While peak hours are overcrowded the same gyms have significant spare capacity between 9am and 3pm on weekdays. A smart member communication system that shows members their nearest location\'s real-time capacity and nudges peak-hour regulars toward these windows is the single highest-impact operational change available without any capital investment.</div>', unsafe_allow_html=True)

    offpeak = checkins[checkins["Is Peak Hour"] == "No"]
    offpeak_avg = offpeak.groupby("Hour")["Utilization %"].mean().reset_index()
    fig_offpeak = px.bar(
        offpeak_avg, x="Hour", y="Utilization %",
        color="Utilization %",
        color_continuous_scale=["#27AE60", "#F59E0B", "#C0392B"],
    )
    fig_offpeak.update_layout(
        height=260, plot_bgcolor="white",
        yaxis=dict(title="Avg Utilization %", gridcolor="#F1F1F1", ticksuffix="%"),
        xaxis=dict(title="Hour of Day", tickmode="linear"),
        coloraxis_showscale=False,
        margin=dict(t=10, b=20),
    )
    st.plotly_chart(fig_offpeak, use_container_width=True)

# ── TAB 2: LOCATION DEEP DIVE ─────────────────────────────────────────────────
with tab2:
    st.markdown('<div class="section-title">Select a location to explore its capacity pattern</div>', unsafe_allow_html=True)

    locations = checkins["Location Name"].unique().tolist()
    selected_loc = st.selectbox("Location", locations, key="loc_select")

    loc_data = checkins[checkins["Location Name"] == selected_loc]
    loc_peak = peak[peak["Location Name"] == selected_loc]

    col1, col2, col3 = st.columns(3)
    with col1:
        avg_util = round(loc_data["Utilization %"].mean(), 1)
        st.markdown(f"""<div class="kpi">
            <div class="kpi-label">Avg utilization all hours</div>
            <div class="kpi-value">{avg_util}%</div>
            <div class="kpi-note">Annual average across all hours</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        peak_util = round(loc_data[loc_data["Is Peak Hour"] == "Yes"]["Utilization %"].mean(), 1)
        card_class = "kpi-red" if peak_util > 85 else "kpi-amber" if peak_util > 70 else "kpi-green"
        st.markdown(f"""<div class="kpi {card_class}">
            <div class="kpi-label">Avg peak hour utilization</div>
            <div class="kpi-value">{peak_util}%</div>
            <div class="kpi-note">5pm to 8pm weekday average</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        oc_hours = loc_data[loc_data["Overcrowded"] == "Yes"].shape[0]
        oc_pct = round(oc_hours / len(loc_data) * 100, 1)
        st.markdown(f"""<div class="kpi kpi-red">
            <div class="kpi-label">Overcrowded hours</div>
            <div class="kpi-value">{oc_pct}%</div>
            <div class="kpi-note">of all operating hours above 85% capacity</div>
        </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">Hourly utilization heatmap by day of week</div>', unsafe_allow_html=True)
        day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        heat_data = loc_data.groupby(["Day of Week","Hour"])["Utilization %"].mean().reset_index()
        heat_pivot = heat_data.pivot(index="Day of Week", columns="Hour", values="Utilization %")
        heat_pivot = heat_pivot.reindex(day_order)
        fig_heat = go.Figure(data=go.Heatmap(
            z=heat_pivot.values,
            x=[f"{h:02d}:00" for h in heat_pivot.columns],
            y=heat_pivot.index.tolist(),
            colorscale=[[0,"#EEF3FB"],[0.5,"#F59E0B"],[0.85,"#C0392B"],[1,"#7B1818"]],
            zmin=0, zmax=100,
            text=[[f"{v:.0f}%" for v in row] for row in heat_pivot.values],
            texttemplate="%{text}",
            textfont=dict(size=9),
            colorbar=dict(title="Util %", ticksuffix="%"),
        ))
        fig_heat.update_layout(
            height=320,
            xaxis=dict(title="Hour of Day"),
            yaxis=dict(title="", autorange="reversed"),
            margin=dict(t=10, b=20),
        )
        st.plotly_chart(fig_heat, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">Monthly utilization trend</div>', unsafe_allow_html=True)
        monthly_util = loc_data.groupby("Month")["Utilization %"].mean().reset_index()
        fig_monthly = px.line(
            monthly_util, x="Month", y="Utilization %",
            markers=True,
            color_discrete_sequence=[LOC_COLORS.get(selected_loc, "#4285F4")],
        )
        fig_monthly.add_hline(y=85, line_dash="dash", line_color="#C0392B", annotation_text="85% threshold")
        fig_monthly.update_layout(
            height=320, plot_bgcolor="white",
            yaxis=dict(title="Avg Utilization %", gridcolor="#F1F1F1", ticksuffix="%"),
            xaxis=dict(title="", tickangle=45),
            margin=dict(t=10, b=60),
        )
        st.plotly_chart(fig_monthly, use_container_width=True)

# ── TAB 3: MEMBER SEGMENTS ────────────────────────────────────────────────────
with tab3:
    st.markdown('<div class="section-title">The four member segments and what they tell us</div>', unsafe_allow_html=True)
    st.markdown('<div class="warning">The Peak Warrior segment is the largest group at 38% of all members and the one most directly affected by overcrowding. Their NPS of 42 is almost 30 points below the Off-Peak Regular segment. The Ghost Member segment accounts for 14% of members and represents revenue that is at imminent risk of cancellation.</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">Member distribution by segment</div>', unsafe_allow_html=True)
        fig_seg = px.pie(
            segments, values="Member Count", names="Segment",
            color="Segment", color_discrete_map=SEG_COLORS, hole=0.45,
        )
        fig_seg.update_layout(height=320, margin=dict(t=10, b=20))
        st.plotly_chart(fig_seg, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">NPS score by segment</div>', unsafe_allow_html=True)
        fig_nps = go.Figure(go.Bar(
            x=segments["Segment"], y=segments["NPS Score"],
            marker_color=[SEG_COLORS[s] for s in segments["Segment"]],
            text=segments["NPS Score"],
            textposition="outside",
        ))
        fig_nps.add_hline(y=50, line_dash="dot", line_color="#888", annotation_text="Benchmark 50")
        fig_nps.update_layout(
            height=320, plot_bgcolor="white",
            yaxis=dict(title="NPS Score", gridcolor="#F1F1F1", range=[0, 90]),
            xaxis=dict(title=""),
            margin=dict(t=10, b=20),
        )
        st.plotly_chart(fig_nps, use_container_width=True)

    st.markdown('<div class="section-title">Segment detail table</div>', unsafe_allow_html=True)
    disp = segments.copy()
    for col in ["Total Annual Revenue CAD", "Annual Revenue at Risk CAD"]:
        disp[col] = disp[col].apply(lambda x: f"${x:,.0f}")
    st.dataframe(disp, use_container_width=True, hide_index=True)

# ── TAB 4: CHURN RISK ─────────────────────────────────────────────────────────
with tab4:
    st.markdown('<div class="section-title">Where the revenue risk sits</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""<div class="kpi kpi-red">
            <div class="kpi-label">Total annual revenue at risk</div>
            <div class="kpi-value">${findings['total_annual_revenue_at_risk']/1000000:.1f}M</div>
            <div class="kpi-note">Across all at-risk member segments</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        ghost_rev = next(r for r in segments.to_dict("records") if r["Segment"] == "Ghost Member")
        st.markdown(f"""<div class="kpi kpi-red">
            <div class="kpi-label">Ghost member count</div>
            <div class="kpi-value">{findings['ghost_member_count']:,}</div>
            <div class="kpi-note">Paying monthly but not visited in 60 or more days</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="kpi kpi-amber">
            <div class="kpi-label">Peak Warrior churn rate</div>
            <div class="kpi-value">18%</div>
            <div class="kpi-note">Estimated annual churn driven by peak frustration</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">Annual revenue at risk by segment</div>', unsafe_allow_html=True)
        fig_risk = go.Figure(go.Bar(
            x=segments["Segment"],
            y=segments["Annual Revenue at Risk CAD"],
            marker_color=[SEG_COLORS[s] for s in segments["Segment"]],
            text=[f"${v:,.0f}" for v in segments["Annual Revenue at Risk CAD"]],
            textposition="outside",
        ))
        fig_risk.update_layout(
            height=320, plot_bgcolor="white",
            yaxis=dict(title="Revenue at Risk (CAD)", gridcolor="#F1F1F1", tickformat="$,.0f"),
            xaxis=dict(title=""),
            margin=dict(t=10, b=20),
        )
        st.plotly_chart(fig_risk, use_container_width=True)

    with col2:
        st.markdown('<div class="section-title">Churn rate vs NPS score by segment</div>', unsafe_allow_html=True)
        fig_scatter = px.scatter(
            segments,
            x="NPS Score", y="Estimated Churn Rate %",
            size="Member Count",
            color="Segment",
            color_discrete_map=SEG_COLORS,
            text="Segment",
            size_max=50,
        )
        fig_scatter.update_traces(textposition="top center", textfont_size=10)
        fig_scatter.update_layout(
            height=320, plot_bgcolor="white",
            xaxis=dict(title="NPS Score", gridcolor="#F1F1F1"),
            yaxis=dict(title="Estimated Churn Rate %", gridcolor="#F1F1F1", ticksuffix="%"),
            showlegend=False,
            margin=dict(t=10, b=20),
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown('<div class="section-title">What the data is telling us about each segment</div>', unsafe_allow_html=True)
    st.markdown(f"""<div class="alert">
        <strong>Ghost Members ({findings['ghost_member_count']:,} members):</strong> These members are paying their monthly fee but have not walked through the door in at least 60 days. Their churn probability is 52%. A targeted re-engagement campaign — a personalised message showing them what they have paid versus what they have used, paired with a low-barrier offer to come back — is the most direct intervention available.
    </div>""", unsafe_allow_html=True)
    st.markdown("""<div class="warning">
        <strong>Peak Warriors (38% of members):</strong> This is the segment most affected by the 6pm problem. Their frustration with equipment wait times is showing up in their NPS scores. They are not gone yet. But without intervention a portion of them will quietly reduce their visits and eventually cancel. The solution is not building more treadmills. It is giving them the information and the incentive to shift their schedule.
    </div>""", unsafe_allow_html=True)

# ── TAB 5: BUSINESS CASE ──────────────────────────────────────────────────────
with tab5:
    st.markdown('<div class="section-title">The business case for a smarter member communication system</div>', unsafe_allow_html=True)
    st.markdown("**The problem is clear from the data. Now here is what fixing it is worth.**")
    st.markdown("")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""<div class="kpi kpi-green">
            <div class="kpi-label">10% retention improvement</div>
            <div class="kpi-value">${findings['retention_10pct_value']:,.0f}</div>
            <div class="kpi-note">Annual revenue protected per year</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div class="kpi kpi-amber">
            <div class="kpi-label">Estimated implementation cost</div>
            <div class="kpi-value">$180,000</div>
            <div class="kpi-note">System build, integration, and rollout</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        payback = round(180000 / (findings['retention_10pct_value'] / 12), 1)
        st.markdown(f"""<div class="kpi kpi-green">
            <div class="kpi-label">Estimated payback period</div>
            <div class="kpi-value">{payback} months</div>
            <div class="kpi-note">Based on conservative 10% retention improvement</div>
        </div>""", unsafe_allow_html=True)
    with col4:
        st.markdown("""<div class="kpi kpi-blue">
            <div class="kpi-label">Segments targeted</div>
            <div class="kpi-value">3 of 4</div>
            <div class="kpi-note">Peak Warriors, Ghost Members, Weekend Warriors</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="section-title">What the system needs to do — requirements summary</div>', unsafe_allow_html=True)
        requirements = [
            {"Priority": "Must Have", "Requirement": "Real-time capacity display per location showing current and forecast utilization", "Benefit": "Lets Peak Warriors see quieter times before they leave home"},
            {"Priority": "Must Have", "Requirement": "Personalised off-peak nudge sent to Peak Warriors 24 hours before their typical visit time", "Benefit": "Shifts demand without reducing it"},
            {"Priority": "Must Have", "Requirement": "Ghost Member re-engagement trigger after 45 days of inactivity", "Benefit": "Catches at-risk members 15 days before the 60-day cancellation window"},
            {"Priority": "Must Have", "Requirement": "Visit history and points balance visible in app for all members", "Benefit": "Makes the value of the membership tangible"},
            {"Priority": "Should Have", "Requirement": "Off-peak visit incentive — bonus points or free class for shifting to quieter windows", "Benefit": "Gives Peak Warriors a reason to change their habit"},
            {"Priority": "Should Have", "Requirement": "Manager dashboard showing daily utilization by location and hour", "Benefit": "Gives operations team the data to make staffing decisions"},
            {"Priority": "Could Have", "Requirement": "Member-facing forecast showing predicted busy times for the next 7 days", "Benefit": "Empowers members to plan around peak hours themselves"},
        ]
        st.dataframe(pd.DataFrame(requirements), use_container_width=True, hide_index=True)

    with col2:
        st.markdown('<div class="section-title">Retention scenario modelling</div>', unsafe_allow_html=True)
        scenarios = []
        for pct in [5, 10, 15, 20]:
            members_retained = int(findings["total_members"] * pct / 100)
            revenue = members_retained * 480
            scenarios.append({"Retention Improvement": f"{pct}%", "Members Retained": members_retained, "Annual Revenue Protected CAD": revenue})

        fig_scenario = px.bar(
            pd.DataFrame(scenarios),
            x="Retention Improvement", y="Annual Revenue Protected CAD",
            color="Annual Revenue Protected CAD",
            color_continuous_scale=["#94A3B8", "#27AE60"],
            text="Annual Revenue Protected CAD",
        )
        fig_scenario.update_traces(texttemplate="$%{text:,.0f}", textposition="outside")
        fig_scenario.update_layout(
            height=340, plot_bgcolor="white",
            yaxis=dict(title="Annual Revenue (CAD)", gridcolor="#F1F1F1", tickformat="$,.0f"),
            xaxis=dict(title="Retention Improvement Scenario"),
            coloraxis_showscale=False,
            margin=dict(t=10, b=20),
        )
        st.plotly_chart(fig_scenario, use_container_width=True)

st.divider()
st.markdown(
    "**Data note:** All check-in data is synthetic and generated for portfolio purposes. "
    "NorthFit is a fictional fitness chain. Utilization patterns, member segments, and churn rates "
    "are modelled on publicly available fitness industry benchmarks. "
    "Prepared by Simran Saran as part of The Case Files portfolio series."
)

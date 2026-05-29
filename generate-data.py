import csv
import random
import json
from datetime import date, timedelta
import math

random.seed(42)

LOCATIONS = {
    "LOC-001": {"name": "Mississauga City Centre", "capacity": 180, "total_members": 2400},
    "LOC-002": {"name": "Toronto Downtown",        "capacity": 220, "total_members": 3100},
    "LOC-003": {"name": "Scarborough",             "capacity": 150, "total_members": 1800},
    "LOC-004": {"name": "Brampton North",          "capacity": 160, "total_members": 2000},
    "LOC-005": {"name": "Etobicoke",               "capacity": 170, "total_members": 2200},
}

# Hourly visit counts as % of capacity -- realistic gym loading
HOUR_PCT_OF_CAPACITY = {
    5: 0.08, 6: 0.22, 7: 0.48, 8: 0.38, 9: 0.28,
    10: 0.22, 11: 0.20, 12: 0.35, 13: 0.28, 14: 0.18,
    15: 0.22, 16: 0.42, 17: 0.78, 18: 0.96, 19: 0.88,
    20: 0.58, 21: 0.32, 22: 0.14, 23: 0.06,
}

DAY_MULTIPLIER = {0:1.15, 1:1.10, 2:1.05, 3:1.05, 4:0.90, 5:0.65, 6:0.45}

MEMBER_SEGMENTS = {
    "Peak Warrior":     {"weight":38,"monthly_visits":(14,3),"churn_risk":"Medium","nps":42,"annual_fee":480},
    "Off-Peak Regular": {"weight":28,"monthly_visits":(16,2),"churn_risk":"Low",   "nps":71,"annual_fee":480},
    "Weekend Warrior":  {"weight":20,"monthly_visits":(8,3), "churn_risk":"Medium","nps":58,"annual_fee":480},
    "Ghost Member":     {"weight":14,"monthly_visits":(1,1), "churn_risk":"High",  "nps":18,"annual_fee":480},
}

start_date = date(2024,1,1)
end_date   = date(2024,12,31)

checkins = []
checkin_id = 1

for loc_id, loc in LOCATIONS.items():
    cap = loc["capacity"]
    current_date = start_date
    while current_date <= end_date:
        dow = current_date.weekday()
        day_mult = DAY_MULTIPLIER[dow]
        for hour in range(5,24):
            base_pct = HOUR_PCT_OF_CAPACITY.get(hour,0.05) * day_mult
            noise = random.gauss(1.0, 0.12)
            pct = max(0.02, base_pct * noise)
            visits = max(1, int(cap * pct))
            utilization = round(visits / cap * 100, 1)
            overcrowded = utilization > 85
            wait_time = round((utilization - 85) * 0.5) if overcrowded else 0

            checkins.append({
                "Checkin ID":              f"CHK{str(checkin_id).zfill(7)}",
                "Location ID":             loc_id,
                "Location Name":           loc["name"],
                "Date":                    current_date.strftime("%Y-%m-%d"),
                "Month":                   current_date.strftime("%Y-%m"),
                "Day of Week":             current_date.strftime("%A"),
                "Hour":                    hour,
                "Time Slot":               f"{hour:02d}:00",
                "Member Visits":           visits,
                "Location Capacity":       cap,
                "Utilization %":           utilization,
                "Overcrowded":             "Yes" if overcrowded else "No",
                "Estimated Wait Minutes":  wait_time,
                "Is Weekend":              "Yes" if dow >= 5 else "No",
                "Is Peak Hour":            "Yes" if hour in [17,18,19] else "No",
            })
            checkin_id += 1
        current_date += timedelta(days=1)

with open('/home/claude/northfit-analytics/checkin-data.csv','w',newline='') as f:
    w = csv.DictWriter(f, fieldnames=checkins[0].keys())
    w.writeheader(); w.writerows(checkins)

print(f"Check-in dataset: {len(checkins)} hourly records")

overcrowded_list = [r for r in checkins if r["Overcrowded"]=="Yes"]
peak_list        = [r for r in checkins if r["Is Peak Hour"]=="Yes"]
peak_overcrowded = [r for r in peak_list  if r["Overcrowded"]=="Yes"]

print(f"Overcrowded records: {len(overcrowded_list)}")
print(f"Peak overcrowded: {len(peak_overcrowded)} of {len(peak_list)} ({round(len(peak_overcrowded)/len(peak_list)*100,1)}%)")

# Peak hour summary by location and hour
from collections import defaultdict
ph_agg = defaultdict(lambda:{"visits":0,"overcrowded":0,"wait":0,"count":0})
for r in checkins:
    k=(r["Location ID"],r["Hour"])
    ph_agg[k]["visits"]+=int(r["Member Visits"])
    ph_agg[k]["count"]+=1
    if r["Overcrowded"]=="Yes":
        ph_agg[k]["overcrowded"]+=1
        ph_agg[k]["wait"]+=int(r["Estimated Wait Minutes"])

peak_rows=[]
for (loc_id,hour),d in sorted(ph_agg.items()):
    cap=LOCATIONS[loc_id]["capacity"]
    avg_visits=round(d["visits"]/d["count"],1)
    util=round(avg_visits/cap*100,1)
    oc_pct=round(d["overcrowded"]/d["count"]*100,1)
    avg_wait=round(d["wait"]/max(d["overcrowded"],1),1)
    peak_rows.append({
        "Location ID":loc_id,"Location Name":LOCATIONS[loc_id]["name"],
        "Hour":hour,"Time Slot":f"{hour:02d}:00",
        "Avg Member Visits":avg_visits,"Location Capacity":cap,
        "Avg Utilization %":util,"Overcrowded % of Days":oc_pct,
        "Avg Wait Minutes When Overcrowded":avg_wait,
        "Is Peak Hour":"Yes" if hour in [17,18,19] else "No",
    })

with open('/home/claude/northfit-analytics/peak-analysis.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=peak_rows[0].keys()); w.writeheader(); w.writerows(peak_rows)

# Member segments
total_members=sum(loc["total_members"] for loc in LOCATIONS.values())
seg_rows=[]
for seg_name,seg in MEMBER_SEGMENTS.items():
    count=int(total_members*seg["weight"]/100)
    churn_rate={"Low":0.08,"Medium":0.18,"High":0.52}[seg["churn_risk"]]
    rev_at_risk=round(count*churn_rate*seg["annual_fee"],0)
    seg_rows.append({
        "Segment":seg_name,"Member Count":count,
        "% of Total Members":seg["weight"],
        "Avg Monthly Visits":seg["monthly_visits"][0],
        "Annual Fee CAD":seg["annual_fee"],
        "Total Annual Revenue CAD":count*seg["annual_fee"],
        "Churn Risk":seg["churn_risk"],
        "Estimated Churn Rate %":round(churn_rate*100,0),
        "Annual Revenue at Risk CAD":rev_at_risk,
        "NPS Score":seg["nps"],
    })

with open('/home/claude/northfit-analytics/member-segments.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=seg_rows[0].keys()); w.writeheader(); w.writerows(seg_rows)

avg_wait_peak = round(sum(int(r["Estimated Wait Minutes"]) for r in overcrowded_list)/max(len(overcrowded_list),1),1)
total_at_risk  = sum(r["Annual Revenue at Risk CAD"] for r in seg_rows)

findings={
    "total_members":total_members,
    "total_locations":len(LOCATIONS),
    "overcrowded_hours_pct":round(len(overcrowded_list)/len(checkins)*100,1),
    "peak_hour_overcrowded_pct":round(len(peak_overcrowded)/len(peak_list)*100,1),
    "worst_location":"Toronto Downtown",
    "worst_hour":"18:00",
    "avg_wait_at_peak":avg_wait_peak,
    "total_annual_revenue_at_risk":round(total_at_risk,0),
    "retention_10pct_value":round(total_members*0.10*480,0),
    "ghost_member_count":next(r["Member Count"] for r in seg_rows if r["Segment"]=="Ghost Member"),
    "peak_warrior_nps":42,
    "offpeak_regular_nps":71,
}

with open('/home/claude/northfit-analytics/key-findings.json','w') as f:
    json.dump(findings,f,indent=2)

summary=[
    ["Metric","Value","Notes"],
    ["Total members across 5 locations",f"{total_members:,}","GTA locations combined"],
    ["Peak hour overcrowding rate",f"{findings['peak_hour_overcrowded_pct']}%","Hours where utilization exceeds 85% capacity"],
    ["Average wait time at peak",f"{findings['avg_wait_at_peak']} minutes","Estimated equipment wait when overcrowded"],
    ["Worst location",findings["worst_location"],"Highest sustained peak utilization in the chain"],
    ["Busiest hour",findings["worst_hour"],"6pm consistently highest across all locations"],
    ["Ghost members",str(findings["ghost_member_count"]),"Paying monthly but not visited in 60 or more days"],
    ["Total annual revenue at risk",f"${findings['total_annual_revenue_at_risk']:,.0f}","Across all at-risk member segments"],
    ["Value of 10% retention improvement",f"${findings['retention_10pct_value']:,.0f}","Annual revenue protected"],
    ["Peak Warrior NPS",str(findings["peak_warrior_nps"]),"vs 71 for Off-Peak Regular members"],
]

with open('/home/claude/northfit-analytics/analysis-summary.csv','w',newline='') as f:
    w=csv.writer(f); w.writerows(summary)

print(f"\nFindings:")
print(f"  Peak overcrowded: {findings['peak_hour_overcrowded_pct']}% of hours")
print(f"  Avg wait: {findings['avg_wait_at_peak']} min")
print(f"  Revenue at risk: ${findings['total_annual_revenue_at_risk']:,.0f}")
print(f"  10% retention value: ${findings['retention_10pct_value']:,.0f}")
print("All files written.")

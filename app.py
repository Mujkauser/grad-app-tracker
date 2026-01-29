import streamlit as st
import pandas as pd
from datetime import date, datetime

st.set_page_config(page_title="Grad App Tracker", layout="wide")

# ---------- DATA ----------
data = [
    ["NYU Tandon", "MS Management of Technology", "2025-12-01", "Admit", "No Interview", None , "2025-12-20"],
    ["Northeastern", "MS in Engineering Management", "2025-12-01", "Admit", "No Interview", None, "2025-12-19"],
    ["Duke", "Master of Engineering Management", "2025-12-08", "Awaiting Decision", "No Interview", "2026-01-30", None],
    ["Dartmouth", "MEM", "2025-12-14", "Under Review", "Awaiting Interview invite", "2026-03-15", None],
    ["Georgia Tech (MS)", "MS Management", "2025-12-15", "Under Review", "No Interview", "2026-02-24", None],
    ["Georgia Tech (MBA)", "MBA", "2026-01-10", "Under Review", "Awaiting Interview invite", "2026-02-27", None],
    ["Northwestern", "Master of Engineering Management", "2025-12-15", "Awaiting Decision", "interview Done", "2026-02-15", None],
    ["Purdue", "MS in Engineering Management", "2025-12-24", "Under Review", "interview Done", "2026-02-15", None],
    ["Johns Hopkins", "MEM", "2025-12-24", "Under Review", "Awaiting Interview invite", "2026-03-15", None],
    ["Columbia", "MS Management Science & Engineering", "2025-12-26", "Under Review", "Awaiting Interview invite", "2026-02-15", None],
    ["Cornell", "MEng Engineering Management", "2025-12-28", "Under Review", "Awaiting Interview invite", "2026-03-15", None],
    ["Tufts", "MS in Engineering Management", "2025-12-28", "Under Review", "No Interview", "2026-01-30", None]
]

columns = [
    "University",
    "Program",
    "Applied On",
    "Status",
    "Interview",
    "Decision By",
    "Admit Received On"
]

df = pd.DataFrame(data, columns=columns)

# ---------- DATE CALCULATIONS ----------
today = date.today()

def parse(d):
    return datetime.strptime(d, "%Y-%m-%d").date() if d else None

df["Applied On"] = df["Applied On"].apply(parse)
df["Decision By"] = df["Decision By"].apply(parse)
df["Days Since Applied"] = df["Applied On"].apply(lambda x: (today - x).days)
df["Days Until Decision"] = df["Decision By"].apply(lambda x: (x - today).days if x else None)
df["Admit Received On"] = df["Admit Received On"].apply(parse)


# ---------- STATUS LOGIC ----------
def health(row):
    if row["Status"] == "Admit":
        return "🏆 Admit Secured"

    if row["Days Until Decision"] is not None and row["Days Until Decision"] <= 0:
        return "🟡 Decision Window Open"

    return "🟢 Safe"

df["Health"] = df.apply(health, axis=1)

df["Decision Turnaround (Days)"] = df.apply(
    lambda row: (row["Admit Received On"] - row["Applied On"]).days
    if row["Status"] == "Admit" and row["Admit Received On"] is not None
    else None,
    axis=1
)

ordered_columns = [
    "University",
    "Program",
    "Applied On",
    "Status",
    "Interview",
    "Decision By",
    "Admit Received On",
    "Decision Turnaround (Days)",
    "Days Since Applied",
    "Days Until Decision",
    "Health"
]

df = df[ordered_columns]

# ---------- UI ----------
st.title("🎓 Graduate Application Tracker")
st.caption("Anxiety-managed. Engineer-approved.")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("✅ Total Admits", df[df["Status"] == "Admit"].shape[0])

with col2:
    st.metric("⏳ Awaiting Decisions", df[df["Status"] != "Admit"].shape[0])

with col3:
    attention = df[df["Health"] == "🟡 Decision Window Open"].shape[0]
    st.metric("👀 Decisions In Progress", attention)


st.divider()

st.subheader("Dashboard")
st.dataframe(
    df.sort_values(by=["Health", "Days Until Decision"], na_position="last"),
    use_container_width=True
)

st.divider()

st.divider()
st.subheader("📈 Decision Speed Insights")

avg_turnaround = df["Decision Turnaround (Days)"].dropna().mean()

if not pd.isna(avg_turnaround):
    st.info(f"⏱️ Average admit turnaround so far: **{int(avg_turnaround)} days**")


# ---------- REALITY CHECK ----------
st.subheader("🧠 Reality Check")

overdue = df[(df["Days Until Decision"].notna()) & (df["Days Until Decision"] < 0)]

if overdue.empty:
    st.success("✅ No universities are overdue. Everything is on track. Breathe.")
else:
    st.warning("⚠️ Some decisions are past the expected date (still normal, but noted).")

st.caption("This dashboard updates daily. You don’t need to.")


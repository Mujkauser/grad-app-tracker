import streamlit as st
import pandas as pd
from datetime import date, datetime

st.set_page_config(page_title="Grad App Tracker", layout="wide")

# ---------- DATA ----------
data = [
    ["NYU Tandon", "MS Management of Technology", "2025-12-01", "Admit", "No Interview", None],
    ["Northeastern", "MS in Engineering Management", "2025-12-01", "Admit", "No Interview", None],
    ["Duke", "Master of Engineering Management", "2025-12-08", "Awaiting Decision", "No Interview", "2026-01-30"],
    ["Dartmouth", "MEM", "2025-12-14", "Under Review", "Awaiting Interview invite", "2026-03-15"],
    ["Georgia Tech (MS)", "MS Management", "2025-12-15", "Under Review", "No Interview", "2026-02-24"],
    ["Georgia Tech (MBA)", "MBA", "2026-01-10", "Under Review", "Awaiting Interview invite", "2026-02-27"],
    ["Northwestern", "Master of Engineering Management", "2025-12-15", "Awaiting Decision", "interview Done", "2026-02-15"],
    ["Purdue", "MS in Engineering Management", "2025-12-24", "Under Review", "interview Done", "2026-02-15"],
    ["Johns Hopkins", "MEM", "2025-12-24", "Under Review", "Awaiting Interview invite", "2026-03-15"],
    ["Columbia", "MS Management Science & Engineering", "2025-12-26", "Under Review", "Awaiting Interview invite", "2026-02-15"],
    ["Cornell", "MEng Engineering Management", "2025-12-28", "Under Review", "Awaiting Interview invite", "2026-03-15"],
    ["Tufts", "MS in Engineering Management", "2025-12-28", "Under Review", "No Interview", "2026-01-30"]
]

columns = [
    "University",
    "Program",
    "Applied On",
    "Status",
    "Interview",
    "Decision By",
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

# ---------- STATUS LOGIC ----------
def health(row):
    if row["Status"] == "Admit":
        return "🏆 Admit Secured"

    if row["Days Until Decision"] is not None and row["Days Until Decision"] <= 0:
        return "🟡 Decision Window Open"

    return "🟢 Safe"

df["Health"] = df.apply(health, axis=1)

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

# ---------- REALITY CHECK ----------
st.subheader("🧠 Reality Check")

overdue = df[(df["Days Until Decision"].notna()) & (df["Days Until Decision"] < 0)]

if overdue.empty:
    st.success("✅ No universities are overdue. Everything is on track. Breathe.")
else:
    st.warning("⚠️ Some decisions are past the expected date (still normal, but noted).")

st.caption("This dashboard updates daily. You don’t need to.")


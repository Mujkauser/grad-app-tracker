import streamlit as st
import pandas as pd
from datetime import date, datetime

st.set_page_config(page_title="Grad App Tracker", layout="wide")

# ---------- DATA (FROM GOOGLE SHEETS) ----------
SHEET_ID = "1hYhyNIJhxZ4Em4Yi-cBq5UxOMGVr8G5p_-n1ceto0Q0"
SHEET_NAME = "Sheet1"   # change if your tab name is different

csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

df = pd.read_csv(csv_url)
st.write(df.head())

# ---------- DATE CALCULATIONS ----------
today = date.today()

df["Applied On"] = pd.to_datetime(df["Applied On"], errors="coerce").dt.date
df["Decision By"] = pd.to_datetime(df["Decision By"], errors="coerce").dt.date
df["Days Since Applied"] = df["Applied On"].apply(lambda x: (today - x).days)
df["Days Until Decision"] = df["Decision By"].apply(lambda x: (x - today).days if x else None)
df["Admit Received On"] = pd.to_datetime(df["Admit Received On"], errors="coerce").dt.date


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


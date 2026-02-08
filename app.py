import streamlit as st
import pandas as pd
from datetime import date, datetime

st.set_page_config(page_title="Grad App Tracker", layout="wide")

# ---------- DATA (FROM GOOGLE SHEETS) ----------
SHEET_ID = "1hYhyNIJhxZ4Em4Yi-cBq5UxOMGVr8G5p_-n1ceto0Q0"
SHEET_NAME = "Sheet1"   # change if your tab name is different

csv_url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

df = pd.read_csv(csv_url)

# ---------- DATE CALCULATIONS ----------
# st.caption(f"🔄 Last refreshed at {datetime.now().strftime('%H:%M:%S')}")
today_msg = "🌿 Journey built on Tawakkul: Do your part, then trust Allah with the rest."
st.info(today_msg)
today = date.today()

df["Applied On"] = pd.to_datetime(df["Applied On"], errors="coerce").dt.date
df["Decision By"] = pd.to_datetime(df["Decision By"], errors="coerce").dt.date
df["Admit Received On"] = pd.to_datetime(df["Admit Received On"], errors="coerce").dt.date


# ---------- STATUS LOGIC ----------
def health(row):
    if row["Status"] == "Admit":
        return "🏆 Admit Secured"

    if row["Interview"] == "Interview Done":
        return "🟡 Decision In Progress"

    return "🟢 In Review"
    
df["Health"] = df.apply(health, axis=1)

ordered_columns = [
    "University",
    "Program",
    "Applied On",
    "Interview",
    "Status",
    "Decision By",
    "Admit Received On",
    "Health"
]

df = df.reindex(columns=ordered_columns)

# ---------- UI ----------
st.title("🎓 Graduate Application Tracker")

#st.divider()

# --------- metrics -------------

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("✅ Total Admits ", df[df["Status"] == "Admit"].shape[0])

with col2:
    st.metric("⏳ Awaiting Decisions", df[df["Status"] != "Admit"].shape[0])

with col3:
    attention = df[df["Health"].str.contains("Decision")].shape[0]
    st.metric("👀 Actively Unfolding", attention)

#st.divider()

st.markdown("### 📜 Where Things Stand (Today)")
st.dataframe(
    df.sort_values(by=["Health", "University"]),
    use_container_width=True
)

st.divider()

# ---------- REALITY CHECK ----------
st.subheader("🧠 Reality Check")

overdue = df[
    (df["Decision By"].notna()) &
    (df["Decision By"] < today) &
    (df["Status"] != "Admit")
]

if overdue.empty:
    st.success("✅ Nothing appears delayed. Everything is unfolding as it should.")
else:
    st.info("Some decisions are taking longer than expected — this is common and not a concern.")

st.divider()
st.markdown("""
> **“What is written for you will reach you,  even if it is beneath two mountains.”**

Nothing here is late.  
Nothing here is missed.  
What’s meant for you in marriage, knowledge, and work is on its way.
""")

from datetime import datetime

st.caption("This dashboard updates daily. You don’t need to.")


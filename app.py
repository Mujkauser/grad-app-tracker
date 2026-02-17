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

# ---------- PERSONAL MILESTONE ----------
clarity_date = date(2026, 3, 31)
days_to_clarity = (clarity_date - today).days
clarity_start = date(2026, 3, 10)   # last 10 days begin
clarity_end = date(2026, 3, 30)     # Ramadan end / closure

df["Applied On"] = pd.to_datetime(df["Applied On"], errors="coerce").dt.date
df["Decision By"] = pd.to_datetime(df["Decision By"], errors="coerce").dt.date
df["Admit Received On"] = pd.to_datetime(df["Admit Received On"], errors="coerce").dt.date
df["Enrollment Deadline"] = pd.to_datetime(df["Enrollment Deadline"], errors="coerce").dt.date

# ---------- STATUS LOGIC ----------
def health(row):
    status = str(row["Status"]).strip().lower()
    interview = str(row["Interview"]).strip().lower()

    # 1. Final outcome
    if status == "admit":
        return "🏆 Admit Secured"

    # 2. Explicit awaiting decision
    if status == "awaiting decision":
        return "🟡 Decision In Progress"

    # 3. Any interview already happened or scheduled
    if (
        "interview" in interview
        and "awaiting" not in interview
        and "no interview" not in interview
    ):
        return "🟡 Decision In Progress"

    # 4. Still early / waiting
    if "awaiting interview" in interview or status == "under review":
        return "🟢 In Review"

    if status in ["reject", "rejected"]:
        return "😅 Rejected, Alhamdulillah"

    return "🟢 In Review"
    
df["Health"] = df.apply(health, axis=1)

ordered_columns = [
    "University",
    "Program",
    "Campus",
    "Applied On",
    "Status",
    "Interview",
    "Decision By",
    "Admit Received On",
    "Enrollment Deadline",
    "Health"
]

df = df.reindex(columns=ordered_columns)

# ---------- UI ----------
st.title("🎓 Graduate Application Tracker")

#st.divider()

st.markdown("### 🌙 A Moment of Tawakkul")

if today < clarity_start:
    days_to_clarity = (clarity_start - today).days
    st.info(
        f"🕊️ **{days_to_clarity} days** until the final days of Ramadan.\n\n"
        "Until then, take the means — and let Allah arrange the outcome."
    )

elif clarity_start <= today <= clarity_end:
    days_left = (clarity_end - today).days
    st.warning(
        f"🌙 **Days of Clarity**\n\n"
        f"The last days of Ramadan are unfolding.\n"
        f"**{days_left} days** remain to make duʿā, seek signs, and surrender fully."
    )

else:
    st.success(
        "🌱 **This matter has been released to Allah.**\n\n"
        "What was meant to reach you has reached.\n"
        "What didn’t was never meant to weigh you down.\n\n"
        "**Sabr now. Trust always.**"
    )

# --------- metrics -------------

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("✅ Total Admits ", df[df["Status"] == "Admit"].shape[0])

with col2:
    st.metric(
        "⏳ Awaiting Decisions",
        df[~df["Status"].isin(["Admit", "Reject", "Rejected"])].shape[0]
    )
    
with col3:
    st.metric("😅 Total Rejects", df[df["Health"].str.contains("Reject")].shape[0])

with col4:
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


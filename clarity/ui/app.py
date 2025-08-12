# clarity/ui/app.py
import os
import streamlit as st
import pandas as pd
from datetime import datetime

# ensure project-root relative paths work
BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)))  # clarity/
DB_PATH = os.path.join(BASE_DIR, "data", "clarity.db")

# add clarity/scripts to path if needed (so we can import modules)
import sys
sys.path.insert(0, os.path.join(BASE_DIR, "scripts"))

# backend functions
from goal_tracker import init_db, log_hours, get_all_logs, get_weekly_avg, check_targets
from suggestion_engine import generate_suggestions

# Ensure DB exists and folder is present
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
init_db()

# Streamlit page config
st.set_page_config(page_title="Clarity — Self-Growth Copilot (MVP)", layout="centered")
st.title("🔵 Clarity — Self-Growth Copilot (MVP)")

# Sidebar nav
menu = ["Home", "Log Hours", "Weekly Report", "Suggestions", "View Logs"]
choice = st.sidebar.selectbox("Navigate", menu)

def df_from_db_rows(rows):
    if not rows:
        return pd.DataFrame(columns=["id", "date", "pillar", "hours"])
    return pd.DataFrame(rows, columns=["id", "date", "pillar", "hours"])

if choice == "Home":
    st.subheader("Welcome")
    st.markdown(
        """
        **Clarity** helps you track your Dev / DSA / GATE hours and gives one simple action each day.
        Use **Log Hours** to add today's work, then visit **Weekly Report** and **Suggestions**.
        """
    )
    st.info("Built for hostel + limited time. Keep it simple, ship daily.")

elif choice == "Log Hours":
    st.subheader("Log Today's Hours")
    with st.form("log_form"):
        pillar = st.selectbox("Pillar", ["Dev", "DSA", "GATE"])
        hours = st.number_input("Hours spent (0.0 - 12.0)", min_value=0.0, max_value=12.0, step=0.25)
        submitted = st.form_submit_button("Log")
        if submitted:
            log_hours(pillar, float(hours))
            st.success(f"Logged {hours} hours for {pillar} at {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    st.markdown("---")
    st.caption("Tip: log honestly. Clarity uses real averages to suggest actions.")

elif choice == "Weekly Report":
    st.subheader("Weekly Averages & Target Status")
    status = check_targets()  # structured dict
    # Convert to dataframe for nice display
    rows = []
    for p, d in status.items():
        rows.append({"Pillar": p, "Avg hrs/day": d["avg"], "Target hrs/day": d["target"], "Status": d["status"]})
    df = pd.DataFrame(rows)
    st.table(df)

    # show bar chart for weekly totals (sum of last 7 days)
    all_rows = get_all_logs()
    df_logs = df_from_db_rows(all_rows)
    if not df_logs.empty:
        chart_df = df_logs.groupby("pillar")["hours"].sum().reset_index()
        chart_df.columns = ["Pillar", "Hours (last 7 days)"]
        st.bar_chart(chart_df.set_index("Pillar"))

elif choice == "Suggestions":
    st.subheader("Actionable Suggestions (Today)")
    status = check_targets()
    suggestions_out = generate_suggestions(status)
    for line in suggestions_out["summary_lines"]:
        st.markdown(line)

    st.markdown("---")
    st.write("Structured suggestions (debug):")
    st.json(suggestions_out["suggestions"])

elif choice == "View Logs":
    st.subheader("View All Logs")
    rows = get_all_logs()
    df_logs = df_from_db_rows(rows)
    st.dataframe(df_logs.sort_values(by="date", ascending=False))

    if not df_logs.empty:
        with st.expander("Show pretty aggregated table"):
            st.table(df_logs.groupby("pillar")["hours"].sum().rename("Total hrs").reset_index())

# Footer
st.markdown("---")
st.caption("Clarity MVP — staged build. Stage 4: UI Integration. Next: Journal Analyzer (Week 2).")

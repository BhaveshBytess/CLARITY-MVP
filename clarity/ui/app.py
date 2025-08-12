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
import plotly.express as px
import plotly.graph_objects as go

# Ensure DB exists and folder is present
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
init_db()

# Streamlit page config
st.set_page_config(page_title="Clarity — Self-Growth Copilot (MVP)", layout="centered")
st.markdown(
    """
    <style>
    .report-card {
        background: #ffffff;
        padding: 10px;
        border-radius: 10px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.08);
        margin-bottom: 12px;
    }
    /* Narrow layout max width */
    .main .block-container {
        max-width: 900px;
    }
    </style>
    """,
    unsafe_allow_html=True
)
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

    # Structured status
    status = check_targets()  # structured dict
    rows = []
    for p, d in status.items():
        rows.append({"Pillar": p, "Avg hrs/day": d["avg"], "Target hrs/day": d["target"], "Status": d["status"]})
    df_status = pd.DataFrame(rows)
    st.table(df_status)

    # Weekly totals bar chart (last 7 days)
    from goal_tracker import get_weekly_totals
    totals = get_weekly_totals()  # dict {pillar: total_hours_last_7_days}
    tot_df = pd.DataFrame(list(totals.items()), columns=["Pillar", "Hours (last 7 days)"])
    fig = px.bar(tot_df, x="Pillar", y="Hours (last 7 days)",
                 text="Hours (last 7 days)",
                 title="Weekly total hours per pillar",
                 labels={"Hours (last 7 days)": "Hours (7 days)"})
    fig.update_traces(textposition='outside')
    fig.update_layout(yaxis=dict(title="Hours (7-day total)"), xaxis=dict(title="Pillar"), uniformtext_minsize=8, uniformtext_mode='hide')
    st.plotly_chart(fig, use_container_width=True)

    # Percent progress toward daily target (avg/target * 100) as horizontal bars
    percent_rows = []
    for p, d in status.items():
        pct = 0.0
        if d["target"] > 0:
            pct = min(150, round((d["avg"] / d["target"]) * 100, 1))  # cap at 150%
        percent_rows.append({"Pillar": p, "PercentOfDailyTarget": pct})

    pct_df = pd.DataFrame(percent_rows)
    # Horizontal bar chart
    fig2 = px.bar(pct_df, x="PercentOfDailyTarget", y="Pillar", orientation='h',
                  text="PercentOfDailyTarget",
                  title="Daily progress vs target (% of daily target)")
    fig2.update_layout(xaxis=dict(title="% of daily target (100% = on target)"), yaxis=dict(categoryorder="total ascending"))
    st.plotly_chart(fig2, use_container_width=True)

    # Optional: show progress with Streamlit's progress widget too (simple)
    st.markdown("### Quick progress bars")
    for idx, r in pct_df.iterrows():
        st.write(f"**{r['Pillar']}** — {r['PercentOfDailyTarget']}% of daily target")
        st.progress(int(r['PercentOfDailyTarget'] if r['PercentOfDailyTarget'] <= 100 else 100))

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

import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# =====================
# DB FUNCTIONS
# =====================
DB_PATH = "clarity/data/clarity.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS pillar_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            pillar TEXT,
            hours REAL
        )
    ''')
    conn.commit()
    conn.close()

def log_hours(pillar, hours):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO pillar_logs (date, pillar, hours) VALUES (?, ?, ?)",
              (datetime.now().strftime("%Y-%m-%d"), pillar, hours))
    conn.commit()
    conn.close()

def get_weekly_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM pillar_logs", conn)
    conn.close()
    return df

# =====================
# SUGGESTION ENGINE (Week 1 basic rule-based)
# =====================
TARGETS = {"Dev": 1.5, "DSA": 1, "GATE": 1}  # hours/day

def generate_suggestions(df):
    suggestions = []
    if df.empty:
        return ["No data yet. Start logging your hours today!"]

    last_7 = df.tail(7)
    avg_hours = last_7.groupby("pillar")["hours"].mean().to_dict()

    for pillar, target in TARGETS.items():
        if avg_hours.get(pillar, 0) < target:
            suggestions.append(f"⚠ {pillar} below target! Spend at least {target - avg_hours.get(pillar, 0):.1f} more hours today.")
        else:
            suggestions.append(f"✅ {pillar} on track! Keep it up.")

    return suggestions

# =====================
# STREAMLIT UI
# =====================
def main():
    st.set_page_config(page_title="Clarity - MVP", layout="centered")
    st.title("📊 Clarity - Self-Growth AI Copilot (MVP)")

    # Navigation
    menu = ["Log Hours", "View Progress", "Suggestions"]
    choice = st.sidebar.selectbox("Navigate", menu)

    if choice == "Log Hours":
        st.subheader("Log Daily Hours")
        pillar = st.selectbox("Select Pillar", list(TARGETS.keys()))
        hours = st.number_input("Hours Spent", min_value=0.0, max_value=12.0, step=0.5)
        if st.button("Log Entry"):
            log_hours(pillar, hours)
            st.success(f"✅ Logged {hours} hours for {pillar}.")

    elif choice == "View Progress":
        st.subheader("Weekly Progress")
        df = get_weekly_data()
        if df.empty:
            st.warning("No data to show yet. Log some hours first.")
        else:
            st.dataframe(df)
            st.bar_chart(df.groupby("pillar")["hours"].sum())

    elif choice == "Suggestions":
        st.subheader("Actionable Suggestions")
        df = get_weekly_data()
        for s in generate_suggestions(df):
            st.write(s)

if __name__ == "__main__":
    init_db()
    main()

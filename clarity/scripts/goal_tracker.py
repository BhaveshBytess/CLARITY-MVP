import sqlite3
import os

# =====================
# DB FUNCTIONS
# =====================
DB_PATH = "clarity/data/clarity.db"

# Make a DB init Script
def init_db():
    # Make sure /data exists
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

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

if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DB_PATH}")



# LOGGING DAILY HOURS
from datetime import datetime, timedelta

def log_hours(pillar, hours):
    """Insert a new record into pillar_logs table."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO pillar_logs (date, pillar, hours)
        VALUES (?, ?, ?)
    """, (datetime.now().strftime("%Y-%m-%d"), pillar, hours))
    conn.commit()
    conn.close()
    print(f"✅ Logged {hours} hours for {pillar}.")

if __name__ == "__main__":
    log_hours("Dev", 2.0)

# FETCH ALL LOGS
def get_all_logs():
    """Retrieve all logs from DB."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM pillar_logs ORDER BY date DESC;")
    rows = c.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    print(get_all_logs())

# Weekly average calculator
TARGETS = {"Dev": 1.5, "DSA": 1, "GATE": 1}

def get_weekly_avg():
    """
    Calculate average hours per pillar for the last 7 calendar days.
    Missing days are counted as 0 hours.
    Returns dict: {pillar: avg_hours}
    """
    # ensure DB path/folder exist (defensive)
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # list of last 7 dates (strings), including today
    seven_days = [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]

    avg_result = {}
    for pillar in TARGETS.keys():
        total_hours = 0.0
        for d in seven_days:
            c.execute("SELECT SUM(hours) FROM pillar_logs WHERE date = ? AND pillar = ?", (d, pillar))
            row = c.fetchone()
            hours_for_day = row[0] if (row and row[0] is not None) else 0.0
            total_hours += hours_for_day
        # divide by 7 to get hours-per-day average
        avg_result[pillar] = round(total_hours / 7.0, 2)

    conn.close()
    return avg_result

if __name__ == "__main__":
    print(get_weekly_avg())


# Target check function
def check_targets():
    """Compare weekly averages with target hours, return structured dict."""
    avg_hours = get_weekly_avg()
    status_dict = {}

    for pillar, target in TARGETS.items():
        current = avg_hours.get(pillar, 0)
        if current >= target:
            status = "✅ On track"
        else:
            status = f"⚠ Below target by {round(target - current, 2):.2f} hrs/day"

        status_dict[pillar] = {
            "avg": current,
            "target": target,
            "status": status
        }

    return status_dict


if __name__ == "__main__":
    from pprint import pprint
    pprint(check_targets())


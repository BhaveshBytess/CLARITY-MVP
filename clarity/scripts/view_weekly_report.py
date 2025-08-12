import sqlite3
from datetime import datetime, timedelta
from tabulate import tabulate

DB_PATH = "clarity/data/clarity.db"

# Hardcoded targets (hrs/day)
TARGETS = {"Dev": 1.5, "DSA": 1, "GATE": 1}

def get_weekly_avg():
    """Calculate average hours per pillar for the last 7 days."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    c.execute("""
        SELECT pillar, AVG(hours) as avg_hours
        FROM pillar_logs
        WHERE date >= ?
        GROUP BY pillar
    """, (seven_days_ago,))

    results = dict(c.fetchall())
    conn.close()
    return results

def generate_report():
    avg_hours = get_weekly_avg()
    table_data = []

    for pillar, target in TARGETS.items():
        current = avg_hours.get(pillar, 0)
        status = "✅ On track" if current >= target else f"⚠ Below target by {target - current:.1f} hrs/day"
        table_data.append([pillar, f"{current:.2f}", f"{target:.2f}", status])

    print(tabulate(table_data, headers=["Pillar", "Avg hrs/day", "Target hrs/day", "Status"], tablefmt="fancy_grid"))

if __name__ == "__main__":
    generate_report()

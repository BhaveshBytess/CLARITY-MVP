from datetime import datetime, timedelta
import sqlite3
import os

from clarity.scripts.goal_tracker import init_db, log_hours, get_all_logs, get_weekly_avg, check_targets

# Step 0: Reset DB for testing
DB_PATH = "clarity/data/clarity.db"
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

init_db()

# Step 1: Insert fake logs for last 6 days
pillars = ["Dev", "DSA", "GATE"]

# Simulated hours for testing
fake_data = {
    "Dev":   [2, 1, 2, 1.5, 0, 2],   # slightly above target
    "DSA":   [0.5, 0, 1, 1, 1, 0.5], # around target
    "GATE":  [0, 0, 0.5, 1, 0.5, 0]  # below target
}

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

for i in range(6):
    date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
    for pillar in pillars:
        hours = fake_data[pillar][i]
        c.execute("INSERT INTO pillar_logs (date, pillar, hours) VALUES (?, ?, ?)",
                  (date, pillar, hours))

conn.commit()
conn.close()

# Step 2: Display all logs
print("\n=== All Logs ===")
for log in get_all_logs():
    print(log)

# Step 3: Show weekly averages
print("\n=== Weekly Averages ===")
print(get_weekly_avg())

# Step 4: Check targets
print("\n=== Target Status ===")
print(check_targets())

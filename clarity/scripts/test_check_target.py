import os
import sqlite3
from datetime import datetime, timedelta
from pprint import pprint

from goal_tracker import init_db, check_targets

DB_PATH = "clarity/data/clarity.db"

# ---------------------------
# Step 1: Reset DB for clean test
# ---------------------------
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
init_db()

# ---------------------------
# Step 2: Insert fake logs for 6 days
# ---------------------------
pillars = ["Dev", "DSA", "GATE"]
fake_data = {
    "Dev":   [2, 1, 2, 1.5, 0, 2],       # Avg ~ 1.58
    "DSA":   [0.5, 0, 1, 1, 1, 0.5],     # Avg ~ 0.83
    "GATE":  [0, 0, 0.5, 1, 0.5, 0]      # Avg ~ 0.33
}

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

for i in range(6):
    date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
    for pillar in pillars:
        hours = fake_data[pillar][i]
        c.execute(
            "INSERT INTO pillar_logs (date, pillar, hours) VALUES (?, ?, ?)",
            (date, pillar, hours)
        )

conn.commit()
conn.close()

# ---------------------------
# Step 3: Get status dictionary
# ---------------------------
status_report = check_targets()

# ---------------------------
# Step 4: Pretty-print result
# ---------------------------
print("\n=== Stage 2 Status Report ===")
pprint(status_report)

# ---------------------------
# Step 5: Inline Sanity Check
# ---------------------------
# Averages are calculated over 7 days, with 6 days of fake data and 1 day of 0 hours.
# Dev: (2+1+2+1.5+0+2) / 7 = 1.21
# DSA: (0.5+0+1+1+1+0.5) / 7 = 0.57
# GATE: (0+0+0.5+1+0.5+0) / 7 = 0.29
expected_avgs = {"Dev": 1.21, "DSA": 0.57, "GATE": 0.29}

for pillar, expected_avg in expected_avgs.items():
    actual_avg = status_report[pillar]["avg"]
    # Allowing a tolerance for floating-point math errors
    if abs(actual_avg - expected_avg) > 0.01:
        raise AssertionError(
            f"❌ Avg mismatch for {pillar}: Expected {expected_avg}, got {actual_avg}"
        )

print("\n✅ Stage 2 Test Passed — All averages match expected values.")

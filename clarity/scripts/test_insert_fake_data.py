# clarity/scripts/test_insert_fake_data.py
import os
import sqlite3
from datetime import datetime, timedelta

from goal_tracker import init_db, DB_PATH

def reset_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    init_db()

def insert_logs_for_scenario(scenario_name, data_map):
    """
    data_map: dict pillar -> list of 7 numbers (hours for each day, 0..6)
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for i in range(7):
        date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        for pillar, hours_list in data_map.items():
            hours = hours_list[i]
            c.execute("INSERT INTO pillar_logs (date, pillar, hours) VALUES (?, ?, ?)",
                      (date, pillar, hours))
    conn.commit()
    conn.close()
    print(f"[+] Inserted scenario '{scenario_name}'")

if __name__ == "__main__":
    reset_db()

    # Scenario A: balanced (should be mostly on-track)
    balanced = {
        "Dev":  [1.5,1.5,1.5,1.5,1.5,1.5,1.5],
        "DSA":  [1.0,1.0,1.0,1.0,1.0,1.0,1.0],
        "GATE": [1.0,1.0,1.0,1.0,1.0,1.0,1.0],
    }
    insert_logs_for_scenario("balanced", balanced)

    # If you want to test other scenarios later, comment out above and run below:
    # Scenario B: DSA lagging
    # dsa_lag = {
    #     "Dev":  [1.5,1.5,1.5,1.5,1.5,1.5,1.5],
    #     "DSA":  [0.2,0.3,0.0,0.5,0.0,0.2,0.3],
    #     "GATE": [1.0,1.0,1.0,1.0,1.0,1.0,1.0],
    # }
    # insert_logs_for_scenario("dsa_lag", dsa_lag)

# clarity/scripts/test_stage6_endtoend.py
import os
from pprint import pprint

from goal_tracker import init_db, DB_PATH
from suggestion_engine import generate_suggestions
from goal_tracker import get_weekly_avg, check_targets

# Helper: use the same fake-data script to prepare DB, or call it programmatically
from test_insert_fake_data import reset_db, insert_logs_for_scenario

def run_test_for_scenario(scenario_name, data_map, expected_top_focus):
    reset_db()
    insert_logs_for_scenario(scenario_name, data_map)
    status = check_targets()
    out = generate_suggestions(status)
    top = out["top_focus"]
    print(f"Scenario: {scenario_name} → top_focus: {top}")
    pprint(out["summary_lines"])
    assert top == expected_top_focus, f"Expected top focus {expected_top_focus}, got {top}"
    print("✅ Test passed.\n")

if __name__ == "__main__":
    # Scenario B: DSA lagging, expect DSA top focus
    dsa_lag = {
        "Dev":  [1.5,1.5,1.5,1.5,1.5,1.5,1.5],
        "DSA":  [0.2,0.3,0.0,0.5,0.0,0.2,0.3],
        "GATE": [1.0,1.0,1.0,1.0,1.0,1.0,1.0],
    }
    run_test_for_scenario("dsa_lag", dsa_lag, expected_top_focus="DSA")

    # Scenario C: GATE worst -> expect GATE top focus
    gate_lag = {
        "Dev":  [1.5,1.0,1.5,1.5,1.5,1.5,1.5],
        "DSA":  [1.0,1.0,1.0,1.0,1.0,1.0,1.0],
        "GATE": [0.0,0.0,0.0,0.0,0.0,0.0,0.0],
    }
    run_test_for_scenario("gate_lag", gate_lag, expected_top_focus="GATE")

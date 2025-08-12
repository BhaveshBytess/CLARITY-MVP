# clarity/scripts/test_suggestion_engine.py

from goal_tracker import check_targets
from suggestion_engine import generate_suggestions

if __name__ == "__main__":
    print("=== Stage 3 Test: Suggestions from Current DB ===\n")

    # 1️⃣ Get status dict from Stage 2
    status_report = check_targets()
    print("📊 Status Report (from DB):")
    for pillar, data in status_report.items():
        print(f"{pillar}: Avg {data['avg']} / Target {data['target']} → {data['status']}")
    print()

    # 2️⃣ Generate suggestions
    suggestions_output = generate_suggestions(status_report)

    # 3️⃣ Show human-friendly summary lines
    print("💡 Suggestions:")
    for line in suggestions_output["summary_lines"]:
        print(line)

    # 4️⃣ Optional: Show structured dict (debug view)
    print("\n🔍 Debug - structured suggestions dict:")
    for s in suggestions_output["suggestions"]:
        print(s)

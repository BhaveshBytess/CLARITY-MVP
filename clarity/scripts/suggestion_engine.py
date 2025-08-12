# clarity/scripts/suggestion_engine.py

from typing import Dict, List, Tuple

# === Configuration: actions mapped to pillars ===
PILLAR_ACTIONS = {
    "Dev": [
        ("Build a tiny feature", 60),   # (task text, recommended minutes)
        ("Fix one open bug or write one unit test", 45),
        ("Write README + docs for current project", 30),
        ("Push one meaningful commit & open a PR", 20),
    ],
    "DSA": [
        ("Solve 1 medium problem (patterns: graphs/trees/greedy)", 60),
        ("Do 2 easy practice problems on a platform (time-box)", 45),
        ("Review one solved problem; write a short note in Obsidian", 30),
        ("Practice 20 min of speed problems (arrays/strings)", 20),
    ],
    "GATE": [
        ("Revise yesterday's topic + solve 5 MCQs", 60),
        ("Do 1 full previous year question on that topic", 45),
        ("Summarize formulae + create 1 flashcard set", 30),
        ("Quick concept check (15 min)", 15),
    ],
}

# Priority thresholds (percentage below target)
PRIORITY_THRESHOLDS = {
    "high": 0.30,   # >=30% below target => HIGH priority
    "medium": 0.15, # >=15% below target => MEDIUM
    "low": 0.0      # <15% below => LOW
}

def _compute_deficit(avg: float, target: float) -> Tuple[float, float]:
    """
    Returns (absolute_deficit, percent_deficit)
    percent_deficit = (target - avg) / target  (0.0..1.0 if below, negative if above)
    """
    abs_def = max(0.0, round(target - avg, 2))
    pct_def = 0.0
    if target > 0:
        pct_def = round((target - avg) / target, 3)
    return abs_def, pct_def

def _pick_action(pillar: str, priority: str) -> Tuple[str, int]:
    """
    Pick a reasonable action for the pillar based on priority.
    Returns (action_text, recommended_minutes)
    """
    actions = PILLAR_ACTIONS.get(pillar, [])
    if not actions:
        return ("Do one focused session for this pillar (30 min).", 30)

    # Strategy: high -> first action; medium -> second; low -> last/third
    if priority == "high":
        return actions[0]
    elif priority == "medium":
        return actions[1] if len(actions) > 1 else actions[0]
    else:
        # pick a short action for "low" deficit
        # prefer the shortest recommended minutes
        return sorted(actions, key=lambda x: x[1])[0]

def generate_suggestions(status_dict: Dict[str, Dict]) -> Dict:
    """
    Input: status_dict like:
      {
        "Dev": {"avg": 1.42, "target": 1.5, "status": "⚠ ..."},
        "DSA": {"avg": 0.67, "target": 1, "status": "⚠ ..."},
        ...
      }
    Output: {
      "top_focus": "DSA",
      "suggestions": [
        {"pillar":"DSA","priority":"high","abs_deficit":0.33,"pct_deficit":0.33,
         "action":"Solve 1 medium problem...","minutes":60},
        ...
      ]
    }
    """
    suggestions = []
    # compute deficits & priority
    for pillar, data in status_dict.items():
        avg = float(data.get("avg", 0.0))
        target = float(data.get("target", 0.0))
        abs_def, pct_def = _compute_deficit(avg, target)

        # Determine priority
        if pct_def >= PRIORITY_THRESHOLDS["high"]:
            priority = "high"
        elif pct_def >= PRIORITY_THRESHOLDS["medium"]:
            priority = "medium"
        else:
            priority = "low"

        action_text, minutes = _pick_action(pillar, priority)
        suggestion = {
            "pillar": pillar,
            "avg": avg,
            "target": target,
            "abs_deficit": round(abs_def, 2),
            "pct_deficit": round(pct_def, 3),
            "priority": priority,
            "action": action_text,
            "minutes": minutes
        }
        suggestions.append(suggestion)

    # Sort suggestions by priority (high -> medium -> low) and pct_deficit desc
    priority_order = {"high": 0, "medium": 1, "low": 2}
    suggestions.sort(key=lambda s: (priority_order[s["priority"]], -s["pct_deficit"]))

    # Top focus is the first in sorted list (if any)
    top_focus = suggestions[0]["pillar"] if suggestions else None

    # Build a plain-text short summary for UI or LinkedIn-friendly lines
    summary_lines = []
    if top_focus:
        top = suggestions[0]
        summary_lines.append(f"🔔 Top focus: {top['pillar']} — {int(top['pct_deficit']*100)}% below target. Suggested: {top['action']} ({top['minutes']} min).")

    for s in suggestions:
        if s["priority"] == "high":
            emoji = "🔥"
        elif s["priority"] == "medium":
            emoji = "⚠"
        else:
            emoji = "✅"

        line = f"{emoji} {s['pillar']}: Avg {s['avg']} / Target {s['target']} → {s['abs_deficit']} hrs deficit. Action: {s['action']} ({s['minutes']}m)."
        summary_lines.append(line)

    return {
        "top_focus": top_focus,
        "suggestions": suggestions,
        "summary_lines": summary_lines
    }

# Small helper for quick CLI testing
if __name__ == "__main__":
    # example fake input
    example_status = {
        "Dev": {"avg": 1.42, "target": 1.5, "status": "⚠ Below target"},
        "DSA": {"avg": 0.67, "target": 1.0, "status": "⚠ Below target"},
        "GATE": {"avg": 0.33, "target": 1.0, "status": "⚠ Below target"}
    }
    out = generate_suggestions(example_status)
    print("\n".join(out["summary_lines"]))

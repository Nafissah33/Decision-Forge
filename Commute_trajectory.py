"""DecisionForge — Scenario A: CampusRoute.

Rule-based campus commute evaluator. No external packages required.
Nafi can import ``evaluate_campus_route`` in the Streamlit app.
All data is illustrative/user-entered; no live transit feeds are used.
"""
from datetime import datetime
from typing import Any


OPTIONS = ("bus", "train", "backup")


def minutes_to_time(value: str) -> int:
    """Parse a 24-hour HH:MM time into minutes after midnight."""
    try:
        parsed = datetime.strptime(value, "%H:%M")
    except (TypeError, ValueError) as exc:
        raise ValueError("Times must use 24-hour HH:MM format, e.g. '09:00'.") from exc
    return parsed.hour * 60 + parsed.minute


def time_from_minutes(value: int) -> str:
    """Format minutes since midnight as HH:MM, including next-day indication."""
    day, clock = divmod(int(value), 1440)
    return f"{clock // 60:02d}:{clock % 60:02d}" + (" (+1 day)" if day else "")


def evaluate_campus_route(data: dict[str, Any]) -> dict[str, Any]:
    """Evaluate bus/train/backup and return explainable results.

    Inputs
    ------
    deadline: "HH:MM" (arrival on campus, not at a stop)
    budget: number >= 0 (one-way maximum in dollars)
    weather: "clear", "rain", or "snow"
    priority: "earliest", "cheapest", or "reliable"
    max_walk_minutes: number >= 0 (maximum TOTAL walking minutes)
    options: dict with keys bus, train, backup. Each has:
        operating: bool
        departure: "HH:MM" (vehicle departs stop/pickup point)
        travel_minutes: number >= 0 (on vehicle)
        walk_before_minutes: number >= 0 (before vehicle departure)
        walk_after_minutes: number >= 0 (after vehicle arrival)
        fare: number >= 0 (one-way)
        reliability: integer from 1 to 5 (user-provided estimate)

    Assumptions: Maya can start early enough to complete pre-departure walking;
    walking is acceptable when total walk <= limit and weather is not "snow".
    For rainy weather the same walk limit is used (simplified rule).
    Arrival must be STRICTLY before deadline, as required by the project.
    Same-day journeys only: departure + journey + walking must not pass midnight.
    "backup" is treated as an on-demand car ride, with no automatic availability.
    """
    if not isinstance(data, dict):
        raise ValueError("Input must be a dictionary.")
    deadline = minutes_to_time(data.get("deadline"))
    budget = _nonnegative(data.get("budget"), "budget")
    max_walk = _nonnegative(data.get("max_walk_minutes"), "max_walk_minutes")
    weather = data.get("weather")
    priority = data.get("priority")
    if weather not in ("clear", "rain", "snow"):
        raise ValueError("weather must be 'clear', 'rain', or 'snow'.")
    if priority not in ("earliest", "cheapest", "reliable"):
        raise ValueError("priority must be 'earliest', 'cheapest', or 'reliable'.")
    options = data.get("options")
    if not isinstance(options, dict) or set(options) != set(OPTIONS):
        raise ValueError("options must contain exactly bus, train, and backup.")

    results = {}
    for name in OPTIONS:
        o = options[name]
        if not isinstance(o, dict) or type(o.get("operating")) is not bool:
            raise ValueError(f"{name}.operating must be True or False.")
        departure = minutes_to_time(o.get("departure"))
        fare = _nonnegative(o.get("fare"), f"{name}.fare")
        travel = _nonnegative(o.get("travel_minutes"), f"{name}.travel_minutes")
        before = _nonnegative(o.get("walk_before_minutes"), f"{name}.walk_before_minutes")
        after = _nonnegative(o.get("walk_after_minutes"), f"{name}.walk_after_minutes")
        reliable = o.get("reliability")
        if type(reliable) is not int or not (1 <= reliable <= 5):
            raise ValueError(f"{name}.reliability must be an integer from 1 to 5.")
        arrival = departure + travel + after
        if arrival >= 1440:
            raise ValueError(f"{name}: arrival after midnight is not supported.")
        if departure < before:
            raise ValueError(f"{name}: walking before departure would start before midnight.")
        walking_total = before + after

        propositions = {
            "S": o["operating"],
            "F": fare <= budget,
            "D": arrival < deadline,
            "W": walking_total <= max_walk and weather != "snow",
        }
        eligible = all(propositions.values())
        reason = {
            "S": "service is operating" if propositions["S"] else "service is not operating",
            "F": f"fare ${fare:.2f} is within budget ${budget:.2f}" if propositions["F"] else f"fare ${fare:.2f} exceeds budget ${budget:.2f}",
            "D": f"campus arrival {time_from_minutes(arrival)} is before deadline {time_from_minutes(deadline)}" if propositions["D"] else f"campus arrival {time_from_minutes(arrival)} is not before deadline {time_from_minutes(deadline)}",
            "W": f"walking ({walking_total:g} min) is acceptable for {weather} weather" if propositions["W"] else f"walking ({walking_total:g} min) is not acceptable for {weather} weather / {max_walk:g}-minute limit",
        }
        first_failure = next((key for key, passed in propositions.items() if not passed), None)
        results[name] = {
            "eligible": eligible,
            "propositions": propositions,
            "expression": "S ∧ F ∧ D ∧ W",
            "fare": fare,
            "departure": time_from_minutes(departure),
            "campus_arrival": time_from_minutes(arrival),
            "arrival_minutes": arrival,
            "walk_total_minutes": walking_total,
            "reliability": reliable,
            "explanation": "; ".join(reason.values()),
            "failed_conditions": [reason[k] for k, ok in propositions.items() if not ok],
            "decision_path": [
                {"question": label, "passed": propositions[key]}
                for key, label in (("S", "Operating?"), ("F", "Affordable?"), ("D", "Before deadline?"), ("W", "Walking acceptable?"))
                if first_failure is None or ("S", "F", "D", "W").index(key) <= ("S", "F", "D", "W").index(first_failure)
            ],
        }

    eligible_names = [n for n in OPTIONS if results[n]["eligible"]]
    if priority == "cheapest":
        key = lambda n: (results[n]["fare"], results[n]["arrival_minutes"], -results[n]["reliability"])
    elif priority == "earliest":
        key = lambda n: (results[n]["arrival_minutes"], results[n]["fare"], -results[n]["reliability"])
    else:
        key = lambda n: (-results[n]["reliability"], results[n]["arrival_minutes"], results[n]["fare"])
    ranked = sorted(eligible_names, key=key)
    best = ranked[0] if ranked else None
    if best:
        summary = (f"Recommend {best}: it meets all required conditions. "
                   f"Estimated campus arrival {results[best]['campus_arrival']}, "
                   f"fare ${results[best]['fare']:.2f}, reliability {results[best]['reliability']}/5. "
                   f"Ranking priority: {priority}.")
    else:
        summary = "No transportation option meets all required conditions. Review the failed checks for each option."
    edges = [("Maya", "needs to reach", "Campus"), ("Maya", "has budget", f"${budget:.2f}"),
             ("Maya", "has deadline", time_from_minutes(deadline)), ("Weather", "condition", weather)]
    for name in OPTIONS:
        edges.extend([("Maya", "can consider", name.title()),
                      (name.title(), "travels to", "Campus"),
                      (name.title(), "has fare", f"${results[name]['fare']:.2f}"),
                      (name.title(), "arrives at", results[name]["campus_arrival"])])
    adjacency = {}
    for src, rel, dst in edges:
        adjacency.setdefault(src, []).append({"relationship": rel, "target": dst})
    return {"recommended": best, "ranked_eligible": ranked, "summary": summary,
            "options": results, "knowledge_graph_edges": edges, "adjacency_list": adjacency,
            "rule": "Eligible = S ∧ F ∧ D ∧ W", "priority": priority}


def _nonnegative(value: Any, name: str) -> float:
    if type(value) not in (int, float) or not (0 <= value < float("inf")):
        raise ValueError(f"{name} must be a nonnegative finite number.")
    return float(value)


if __name__ == "__main__":
    example = {
        "deadline": "09:00", "budget": 10, "weather": "clear",
        "priority": "earliest", "max_walk_minutes": 20,
        "options": {
            "bus": {"operating": True, "departure": "08:00", "travel_minutes": 35,
                    "walk_before_minutes": 5, "walk_after_minutes": 15, "fare": 3, "reliability": 3},
            "train": {"operating": True, "departure": "08:00", "travel_minutes": 25,
                      "walk_before_minutes": 5, "walk_after_minutes": 5, "fare": 6, "reliability": 5},
            "backup": {"operating": True, "departure": "08:10", "travel_minutes": 25,
                       "walk_before_minutes": 0, "walk_after_minutes": 5, "fare": 12, "reliability": 4},
        },
    }
    result = evaluate_campus_route(example)
    print(result["summary"])
    for name, option in result["options"].items():
        print(f"{name.title()}: eligible={option['eligible']}, "
              f"conditions={option['propositions']}; {option['explanation']}")


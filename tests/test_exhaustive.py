"""Measured verification: the engines are compared against an independent re-statement of the
rules over many generated inputs. This checks the code against the written rules; it cannot
check that the rules themselves are the right ones."""
import random
from itertools import product

from logic.commute_trajectory import OPTIONS, evaluate_campus_route
from logic.login import evaluate_login, get_truth_table

N_RANDOM = 3000


def hhmm(m):
    return f"{m // 60:02d}:{m % 60:02d}"


def random_case(rng):
    options = {}
    for name in OPTIONS:
        options[name] = {
            "operating": rng.random() < 0.8,
            "departure": hhmm(rng.randint(30, 600)),
            "travel_minutes": rng.randint(0, 120),
            "walk_before_minutes": rng.randint(0, 20),
            "walk_after_minutes": rng.randint(0, 25),
            "fare": rng.choice([0, 1.5, 3, 6, 10, 12, 20]),
            "reliability": rng.randint(1, 5),
        }
    return {
        "deadline": hhmm(rng.randint(400, 800)), "budget": rng.choice([0, 3, 6, 10, 15]),
        "weather": rng.choice(["clear", "rain", "snow"]),
        "priority": rng.choice(["earliest", "cheapest", "reliable"]),
        "max_walk_minutes": rng.choice([0, 5, 10, 20, 30]), "options": options,
    }


def oracle(case):
    """Independent statement of: Eligible = S ∧ F ∧ D ∧ W, then rank by priority."""
    dl = int(case["deadline"][:2]) * 60 + int(case["deadline"][3:])
    elig, info = [], {}
    for n, o in case["options"].items():
        dep = int(o["departure"][:2]) * 60 + int(o["departure"][3:])
        arrive = dep + o["travel_minutes"] + o["walk_after_minutes"]
        walk = o["walk_before_minutes"] + o["walk_after_minutes"]
        ok = (o["operating"] and o["fare"] <= case["budget"] and arrive < dl
              and walk <= case["max_walk_minutes"] and case["weather"] != "snow")
        info[n] = (o["fare"], arrive, -o["reliability"])
        if ok:
            elig.append(n)
    keyfn = {"earliest": lambda n: (info[n][1], info[n][0], info[n][2]),
             "cheapest": lambda n: (info[n][0], info[n][1], info[n][2]),
             "reliable": lambda n: (info[n][2], info[n][1], info[n][0])}[case["priority"]]
    ranked = sorted(elig, key=keyfn)
    return set(elig), (ranked[0] if ranked else None)


def test_commute_engine_matches_independent_oracle():
    rng, checked, skipped = random.Random(208), 0, 0
    for _ in range(N_RANDOM):
        case = random_case(rng)
        try:
            result = evaluate_campus_route(case)
        except ValueError:            # e.g. journey passes midnight: rejected by design
            skipped += 1
            continue
        elig, best = oracle(case)
        assert {n for n, o in result["options"].items() if o["eligible"]} == elig
        assert result["recommended"] == best
        checked += 1
    assert checked > 0.9 * N_RANDOM
    print(f"\ncommute: {checked} generated cases matched the oracle ({skipped} rejected as invalid)")


def test_login_all_eight_combinations():
    for p, v, l in product([True, False], repeat=3):
        granted = evaluate_login(p, v, l)["result"] == "Access Granted"
        assert granted == (p and v and l)
    assert len(get_truth_table()) == 8

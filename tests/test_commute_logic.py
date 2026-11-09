"""Commute rule engine: normal, boundary, and changed-input cases (Eligible = S ∧ F ∧ D ∧ W)."""
import copy
import itertools

import pytest

from logic.commute_trajectory import evaluate_campus_route

BASE = {
    "deadline": "09:00", "budget": 10, "weather": "clear", "priority": "earliest",
    "max_walk_minutes": 20,
    "options": {
        "bus": {"operating": True, "departure": "08:00", "travel_minutes": 35,
                "walk_before_minutes": 5, "walk_after_minutes": 15, "fare": 3, "reliability": 3},
        "train": {"operating": True, "departure": "08:00", "travel_minutes": 25,
                  "walk_before_minutes": 5, "walk_after_minutes": 5, "fare": 6, "reliability": 5},
        "backup": {"operating": True, "departure": "08:10", "travel_minutes": 25,
                   "walk_before_minutes": 0, "walk_after_minutes": 5, "fare": 12, "reliability": 4},
    },
}


def run(**changes):
    data = copy.deepcopy(BASE)
    for key, value in changes.items():
        if key in data["options"]:
            data["options"][key].update(value)
        else:
            data[key] = value
    return evaluate_campus_route(data)


# ---- normal cases ----
def test_default_example_recommends_train():
    r = run()
    assert r["recommended"] == "train"
    assert r["ranked_eligible"] == ["train", "bus"]
    assert not r["options"]["backup"]["propositions"]["F"]   # $12 > $10


def test_eligibility_is_exactly_the_conjunction():
    for name, o in run()["options"].items():
        assert o["eligible"] == all(o["propositions"].values())


# ---- boundary cases ----
def test_arrival_exactly_at_deadline_is_not_eligible():
    # train: 08:00 + 25 + 5 = 08:30 -> set deadline to 08:30 (strictly before required)
    r = run(deadline="08:30")
    assert not r["options"]["train"]["propositions"]["D"]
    assert run(deadline="08:31")["options"]["train"]["propositions"]["D"]


def test_fare_exactly_equal_to_budget_is_eligible():
    assert run(budget=6)["options"]["train"]["propositions"]["F"]
    assert not run(budget=5.99)["options"]["train"]["propositions"]["F"]


def test_walking_exactly_at_limit_is_ok_but_snow_always_fails():
    assert run(max_walk_minutes=10)["options"]["train"]["propositions"]["W"]   # 5 + 5
    assert not run(max_walk_minutes=9)["options"]["train"]["propositions"]["W"]
    snow = run(weather="snow")
    assert all(not o["propositions"]["W"] for o in snow["options"].values())
    assert snow["recommended"] is None


@pytest.mark.parametrize("bad", [{"deadline": "9am"}, {"budget": -1}, {"weather": "fog"},
                                 {"priority": "fastest"}])
def test_invalid_inputs_are_rejected(bad):
    with pytest.raises(ValueError):
        run(**bad)


# ---- changing one input changes the outcome ----
def test_service_outage_changes_recommendation():
    assert run()["recommended"] == "train"
    assert run(train={"operating": False})["recommended"] == "bus"


def test_priority_changes_recommendation():
    assert run(priority="earliest")["recommended"] == "train"
    assert run(priority="cheapest")["recommended"] == "bus"


def test_lower_budget_changes_recommendation():
    assert run(budget=4)["recommended"] == "bus"
    assert run(budget=2)["recommended"] is None


# ---- knowledge graph / adjacency consistency ----
def test_adjacency_list_matches_edges():
    r = run()
    from_adj = sorted((s, c["relationship"], c["target"])
                      for s, cs in r["adjacency_list"].items() for c in cs)
    assert from_adj == sorted(map(tuple, r["knowledge_graph_edges"]))


def test_explanation_uses_entered_values():
    assert "$6.00" in run()["options"]["train"]["explanation"]
    assert "$7.00" in run(train={"fare": 7})["options"]["train"]["explanation"]

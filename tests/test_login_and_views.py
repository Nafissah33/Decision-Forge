"""Login rule (AccessGranted = P ∧ V ∧ L), expression trees, and De Morgan equivalence."""
from itertools import product

import views
from logic.login import evaluate_login, get_knowledge_graph, get_tree_traversals, get_truth_table


def test_access_granted_only_when_all_three_true():
    for p, v, l in product([True, False], repeat=3):
        granted = evaluate_login(p, v, l)["result"] == "Access Granted"
        assert granted == (p and v and l)


def test_truth_table_has_8_rows_and_one_true():
    rows = get_truth_table()
    assert len(rows) == 8
    assert [r for r in rows if r["AccessGranted"]] == [{"P": True, "V": True, "L": True, "AccessGranted": True}]


def test_changing_one_input_changes_outcome_and_guidance():
    ok = evaluate_login(True, True, True)
    locked = evaluate_login(True, True, False)
    assert ok["result"] != locked["result"]
    assert "support" in locked["explanation"].lower()
    assert "recovery" in evaluate_login(False, True, True)["explanation"].lower()


def test_login_traversals_match_expression():
    t = get_tree_traversals()                      # tree for (P AND V) AND L
    assert t["preorder"] == ["AND", "AND", "P", "V", "L"]
    assert t["inorder"] == ["P", "AND", "V", "AND", "L"]
    assert t["postorder"] == ["P", "V", "AND", "L", "AND"]


def test_views_traversals_for_four_variables():
    root = views.and_tree(["S", "F", "D", "W"])    # ((S ∧ F) ∧ D) ∧ W
    assert views.preorder(root) == ["∧", "∧", "∧", "S", "F", "D", "W"]
    assert views.inorder(root) == ["S", "∧", "F", "∧", "D", "∧", "W"]
    assert views.postorder(root) == ["S", "F", "∧", "D", "∧", "W", "∧"]


def test_login_knowledge_graph_has_labeled_edges_and_adjacency():
    g = get_knowledge_graph()
    assert all(e["relationship"] for e in g["edges"])
    assert sum(len(v) for v in g["adjacency_list"].values()) == len(g["edges"])


def test_de_morgan_equivalence_holds_for_all_rows():
    for n in (3, 4):
        for combo in product([True, False], repeat=n):
            assert (not all(combo)) == any(not x for x in combo)


def test_backend_truth_table_rows_are_consistent_with_rule():
    for r in get_truth_table():
        assert r["AccessGranted"] == (r["P"] and r["V"] and r["L"])

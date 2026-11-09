"""Scenario D screen: SecureSteps login simulator (fictional inputs only).

All logic comes from login.py (Maya's backend); this file only renders it.
"""
import streamlit as st

import views
from logic.login import (evaluate_login, get_knowledge_graph, get_tree_traversals,
                   get_truth_table, tree)

VARS = ["P", "V", "L"]


def _to_view_node(n):
    """Convert login.py's Node (.value, 'AND') to views.Node (.label, '∧')."""
    if n is None:
        return None
    label = "∧" if n.value == "AND" else n.value
    return views.Node(label, _to_view_node(n.left), _to_view_node(n.right))


def show():
    st.header("🔐 Login System")
    st.info("**Learning simulator.** These are fictional toggles. This app never asks for "
            "or stores real passwords, verification codes, or account details.")

    c1, c2, c3 = st.columns(3)
    p = c1.toggle("P: password check passed", True)
    v = c2.toggle("V: second verification passed", True)
    l = c3.toggle("L: account is not locked", True)

    # Keep the result in session state so it survives toggling/other reruns.
    if st.button("Evaluate", type="primary"):
        st.session_state.login_result = {"inputs": (p, v, l), **evaluate_login(p, v, l)}
    res = st.session_state.get("login_result")
    if not res:
        return

    p, v, l = res["inputs"]
    granted = res["result"] == "Access Granted"
    (st.success if granted else st.error)(
        f"AccessGranted = P ∧ V ∧ L = {p} ∧ {v} ∧ {l} → **{res['result']}**")
    st.write(res["explanation"])
    failed = [name for name, ok in (("password check", p), ("second verification", v),
                                   ("not-locked check", l)) if not ok]
    if failed:
        st.write("Failed checks: " + ", ".join(failed))

    summary = (f"DecisionForge - Login simulator summary (fictional inputs)\n\n"
               f"P={p}, V={v}, L={l}\nAccessGranted = P ∧ V ∧ L = {granted}\n"
               f"{res['explanation']}\n")
    st.download_button("Download summary", summary, "login_summary.txt")

    t1, t2, t3, t4, t5 = st.tabs(["Truth table", "Expression tree", "Decision tree", "Knowledge graph", "Equivalence"])
    with t1:
        views.show_truth_table(VARS, "AccessGranted", {"P": p, "V": v, "L": l},
                               backend_rows=get_truth_table())
    with t2:
        st.graphviz_chart(views.tree_dot(_to_view_node(tree)))
        t = get_tree_traversals()
        a, b, c = st.columns(3)
        a.markdown("**Preorder**\n\n" + " ".join(t["preorder"]))
        b.markdown("**Inorder**\n\n" + " ".join(t["inorder"]))
        c.markdown("**Postorder**\n\n" + " ".join(t["postorder"]))
    with t3:
        # Same order as login.decision_tree: password -> verification -> lock.
        path = [{"question": "Password check passed?", "passed": p}]
        if p:
            path.append({"question": "Second verification passed?", "passed": v})
        if p and v:
            path.append({"question": "Account not locked?", "passed": l})
        st.graphviz_chart(views.decision_tree_dot(path, res["explanation"]))
    with t4:
        g = get_knowledge_graph()
        edges = [(e["source"], e["relationship"], e["target"]) for e in g["edges"]]
        st.graphviz_chart(views.knowledge_graph_dot(edges))
        views.show_adjacency(edges)
    with t5:
        views.show_equivalence(VARS, "AccessGranted")

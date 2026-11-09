"""Shared display helpers for DecisionForge: truth tables, expression trees,
decision trees, and knowledge graphs. Used by both scenario screens."""
from itertools import product

import pandas as pd
import streamlit as st


# ---------- expression tree ----------
class Node:
    def __init__(self, label, left=None, right=None):
        self.label, self.left, self.right = label, left, right


def and_tree(variables):
    """Left-nested tree for v1 ∧ v2 ∧ ... (e.g. P ∧ V ∧ L)."""
    tree = Node(variables[0])
    for v in variables[1:]:
        tree = Node("∧", tree, Node(v))
    return tree


def preorder(n):
    return [] if n is None else [n.label] + preorder(n.left) + preorder(n.right)


def inorder(n):
    return [] if n is None else inorder(n.left) + [n.label] + inorder(n.right)


def postorder(n):
    return [] if n is None else postorder(n.left) + postorder(n.right) + [n.label]


def tree_dot(root):
    lines, counter = ["digraph {", "node [shape=circle]"], [0]

    def walk(n):
        me = counter[0]
        counter[0] += 1
        lines.append(f'n{me} [label="{n.label}"]')
        for child in (n.left, n.right):
            if child is not None:
                lines.append(f"n{me} -> n{walk(child)}")
        return me

    walk(root)
    return "\n".join(lines + ["}"])


def show_expression_tree(variables, symbol="∧"):
    root = and_tree(variables)
    st.graphviz_chart(tree_dot(root))
    c1, c2, c3 = st.columns(3)
    c1.markdown("**Preorder**\n\n" + " ".join(preorder(root)))
    c2.markdown("**Inorder**\n\n" + " ".join(inorder(root)))
    c3.markdown("**Postorder**\n\n" + " ".join(postorder(root)))


# ---------- truth table ----------
def show_truth_table(variables, rule_name, current=None, backend_rows=None):
    """All T/F combinations for an AND of `variables`. Highlights the row
    matching `current` (dict var -> bool) if given. If `backend_rows` (a list of
    dicts with the variables plus `rule_name` booleans) is given, the output column
    is taken from the backend instead of being recomputed here."""
    backend = {tuple(r[v] for v in variables): r[rule_name] for r in (backend_rows or [])}
    rows = []
    for combo in product([True, False], repeat=len(variables)):
        row = {v: "T" if x else "F" for v, x in zip(variables, combo)}
        out = backend.get(combo, all(combo))
        row[rule_name] = "T" if out else "F"
        row["Why"] = ("all conditions true" if all(combo) else
                      "fails: " + ", ".join(v for v, x in zip(variables, combo) if not x))
        row["Your input"] = "◀" if current and tuple(current[v] for v in variables) == combo else ""
        rows.append(row)
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")


# ---------- decision tree / knowledge graph ----------
def decision_tree_dot(path, outcome):
    """path: list of {"question", "passed"}; stops at the first failure."""
    lines = ["digraph {", "rankdir=LR", "node [shape=box, style=rounded]"]
    for i, step in enumerate(path):
        lines.append(f'q{i} [label="{step["question"]}"]')
        if i:
            lines.append(f'q{i-1} -> q{i} [label="yes"]')
    last = len(path) - 1
    failed = path and not path[-1]["passed"]
    lines.append(f'out [label="{outcome}", shape=box, style="filled", '
                 f'fillcolor="{"#f8d7da" if failed else "#d4edda"}"]')
    if path:
        lines.append(f'q{last} -> out [label="{"no" if failed else "yes"}"]')
    return "\n".join(lines + ["}"])


def knowledge_graph_dot(edges):
    lines = ["digraph {", "node [shape=ellipse]"]
    lines += [f'"{a}" -> "{b}" [label="{rel}"]' for a, rel, b in edges]
    return "\n".join(lines + ["}"])


# ---------- adjacency list ----------
def show_adjacency(edges):
    """Readable adjacency list for a knowledge graph given (source, relation, target) edges."""
    adj = {}
    for src, rel, dst in edges:
        adj.setdefault(src, []).append(f"{rel} → {dst}")
        adj.setdefault(dst, [])
    rows = [{"Node": n, "Outgoing edges": "; ".join(out) if out else "(none)"}
            for n, out in adj.items()]
    st.markdown(f"**Adjacency list** ({len(adj)} nodes, {len(edges)} labeled edges)")
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")


# ---------- logical equivalence (De Morgan) ----------
def show_equivalence(variables, rule_name):
    """Demonstrate  ¬(v1 ∧ v2 ∧ …)  ≡  ¬v1 ∨ ¬v2 ∨ …  with a truth table."""
    left = "¬(" + " ∧ ".join(variables) + ")"
    right = " ∨ ".join(f"¬{v}" for v in variables)
    rows, all_equal = [], True
    for combo in product([True, False], repeat=len(variables)):
        lhs = not all(combo)
        rhs = any(not x for x in combo)
        all_equal &= lhs == rhs
        row = {v: "T" if x else "F" for v, x in zip(variables, combo)}
        row[left], row[right] = "T" if lhs else "F", "T" if rhs else "F"
        row["Same?"] = "✓" if lhs == rhs else "✗"
        rows.append(row)
    st.markdown(f"**De Morgan's law applied to {rule_name}**: `{left}  ≡  {right}`")
    st.write(f"{rule_name} is denied exactly when at least one condition fails. "
             "Both forms have identical columns in every row, so they are logically equivalent.")
    st.dataframe(pd.DataFrame(rows), hide_index=True, width="stretch")
    (st.success if all_equal else st.error)(
        "Equivalent in all rows." if all_equal else "Not equivalent: check the rule.")
    return all_equal

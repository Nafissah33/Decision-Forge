"""CampusRoute: decision tree, knowledge graph, and adjacency-list verification.

Run in the root of the team's Decision-Forge folder:
    python campus_route_diagrams.py

Uses the EXISTING evaluator (commute_trajectory.py / Commute_trajectory.py /
campus_route.py). Does not modify the team's Python files.
Creates .dot diagrams and, if Graphviz 'dot' is installed, .svg and .png images.
"""
from __future__ import annotations

from collections import Counter
from importlib import import_module
from pathlib import Path
import json
import shutil
import subprocess

OUTPUT = Path(__file__).resolve().parent / "campusroute_diagrams"
OPTION_NAMES = ("bus", "train", "backup")
CONDITIONS = (
    ("S", "Service operating?"),
    ("F", "Fare within budget?"),
    ("D", "Arrives before deadline?"),
    ("W", "Walking acceptable?"),
)


def get_evaluator():
    """Support BOTH names seen in the team's two GitHub repositories."""
    for module_name in ("commute_trajectory", "Commute_trajectory", "campus_route"):
        try:
            module = import_module(module_name)
        except ModuleNotFoundError as error:
            if error.name == module_name:
                continue
            raise
        evaluator = getattr(module, "evaluate_campus_route", None)
        if callable(evaluator):
            return evaluator, module_name
    raise ImportError("Place this script beside commute_trajectory.py, Commute_trajectory.py, or campus_route.py with evaluate_campus_route().")


def example_input():
    """Same fictional example used in Nia's earlier local CampusRoute tests."""
    return {
        "deadline": "09:00", "budget": 10, "weather": "clear",
        "priority": "earliest", "max_walk_minutes": 20,
        "options": {
            "bus": {"operating": True, "departure": "08:00", "travel_minutes": 35,
                    "walk_before_minutes": 5, "walk_after_minutes": 15,
                    "fare": 3, "reliability": 3},
            "train": {"operating": True, "departure": "08:00", "travel_minutes": 25,
                      "walk_before_minutes": 5, "walk_after_minutes": 5,
                      "fare": 6, "reliability": 5},
            "backup": {"operating": True, "departure": "08:10", "travel_minutes": 25,
                       "walk_before_minutes": 0, "walk_after_minutes": 5,
                       "fare": 12, "reliability": 4},
        },
    }


def quote(value):
    """Escape a string safely for Graphviz DOT quoted values."""
    return json.dumps(str(value), ensure_ascii=False)


def validate_graph(result):
    """Verify the exact directed labeled graph edges match the adjacency representation."""
    edges = result["knowledge_graph_edges"]
    adjacency = result["adjacency_list"]
    from_adjacency = [
        (source, item["relationship"], item["target"])
        for source, connections in adjacency.items()
        for item in connections
    ]
    assert Counter(map(tuple, edges)) == Counter(map(tuple, from_adjacency)), (
        "Knowledge-graph edges and adjacency list do not match."
    )
    assert len(edges) == len(from_adjacency), "Adjacency list edge count differs."
    expected = {"Maya", "Campus", "Bus", "Train", "Backup", "Weather"}
    all_nodes = {node for a, _, b in edges for node in (a, b)}
    assert expected <= all_nodes, f"Missing required graph entities: {expected - all_nodes}"
    assert len(result["options"]) == 3, "Expected all three transport options."
    for name in OPTION_NAMES:
        option = result["options"][name]
        assert option["eligible"] == all(option["propositions"].values()), name
    expected_order = sorted(adjacency)
    assert len(expected_order) > 0
    return len(edges), len(all_nodes)


def make_decision_tree(result):
    """Show ordered decision checks, failed branches and final ranking."""
    lines = [
        "digraph CampusRouteDecision {",
        'graph [rankdir=LR, bgcolor="white", pad="0.28", nodesep="0.23", ranksep="0.55", fontname="Arial", label="CampusRoute | Decision tree — illustrative input", labelloc=t, fontsize=20, fontcolor="#18324B"];',
        'node [fontname="Arial", fontsize=10, shape=box, style="rounded,filled", fillcolor="#EFF4FA", color="#9DB4CC", fontcolor="#18324B", margin="0.15,0.12"];',
        'edge [fontname="Arial", fontsize=9, color="#74869B", arrowsize=0.7];',
        'start [shape=oval, label="Evaluate each transport option", fillcolor="#DBEAFE"];',
        'rank [shape=box, label="Rank eligible options\\nPriority: '+str(result["priority"])+ '", fillcolor="#DBEAFE"];',
    ]
    rec = result["recommended"]
    rec_label = "No eligible option" if rec is None else f"Recommend: {rec.title()}"
    lines.append(f'final [shape=oval, label={quote(rec_label)}, fillcolor={quote("#D3F4DF" if rec else "#FFE4E2")}, color="#4B8260"];')
    lines.append('rank -> final [label="choose best"];')
    for name in OPTION_NAMES:
        option = result["options"][name]
        title = "Uber (backup)" if name == "backup" else name.title()
        lines.append(f'{name}_start [shape=oval, label={quote(title)}, fillcolor="#F1F5F9"];')
        lines.append(f'start -> {name}_start;')
        first_failed = next((symbol for symbol, _ in CONDITIONS if not option["propositions"][symbol]), None)
        for index, (symbol, label) in enumerate(CONDITIONS):
            if first_failed is not None and index > [c[0] for c in CONDITIONS].index(first_failed):
                break  # A decision path stops after its first failed requirement.
            node = f"{name}_{symbol}"
            passed = option["propositions"][symbol]
            lines.append(f'{node} [shape=diamond, label={quote(label)}, fillcolor={quote("#E5F5EA" if passed else "#FCE8E6")}, color={quote("#5E9E73" if passed else "#CB736B")}];')
            if index == 0:
                lines.append(f'{name}_start -> {node};')
            if first_failed is None or first_failed == symbol or CONDITIONS.index((symbol, label)) < [c[0] for c in CONDITIONS].index(first_failed):
                if passed:
                    next_id = f'{name}_{CONDITIONS[index+1][0]}' if index < len(CONDITIONS) - 1 else f'{name}_eligible'
                    lines.append(f'{node} -> {next_id} [label="Yes", color="#4F9567"];')
                else:
                    lines.append(f'{node} -> {name}_reject [label="No", color="#C96B62"];')
        if option["eligible"]:
            lines.append(f'{name}_eligible [label="ELIGIBLE\\n{option["campus_arrival"]} | ${option["fare"]:.2f}", fillcolor="#D3F4DF", color="#5E9E73"];')
            lines.append(f'{name}_eligible -> rank [label="qualifies"];')
        else:
            lines.append(f'{name}_reject [label="NOT ELIGIBLE\\nFails {first_failed}", fillcolor="#FCE8E6", color="#CB736B"];')
    lines.append("}")
    return "\n".join(lines) + "\n"


def make_knowledge_graph(result):
    """Draw every relationship from the evaluator's actual knowledge_graph_edges."""
    edges = result["knowledge_graph_edges"]
    lines = [
        "digraph CampusRouteKnowledge {",
        'graph [rankdir=LR, bgcolor="white", pad="0.32", nodesep="0.4", ranksep="1.05", fontname="Arial", label="CampusRoute | Knowledge graph — illustrative input", labelloc=t, fontsize=20, fontcolor="#18324B"];',
        'node [fontname="Arial", fontsize=11, shape=box, style="rounded,filled", fillcolor="#F0F5FB", color="#A2B4C7", fontcolor="#18324B"];',
        'edge [fontname="Arial", fontsize=9, color="#8C99AA", fontcolor="#506172", arrowsize=0.7];',
    ]
    seen = set()
    for source, relationship, target in edges:
        for node in (source, target):
            if node in seen:
                continue
            seen.add(node)
            fill = "#DBEAFE" if node == "Maya" else "#D3F4DF" if node in ("Bus", "Train", "Backup", "Campus") else "#F6F7FA"
            label = "Uber (backup)" if node == "Backup" else node
            lines.append(f'{quote(node)} [label={quote(label)}, fillcolor={quote(fill)}];')
        lines.append(f'{quote(source)} -> {quote(target)} [label={quote(relationship)}];')
    lines.append("}")
    return "\n".join(lines) + "\n"


def adjacency_text(result, edge_count, node_count):
    lines = [
        "CAMPUSROUTE — VERIFIED ADJACENCY LIST",
        "A directed relationship 'A --label--> B' is a connection FROM A TO B.",
        "Only nodes with outgoing connections are listed as headings.",
        f"Verified: {edge_count} labeled edges, {node_count} unique nodes.", "",
    ]
    for source, connections in result["adjacency_list"].items():
        lines.append(f"{source}:")
        for item in connections:
            lines.append(f'  --{item["relationship"]}--> {item["target"]}')
        lines.append("")
    lines.append("PASS: adjacency entries exactly match the knowledge-graph edges (including duplicates).")
    return "\n".join(lines) + "\n"


def run(data=None, output_dir=OUTPUT):
    evaluate, module_name = get_evaluator()
    result = evaluate(example_input() if data is None else data)
    edge_count, node_count = validate_graph(result)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    files = {
        "campusroute_decision_tree.dot": make_decision_tree(result),
        "campusroute_knowledge_graph.dot": make_knowledge_graph(result),
        "campusroute_adjacency_verified.txt": adjacency_text(result, edge_count, node_count),
        "campusroute_results.json": json.dumps(result, ensure_ascii=False, indent=2),
    }
    for name, content in files.items():
        (output_dir / name).write_text(content, encoding="utf-8")
    rendered = []
    if shutil.which("dot"):
        for stem in ("campusroute_decision_tree", "campusroute_knowledge_graph"):
            for fmt in ("svg", "png"):
                subprocess.run(["dot", f"-T{fmt}", str(output_dir / (stem + ".dot")), "-o", str(output_dir / (stem + "." + fmt))], check=True)
                rendered.append(stem + "." + fmt)
    print(f"Using evaluator: {module_name}.py")
    print("Recommendation:", result["recommended"] or "None")
    print(f"PASS: Knowledge graph and adjacency list match ({edge_count} edges, {node_count} nodes).")
    print(f"Files saved to: {output_dir}")
    if rendered:
        print("Rendered diagram files:", ", ".join(rendered))
    else:
        print("Graphviz dot not installed: .dot diagram files are ready; SVG and PNG files are included in the download package.")
    return result


if __name__ == "__main__":
    run()

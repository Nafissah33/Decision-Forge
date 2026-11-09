
# Test importing Scenario D functions

from logic.login import (
    evaluate_login,
    get_truth_table,
    get_tree_traversals,
    get_knowledge_graph
)

print("Login:", evaluate_login(True, True, True))

print("Truth table rows:", len(get_truth_table()))

print("Tree traversals:", get_tree_traversals())

print("Knowledge graph nodes:",
      len(get_knowledge_graph()["nodes"]))

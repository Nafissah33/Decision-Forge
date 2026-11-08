
# Scenario D - SecureSteps Login Simulator
# Uses fictional login conditions only.


# STEP 1 - LOGIN LOGIC

def check_login(password, verification, not_locked):
    if password and verification and not_locked:
        return "Access Granted"
    else:
        return "Access Denied"




# STEP 2 - TRUTH TABLE

def generate_truth_table():
    print("\nP     V     L     Access Granted")

    for p in [True, False]:
        for v in [True, False]:
            for l in [True, False]:
                result = p and v and l
                print(p, v, l, result)





# STEP 3 - EXPRESSION TREE

class Node:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right


# Build the tree for (P AND V) AND L
tree = Node(
    "AND",
    Node("AND", Node("P"), Node("V")),
    Node("L")
)


# Preorder: Root, Left, Right
def preorder(node):
    if node:
        print(node.value, end=" ")
        preorder(node.left)
        preorder(node.right)


# Inorder: Left, Root, Right
def inorder(node):
    if node:
        if node.left or node.right:
            print("(", end="")

        inorder(node.left)
        print(node.value, end=" ")
        inorder(node.right)

        if node.left or node.right:
            print(")", end="")


# Postorder: Left, Right, Root
def postorder(node):
    if node:
        postorder(node.left)
        postorder(node.right)
        print(node.value, end=" ")



# STEP 4 - DECISION TREE

def decision_tree(password, verification, not_locked):

    if not password:
        return "Access Denied: Retry password or use account recovery."

    elif not verification:
        return "Access Denied: Retry second verification."

    elif not not_locked:
        return "Access Denied: Account locked. Contact support."

    else:
        return "Access Granted: All security checks passed."





# STEP 5 - KNOWLEDGE GRAPH

knowledge_graph = {
    "Account": [
        ("requires", "Password Check"),
        ("requires", "Verification"),
        ("has status", "Lockout")
    ],
    "Password Check": [
        ("evaluated by", "Login Rule")
    ],
    "Verification": [
        ("evaluated by", "Login Rule")
    ],
    "Lockout": [
        ("resolved through", "Help Desk")
    ],
    "Login Rule": [],
    "Help Desk": []
}


def show_knowledge_graph():
    print("\nKnowledge Graph:")

    for node, connections in knowledge_graph.items():
        for relationship, destination in connections:
            print(node, "--", relationship, "-->", destination)





# STEP 6 - WEBSITE INTEGRATION

def evaluate_login(password, verification, not_locked):
    result = check_login(password, verification, not_locked)

    explanation = decision_tree(
        password,
        verification,
        not_locked
    )

    return {
        "result": result,
        "explanation": explanation
    }






# STEP 7 - Truth Table Data for Website

def get_truth_table():
    rows = []

    for p in [True, False]:
        for v in [True, False]:
            for l in [True, False]:
                rows.append({
                    "P": p,
                    "V": v,
                    "L": l,
                    "AccessGranted": p and v and l
                })

    return rows







# STEP 8 - Expression Tree Data for Website

def get_tree_traversals():

    def pre(node):
        if node is None:
            return []
        return [node.value] + pre(node.left) + pre(node.right)

    def ino(node):
        if node is None:
            return []
        return ino(node.left) + [node.value] + ino(node.right)

    def post(node):
        if node is None:
            return []
        return post(node.left) + post(node.right) + [node.value]

    return {
        "preorder": pre(tree),
        "inorder": ino(tree),
        "postorder": post(tree)
    }







# STEP 9 - Knowledge Graph Data for Website

def get_knowledge_graph():
    nodes = list(knowledge_graph.keys())
    edges = []

    for source, connections in knowledge_graph.items():
        for relationship, destination in connections:
            edges.append({
                "source": source,
                "relationship": relationship,
                "target": destination
            })

    return {
        "nodes": nodes,
        "edges": edges,
        "adjacency_list": knowledge_graph
    }






# STEP 11 - Direct Run Test

if __name__ == "__main__":
    print("\nScenario D running directly")

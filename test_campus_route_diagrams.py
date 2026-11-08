"""Run: python -m unittest test_campus_route_diagrams.py -v"""
import copy
import unittest
from campus_route_diagrams import (get_evaluator, example_input, validate_graph,
                                   make_decision_tree, make_knowledge_graph)


class CampusRouteDiagramsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evaluate, _ = get_evaluator()

    def test_diagram_and_adjacency_relationships_match(self):
        result = type(self).evaluate(example_input())
        self.assertEqual(validate_graph(result), (16, 15))
        self.assertEqual(len(result["knowledge_graph_edges"]), 16)

    def test_decision_tree_has_correct_recommendation(self):
        result = type(self).evaluate(example_input())
        graph = make_decision_tree(result)
        self.assertIn("Recommend: Train", graph)
        self.assertIn("backup_reject", graph)
        self.assertNotIn("backup_D [", graph)  # Stops after failed fare.

    def test_graph_draws_every_actual_relationship(self):
        result = type(self).evaluate(example_input())
        graph = make_knowledge_graph(result)
        self.assertEqual(graph.count(' -> '), len(result["knowledge_graph_edges"]))
        self.assertIn('"Maya" -> "Campus" [label="needs to reach"]', graph)

    def test_change_inputs_changes_decision_but_stays_consistent(self):
        data = copy.deepcopy(example_input())
        data["priority"] = "cheapest"
        result = type(self).evaluate(data)
        self.assertEqual(result["recommended"], "bus")
        self.assertIn("Recommend: Bus", make_decision_tree(result))
        self.assertEqual(validate_graph(result), (16, 15))


if __name__ == "__main__":
    unittest.main()

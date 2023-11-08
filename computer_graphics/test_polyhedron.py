import unittest
import igraph as ig
from .solid import to_line, sort_pairs

def get_plain_graph() -> ig.Graph:
    return ig.Graph(n=5, edges=[
        (0, 1),
        (0, 4),
        (1, 2),
        (1, 3),
    ])

class TestToLine(unittest.TestCase):
    def test_plain(self):
        graph = get_plain_graph()
        line = to_line(graph)
        self.assertEqual(line, [0, 4, 0, 1, 3, 1, 2])
    
    def test_square(self):
        graph = ig.Graph(n=4, edges=[
            (0, 1),
            (0, 2),
            (1, 3),
            (2, 3),
        ])
        line = to_line(graph)
        self.assertEqual(line, [])

class TestSortPairs(unittest.TestCase):
    def test_penta(self):
        edges = [
            (1, 0),
            (1, 2),
            (3, 2),
            (3, 4),
            (4, 0),
        ]
        expected_edges = [
            (0, 1),
            (1, 2),
            (2, 3),
            (3, 4),
            (4, 0),
        ]
        sorted_edges = sort_pairs(edges)
        self.assertEqual(sorted_edges, expected_edges)

if __name__ == '__main__':
    unittest.main()
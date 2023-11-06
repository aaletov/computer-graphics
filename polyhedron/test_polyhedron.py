import unittest
import igraph as ig
from .polyhedron import to_line, to_triangulized

class TestToLine(unittest.TestCase):
    def test_plain(self):
        graph = ig.Graph(n=4, edges=[
            (0, 1),
            (0, 4),
            (1, 2),
            (1, 3),
        ])
        line = to_line(graph)
        self.assertEqual(line, [0, 4, 0, 1, 3, 1, 2])

class TestToTriangulized(unittest.TestCase):
    def test_plain(self):
        graph = ig.Graph(n=5, edges=[
            (0, 1),
            (1, 2),
            (2, 3),
            (3, 4),
            (4, 0),
        ])
        triangulized = to_triangulized(graph)
        edges = list([(es.source, es.target) for es in triangulized.es])
        self.assertEqual(edges, [(0, 1), (1, 2), (2, 3), (3, 4), (0, 4), (1, 3), (1, 4)])

if __name__ == '__main__':
    unittest.main()
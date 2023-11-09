import unittest
import numpy as np
import igraph as ig
from .solid import SolidGraph

def get_square_graph() -> SolidGraph:
    return SolidGraph(ig.Graph(n=4, edges=[
            (0, 1),
            (0, 2),
            (1, 3),
            (2, 3),
        ],
        graph_attrs={
            "faces": [
                1
            ],
        },
        vertex_attrs={
            "name": [
                "A",
                "B",
                "C",
                "D",
            ],
            "faces": [
                [1],
                [1],
                [1],
                [1],
            ],
        },
    ))

def get_penta_graph() -> SolidGraph:
    return SolidGraph(ig.Graph(n=5, edges = [
            (0, 1),
            (1, 2),
            (2, 3),
            (3, 4),
            (4, 0),
        ],
        graph_attrs={
            "faces": [
                1
            ],
        },
        vertex_attrs={
            "name": [
                "A",
                "B",
                "C",
                "D",
                "E",
            ],
            "faces": [
                [1],
                [1],
                [1],
                [1],
                [1],
            ],
        },
    ))

def get_cube_graph() -> SolidGraph:
    return SolidGraph(ig.Graph(8, edges=[
            (0, 1),
            (0, 3),
            (0, 4),
            (6, 2),
            (6, 5),
            (6, 7),
            (4, 5),
            (4, 7),
            (1, 5),
            (1, 2),
            (3, 2),
            (3, 7),
        ],
        graph_attrs={
            "faces": [
                0,
                1,
                2,
                3,
                4,
                5,
            ],
        },
        vertex_attrs={
            "name": [
                "A",
                "B",
                "C",
                "D",
                "E",
                "F",
                "G",
                "H",
            ],
            "faces": [
                [0, 1, 4],
                [0, 1, 2],
                [0, 2, 3],
                [0, 3, 4],
                [1, 4, 5],
                [1, 2, 5],
                [2, 3, 5],
                [3, 4, 5],
            ],
        }
    ))


class TestGetCoverLine(unittest.TestCase):
    def test_square(self):
        graph = get_square_graph()
        line = graph.get_cover_line()
        expected = np.array([0, 1, 1, 3, 0, 2, 2, 3])
        self.assertTrue(np.equal(expected, line).all())

    def test_penta(self):
        graph = get_penta_graph()
        line = graph.get_cover_line()
        expected = np.array([0, 1, 0, 4, 3, 4, 1, 2, 2, 3])
        self.assertTrue(np.equal(expected, line).all())

    def test_cube(self):
        graph = get_cube_graph()
        line = graph.get_cover_line()
        expected = np.array([0, 1, 1, 2, 2, 6, 1, 5, 5, 6, 0, 4, 4, 7, 4, 5, 0, 3, 3, 7, 6, 7, 2, 3])
        self.assertTrue(np.equal(expected, line).all())

class TestGetCoverTriangles(unittest.TestCase):
    def test_square(self):
        graph = get_square_graph()
        line = graph.get_cover_triangles()
        expected = np.array([
            0, 2, 3,
            0, 3, 1,
        ])
        self.assertTrue(np.equal(expected, line).all())

    def test_penta(self):
        graph = get_penta_graph()
        line = graph.get_cover_triangles()
        expected = np.array([
            0, 4, 3,
            0, 3, 2,
            0, 2, 1,
        ])
        self.assertTrue(np.equal(expected, line).all())

    def test_cube(self):
        graph = get_cube_graph()
        line = graph.get_cover_triangles()
        expected = np.array([
            0, 1, 2,
            0, 2, 3,
            0, 1, 5,
            0, 5, 4,
            0, 3, 7,
            0, 7, 4,
            2, 6, 5,
            2, 5, 1,
            2, 6, 7,
            2, 7, 3,
        ])
        print(line)
        self.assertTrue(np.equal(expected, line).all())

class TestGetCycles(unittest.TestCase):
    def test_square(self):
        graph = get_square_graph()
        cycles = graph.get_cycles()
        expected = np.array([
            [0, 1, 2, 3],
        ])
        self.assertTrue(np.equal(expected, cycles).all())

    def test_penta(self):
        graph = get_penta_graph()
        cycles = graph.get_cycles()
        expected = np.array([
            [0, 1, 2, 3, 4],
        ])
        self.assertTrue(np.equal(expected, cycles).all())

    def test_cube(self):
        graph = get_cube_graph()
        cycles = graph.get_cycles()
        expected = np.array([
            0, 1, 2,
            0, 2, 3,
            0, 1, 5,
            0, 5, 4,
            0, 3, 7,
            0, 7, 4,
            2, 6, 5,
            2, 5, 1,
            2, 6, 7,
            2, 7, 3,
        ])
        self.assertTrue(np.equal(expected, cycles).all())



# class TestSortPairs(unittest.TestCase):
#     def test_penta(self):
#         edges = [
#             (1, 0),
#             (1, 2),
#             (3, 2),
#             (3, 4),
#             (4, 0),
#         ]
#         expected_edges = [
#             (0, 1),
#             (1, 2),
#             (2, 3),
#             (3, 4),
#             (4, 0),
#         ]
#         sorted_edges = sort_pairs(edges)
#         self.assertEqual(sorted_edges, expected_edges)

if __name__ == '__main__':
    unittest.main()
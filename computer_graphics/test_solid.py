import unittest
import numpy as np
import numpy.testing as npt
import igraph as ig
from .solid import Solid
from itertools import permutations
from typing import Any, List

def get_square_graph() -> Solid:
    graph = ig.Graph(graph_attrs={
        "faces": [
            0,
        ],
    })
    graph.add_vertices(n=4, attributes={
        "name": [
            "A",
            "B",
            "C",
            "D",
        ],
        "faces": [
            [0],
            [0],
            [0],
            [0],
        ],
        "coord": [
            (0.0, 0.0, 0.0),
            (0.0, 1.0, 0.0),
            (1.0, 1.0, 0.0),
            (1.0, 0.0, 0.0),
        ]
    })
    graph.add_edges([
        ("A", "B"),
        ("B", "C"),
        ("C", "D"),
        ("D", "A"),
    ])
    return Solid(graph)

def get_penta_graph() -> Solid:
    graph = ig.Graph(graph_attrs={
        "faces": [
            0,
        ],
    })
    graph.add_vertices(n=5, attributes={
        "name": [
            "A",
            "B",
            "C",
            "D",
            "E",
        ],
        "faces": [
            [0],
            [0],
            [0],
            [0],
            [0],
        ],
        "coord": [
            (0.79, 0.1, 0.0),
            (0.98, 0.65, 0.0),
            (0.5, 1.0, 0.0),
            (0.02, 0.65, 0.0),
            (0.2, 0.1, 0.0),
        ],
    })
    graph.add_edges([
        ("A", "B"),
        ("B", "C"),
        ("C", "D"),
        ("D", "E"),
        ("E", "A"),
    ])
    return Solid(graph)

def get_cube_graph() -> Solid:
    graph = ig.Graph(graph_attrs={
        "faces": [
            0,
            1,
            2,
            3,
            4,
            5,
        ],
    })
    graph.add_vertices(n=8, attributes={
        "name": [
            "A",
            "B",
            "C",
            "D",
            "E",
            "F",
            "G",
            "H"
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
        "coord": [
            (0.0,0.0,0.0),
            (0.0,1.0,0.0),
            (1.0,1.0,0.0),
            (1.0,0.0,0.0),
            (0.0,0.0,1.0),
            (0.0,1.0,1.0),
            (1.0,1.0,1.0),
            (1.0,0.0,1.0),
        ],
    })
    graph.add_edges([
        ("A", "B"),
        ("A", "D"),
        ("A", "E"),
        ("G", "C"),
        ("G", "F"),
        ("G", "H"),
        ("E", "F"),
        ("E", "H"),
        ("B", "F"),
        ("B", "C"),
        ("D", "C"),
        ("D", "H"),
    ])
    return Solid(graph)

class CustomMatchers(unittest.TestCase):
    def assert_equal_with_shifts(self, x: np.ndarray, y: np.ndarray):
        res = False
        for i in range(x.shape[0]):
            res |= np.allclose(x, y)
            x = np.roll(x, 1)

        if not res:
            msg = npt.build_err_msg([x, y], "Arrays not equal")
            raise AssertionError(msg)
        
    def assert_contains_tuples(self, x: np.ndarray, y: np.ndarray, tuple_size: int):
        rows = x.shape[0] // tuple_size
        x = x.reshape((rows, tuple_size))
        y = y.reshape((rows, tuple_size))
        xl: List[Any] = x.tolist()
        yl: List[Any] = y.tolist()
        res = True
        for tup in xl:
            i = yl.index(tup) if tup in yl else None
            if i != None:
                yl.pop(i)
            else:
                res = False
                break

        if not res:
            msg = npt.build_err_msg([x, y], "Arrays not equal")
            raise AssertionError(msg)
        
    def assert_equal_tuples(self, x: np.ndarray, y: np.ndarray, tuple_size: int):
        rows = x.shape[0] // tuple_size
        x = x.reshape((rows, tuple_size))
        y = y.reshape((rows, tuple_size))
        xl: List[Any] = set(map(tuple, x.tolist()))
        yl: List[Any] = set(map(tuple, y.tolist()))
        self.assertEqual(xl, yl)

class TestGetCoverLineIdx(CustomMatchers):
    def test_square(self):
        graph = get_square_graph()
        line = graph.get_cover_line_idx()
        expected = np.array([0, 1, 1, 2, 2, 3, 0, 3])
        self.assert_equal_tuples(line, expected, 2)

    def test_penta(self):
        graph = get_penta_graph()
        line = graph.get_cover_line_idx()
        expected = np.array([0, 1, 0, 4, 3, 4, 1, 2, 2, 3])
        self.assert_equal_tuples(line, expected, 2)

    def test_cube(self):
        graph = get_cube_graph()
        line = graph.get_cover_line_idx()
        expected = np.array([0, 1, 1, 2, 2, 6, 1, 5, 5, 6, 0, 4, 4, 7, 4, 5, 0, 3, 3, 7, 6, 7, 2, 3])
        self.assert_equal_tuples(line, expected, 2)

# class TestGetCoverLine(CustomMatchers):
#     def assert_lines_equal(self, line: np.ndarray, exp: np.ndarray):
#         nline = line.reshape((line.shape[0] // 6, 6))
#         nexp = exp.reshape((exp.shape[0] // 6, 6))
#         self.assert_equal_with_shifts(nline, nexp)

#     def test_square(self):
#         graph = get_square_graph()
#         line = graph.get_cover_line()
#         expected = np.array([
#             0.0, 0.0, 0.0,
#             0.0, 1.0, 0.0,
#             0.0, 1.0, 0.0,
#             1.0, 1.0, 0.0,
#             1.0, 1.0, 0.0,
#             1.0, 0.0, 0.0,
#             1.0, 0.0, 0.0,
#             0.0, 0.0, 0.0,
#         ])
#         self.assert_lines_equal(line, expected)

#     def test_penta(self):
#         graph = get_penta_graph()
#         line = graph.get_cover_line()
#         expected = np.array([
#             0.79, 0.1, 0.0,
#             0.98, 0.65, 0.0,
#             0.5, 1.0, 0.0,
#             0.02, 0.65, 0.0,
#             0.2, 0.1, 0.0,
#         ])
#         nline = line.reshape((line.shape[0] // 3, 3))
#         nexp = expected.reshape((expected.shape[0] // 3, 3))
#         self.assert_equal_with_shifts(nline, nexp)

#     def test_cube(self):
#         graph = get_cube_graph()
#         line = graph.get_cover_line()
#         expected = np.array([
#             0.0, 0.0, 0.0,
#             0.0, 1.0, 0.0,
#             1.0, 1.0, 0.0,
#             1.0, 0.0, 0.0,
#         ])
#         nline = line.reshape((line.shape[0] // 3, 3))
#         nexp = expected.reshape((expected.shape[0] // 3, 3))
#         self.assert_equal_with_shifts(nline, nexp)
    

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
            0, 3, 2,
            0, 2, 1,
            0, 4, 5,
            0, 5, 1,
            1, 5, 6,
            1, 6, 2,
            2, 6, 7,
            2, 7, 3,
            0, 4, 7,
            0, 7, 3,
            4, 7, 6,
            4, 6, 5,
        ])
        self.assertTrue(np.equal(expected, line).all())

class TestGetCoverTrianglesTex(unittest.TestCase):
    def test_square(self):
        graph = get_square_graph()
        line = graph.get_cover_triangles_tex()
        expected = np.array([
            0, 1, 2,
            0, 2, 3,
        ])
        self.assertTrue(np.equal(expected, line).all())

    def test_penta(self):
        graph = get_penta_graph()
        line = graph.get_cover_triangles_tex()
        expected = np.array([
            0, 1, 2,
            0, 2, 3,
            0, 3, 4,
        ])
        self.assertTrue(np.equal(expected, line).all())

    def test_cube(self):
        graph = get_cube_graph()
        line = graph.get_cover_triangles_tex()
        expected = np.array([
            0, 1, 2,
            0, 2, 3,
        ] * 6)
        self.assertTrue(np.equal(expected, line).all())

if __name__ == '__main__':
    unittest.main()
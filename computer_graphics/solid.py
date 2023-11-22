from typing import Dict, Tuple, Any, List, Iterable
import math
import numpy as np
import pyrr
from numpy.typing import NDArray
import igraph as ig
from .revolution import Axis, create_revolution_graph


VertexLabel = int
    
class Solid:
    def __init__(self, graph: ig.Graph, is_polar=True) -> None:
        self.graph = graph
        self.is_polar = is_polar
        self.zero = pyrr.Vector3((0.0, 0.0, 0.0), dtype='f4')

    def to_coordinates(self, arr: np.ndarray[int, int]) -> np.ndarray[int, int]:
        oarr = np.ndarray(shape=(3 * arr.shape[0],))
        for i, idx in enumerate(arr):
            coord = self.graph.vs[idx]["coord"]
            for j in range(3):
                oarr[3 * i + j] = coord[j]
        return oarr

    @classmethod
    def cartesian_point(cls, point: pyrr.Vector3) -> pyrr.Vector3:
        r: float = point[0]
        teta: float = point[1]
        phi: float = point[2]
        return pyrr.Vector3((
            r * math.cos(phi) * math.cos(teta),
            r * math.cos(phi) * math.sin(teta),
            r * math.sin(phi),
        ))
    
    def to_cartesian(self) -> 'Solid':
        if not self.is_polar:
            raise RuntimeError("Already cartesian")

        new_graph = self.graph.copy()        
        for v in new_graph.dfsiter(0):
            v["coord"] = Solid.cartesian_point(v["coord"])

        return Solid(new_graph, is_polar=False)

    # Returns 1D ndarray
    def get_cover_line_idx(self) -> np.ndarray[int, int]:
        linegraph: ig.Graph = self.graph.linegraph()
        tree: ig.Graph = linegraph.spanning_tree()
        edges_idx, _ = tree.dfs(0)

        line = [0] * len(edges_idx)
        for i, e_idx in enumerate(edges_idx):
            e = self.graph.es[e_idx]
            line[i] = (e.source, e.target)

        return np.array(line).flatten()
    
    def get_cover_line(self) -> np.ndarray[int, int]:
        idx_arr = self.get_cover_line_idx()
        return self.to_coordinates(idx_arr)
    
    # Return sorted left
    @classmethod
    def sort_left(cls, le: Tuple[int, int], re: Tuple[int, int]) -> Tuple[int, int]:
        les, let = le[0], le[1]
        res, ret = re[0], re[1]
        if (les == res) or (les == ret):
            return (let, les)
        elif (let == res) or (let == ret):
            return (les, let)
        else:
            raise RuntimeError("edges not related")

    # Consider left already sorted
    @classmethod
    def sort_right(cls, le: Tuple[int, int], re: Tuple[int, int]) -> Tuple[int, int]:
        les, let = le[0], le[1]
        res, ret = re[0], re[1] 
        if let == ret:
            return (ret, res)
        elif let == res:
            return (res, ret)
        else:
            raise RuntimeError("edges not related")

    @classmethod
    def sort_pairs(cls, edges: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        sorted_list = []
        le = Solid.sort_left(edges[0], edges[1])
        for re in edges[1:]:
            sorted_re = Solid.sort_right(le, re)
            sorted_list.append(le)
            le = sorted_re
        sorted_list.append(le)
        return sorted_list

    # Returns 1D ndarray
    def get_cover_triangles_idx(self) -> np.ndarray[int, int]:
        triangles: List[Tuple[int, int, int]] = []

        for face in self.graph["faces"]:
            vertices = list(filter(lambda x: face in x["faces"], self.graph.vs))
            subgraph = self.graph.induced_subgraph(vertices)
            subpath, _ = subgraph.dfs(subgraph.vs[0].index)
            path = []
            for sv in subpath:
                for v in vertices:
                    if v["name"] == subgraph.vs[sv]["name"]:
                        path.append(v.index)
                        break
            pivot = path[0]
            for i in range(0, len(path) - 2):
                triangles.append(
                    (
                        pivot,
                        path[i + 1],
                        path[i + 2],
                    )
                )

        return np.array(triangles).flatten()
    
    def get_cover_triangles_tex(self) -> np.ndarray[int, int]:
        triangles: List[Tuple[int, int, int]] = []

        for face in self.graph["faces"]:
            vertices = list(filter(lambda x: face in x["faces"], self.graph.vs))
            subgraph = self.graph.induced_subgraph(vertices)
            subpath, _ = subgraph.dfs(subgraph.vs[0].index)
            # indexes = list([v.index for v in vertices])
            path = []
            for sv in subpath:
                for v in vertices:
                    if v["name"] == subgraph.vs[sv]["name"]:
                        path.append(sv)
                        break
            pivot = path[0]
            for i in range(0, len(path) - 2):
                triangles.append(
                    (
                        subpath.index(pivot),
                        subpath.index(path[i + 1]),
                        subpath.index(path[i + 2]),
                    )
                )

        return np.array(triangles).flatten()

    def get_cover_triangles(self) -> np.ndarray[int, int]:
        idx_arr = self.get_cover_triangles_idx()
        return self.to_coordinates(idx_arr)
    
    def get_vertices(self) -> np.ndarray[int, int]:
        vs = np.array([v.index for v in self.graph.vs])
        return self.to_coordinates(vs)
    
    @classmethod
    def angle(cls, x: np.array, y: np.array) -> float:
        xn = x / np.linalg.norm(x)
        yn = y / np.linalg.norm(y)
        return np.arccos(np.clip(np.dot(xn, yn), -1.0, 1.0))
    
    @classmethod
    def clockwise_angle(cls, x: np.array, y: np.array) -> float:
        xn = x / np.linalg.norm(x)
        yn = y / np.linalg.norm(y)
        dot = np.dot(xn, yn)
        det = xn[0] * yn[2] - yn[0] * xn[2]      # Determinant
        angle = math.atan2(det, dot)  # atan2(y, x) or atan2(sin, cos)
        return angle
    
    def get_normal(self, points: np.ndarray) -> np.ndarray:
        if points.shape != (3, 3):
            raise RuntimeError(f"Invalid shape {points.shape}")
        
        index: np.ndarray = np.subtract(points[2], points[1])
        mid: np.ndarray = np.subtract(points[1], points[0])
        normal_vec = np.cross(index, mid)
        # le costile begin
        center_vec = np.average(points, axis=0) - self.zero
        if Solid.angle(normal_vec, center_vec) > (math.pi / 2):
            normal_vec = - normal_vec
        # le costile end
        return normal_vec
    
    def get_normales(self) -> np.ndarray[int, int]:
        triangles = self.get_cover_triangles()
        triangles = triangles.reshape((triangles.shape[0] // (3 * 3), 3, 3))
        normales = [0] * triangles.shape[0]
        for i, triangle in enumerate(triangles):
            normal_vec = self.get_normal(triangle)
            normales[i] = normal_vec
        return np.array(normales).flatten()
    
    def get_normales_repeated(self) -> np.ndarray[int, int]:
        normales = self.get_normales()
        normales = normales.reshape((normales.shape[0] // 3, 3))
        normales = np.repeat(normales, repeats=3, axis=0)
        return normales.flatten()
    
    def get_common_edge(self, lface_idx: int, rface_idx: int) -> Tuple[int, int]:
        f = lambda v: (lface_idx in v["faces"]) and (rface_idx in v["faces"])
        vertices = filter(f, self.graph.vs)
        return tuple(v.index for v in vertices)
    
    def get_face_normal(self, face_idx: int) -> pyrr.Vector3:
        f = lambda v: face_idx in v["faces"]
        vertices = list(filter(f, self.graph.vs))
        coords = self.to_coordinates(np.array([v.index for v in vertices[0:3]])).reshape((3, 3))
        return self.get_normal(coords)
    
    def transform(self, matrix: pyrr.Matrix44) -> None:
        for v in self.graph.vs:
            v["coord"] = matrix * v["coord"]
        self.zero = matrix * self.zero
        return

def createDodecahedron() -> Solid:
    graph = ig.Graph(graph_attrs={
        "faces": [
            0,
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
        ],
    })
    R = 1.0
    RADIAN_DEGREE = math.pi / 180
    ALPHA = math.asin(math.sqrt(3) / 3)
    BETA = math.acos(math.sqrt(3) / (6 * math.sin(54 * RADIAN_DEGREE)))
    graph.add_vertices(n=20, attributes={
        "name": [
            "A", # 0 f1 f5 f10
            "B", # 1 f4 f6 f10
            "C", # 2 f3 f6 f9
            "D", # 3 f2 f5 f9
            "E", # 4 f4 f7 f12
            "F", # 5 f3 f7 f11
            "G", # 6 f2 f8 f11
            "H", # 7 f1 f8 f12
            "I", # 8 f1 f10 f12
            "J", # 9 f4 f10 f12
            "K", # 10 f3 f4 f6
            "L", # 11 f3 f9 f11
            "M", # 12 f2 f9 f11
            "N", # 13 f1 f2 f5
            "O", # 14 f1 f2 f8
            "P", # 15 f3 f4 f7
            "Q", # 16 f5 f6 f9
            "R", # 17 f7 f8 f11
            "S", # 18 f5 f6 f10
            "T", # 19 f7 f8 f12
        ],
        "faces": [
            [0, 4, 9],
            [3, 5, 9],
            [2, 5, 8],
            [1, 4, 8],
            [3, 6, 11],
            [2, 6, 10],
            [1, 7, 10],
            [0, 7, 11],
            [0, 9, 11],
            [3, 9, 11],
            [2, 3, 5],
            [2, 8, 10],
            [1, 8, 10],
            [0, 1, 4],
            [0, 1, 7],
            [2, 3, 6],
            [4, 5, 8],
            [6, 7, 10],
            [4, 5, 9],
            [6, 7, 11],
        ],
        "coord": [
            pyrr.Vector3((R, (math.pi / 4) + 0 *(math.pi / 2), ALPHA)), # A
            pyrr.Vector3((R, (math.pi / 4) + 1 *(math.pi / 2), ALPHA)), # B
            pyrr.Vector3((R, (math.pi / 4) + 2 *(math.pi / 2), ALPHA)), # C
            pyrr.Vector3((R, (math.pi / 4) + 3 *(math.pi / 2), ALPHA)), # D
            pyrr.Vector3((R, (math.pi / 4) + 1 * (math.pi / 2), -ALPHA)), # E
            pyrr.Vector3((R, (math.pi / 4) + 2 * (math.pi / 2), -ALPHA)), # F
            pyrr.Vector3((R, (math.pi / 4) + 3 * (math.pi / 2), -ALPHA)), # G
            pyrr.Vector3((R, (math.pi / 4) + 0 * (math.pi / 2), -ALPHA)), # H
            pyrr.Vector3((R, BETA, 0)), # I
            pyrr.Vector3((R, math.pi - BETA, 0)), # J
            pyrr.Vector3((R, math.pi, (math.pi / 2 - BETA))), # K
            pyrr.Vector3((R, math.pi + BETA, 0)), # L
            pyrr.Vector3((R, -BETA, 0)), # M
            pyrr.Vector3((R, 2 * math.pi, (math.pi/ 2 - BETA))), # N
            pyrr.Vector3((R, 2 * math.pi, -(math.pi / 2 - BETA))), # O
            pyrr.Vector3((R, math.pi, -(math.pi / 2 - BETA))), # P
            pyrr.Vector3((R, math.pi / 2, math.pi - BETA)), # Q
            pyrr.Vector3((R, math.pi / 2, math.pi + BETA)), # R
            pyrr.Vector3((R, math.pi / 2, BETA)), # S
            pyrr.Vector3((R, math.pi / 2, -BETA)), # T
        ],
    })
    graph.add_edges([
        ["A", "I"], # A-I
        ["A", "N"], # 
        ["A", "S"],
        ["B", "J"],
        ["B", "K"],
        ["B", "S"],
        ["C", "K"],
        ["C", "L"],
        ["C", "Q"],
        ["D", "M"],
        ["D", "N"],
        ["D", "Q"],
        ["E", "J"],
        ["E", "P"],
        ["E", "T"],
        ["F", "L"],
        ["F", "P"],
        ["F", "R"],
        ["G", "M"],
        ["G", "O"],
        ["G", "R"],
        ["H", "I"],
        ["H", "O"],
        ["H", "T"],
        ["I", "J"],
        ["K", "P"],
        ["L", "M"],
        ["N", "O"],
        ["Q", "S"],
        ["R", "T"],
    ])

    return Solid(graph).to_cartesian()

def createCube() -> Solid:
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

    R = 1.0
    RADIAN_DEGREE = math.pi / 180
    ALPHA = math.acos(math.sqrt(2) / math.sqrt(3))

    graph.add_vertices(n=8, attributes={
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
        "coord": [
            pyrr.Vector3((R, 5 * math.pi / 4, -ALPHA)),
            pyrr.Vector3((R, 3 * math.pi / 4, -ALPHA)),
            pyrr.Vector3((R, 1 * math.pi / 4, -ALPHA)),
            pyrr.Vector3((R, 7 * math.pi / 4, -ALPHA)),
            pyrr.Vector3((R, 5 * math.pi / 4, ALPHA)),
            pyrr.Vector3((R, 3 * math.pi / 4, ALPHA)),
            pyrr.Vector3((R, 1 * math.pi / 4, ALPHA)),
            pyrr.Vector3((R, 7 * math.pi / 4, ALPHA)),
        ],
    })
    graph.add_edges([
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
    ])

    return Solid(graph).to_cartesian()

def createTetrahedron() -> Solid:
    graph = ig.Graph(graph_attrs={
        "faces": [
            0,
            1,
            2,
            3,
        ],
    })
    R = 1.0
    RADIAN_DEGREE = math.pi / 180
    ALPHA = (math.pi / 2) - math.atan(math.sqrt(2))
    graph.add_vertices(n=4, attributes={
        "name": [
            "D",
            "A",
            "B",
            "C",
        ],
        "coord": [
            pyrr.Vector3((R, 0, math.pi / 2)),
            pyrr.Vector3((R, 1 * math.pi / 3, -ALPHA)),
            pyrr.Vector3((R, 3 * math.pi / 3, -ALPHA)),
            pyrr.Vector3((R, 5 * math.pi / 3, -ALPHA)),
        ],
        "faces": [
            [1, 2, 3],
            [0, 1, 2],
            [0, 2, 3],
            [0, 3, 1],
        ],
    })
    graph.add_edges([
        ("A", "B"),
        ("A", "C"),
        ("A", "D"),
        ("B", "C"),
        ("C", "D"),
        ("D", "B"),
    ])

    return Solid(graph).to_cartesian()

def createCone() -> Solid:
    line = [
        pyrr.Vector3((0.0, 1.0, 0.0)),
        pyrr.Vector3((1.0, 0.0, 0.0)),
    ]
    graph = create_revolution_graph(line, axis=Axis.Y)
    new_idx = [0] * graph["pieces"] + [i + 1 for i in range(graph["pieces"])]
    
    attr_num = 0
    def combinator(values: List[Any]) -> List[Any]:
        nonlocal attr_num
        if len(values) == 1:
            return values[0]
        if attr_num == 1: # faces
            faces = set()
            for farr in values:
                subset = set(farr)
                faces |= subset
            values = list(faces)
        else:
            values = values[0]
        attr_num += 1
        return values

    graph.contract_vertices(new_idx, combine_attrs=combinator)
    
    del_edges = []
    for e in graph.es:
        if e.source == e.target:
            del_edges.append(e.index)
    graph.delete_edges(del_edges)
    
    tt = list([e for e in graph.es])
    ttt = list([v for v in graph.vs])

    return Solid(graph, is_polar=False)
from typing import Dict, Tuple, Any, List
import math
import numpy as np
from numpy.typing import NDArray
import igraph as ig


VertexLabel = int
Point = Tuple[float, float, float]

class SolidGraph:
    def __init__(self, graph: ig.Graph):
        self.graph = graph

    # Returns 2D ndarray
    @classmethod
    def to_line(cls, graph: ig.Graph) -> np.ndarray[int, int]:
        linegraph: ig.Graph = graph.linegraph()
        tree: ig.Graph = linegraph.spanning_tree()
        edges, _ = tree.dfs(0)
        return np.array([(graph.es[e].source, graph.es[e].target) for e in edges])

    # Returns 1D ndarray
    def get_cover_line(self) -> np.ndarray[int, int]:
        line: np.ndarray[int, int] = SolidGraph.to_line(self.graph)
        return line.flatten()
    
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
        le = SolidGraph.sort_left(edges[0], edges[1])
        for re in edges[1:]:
            sorted_re = SolidGraph.sort_right(le, re)
            sorted_list.append(le)
            le = sorted_re
        sorted_list.append(le)
        return sorted_list
    
    # Returns 1D ndarray
    def get_cover_triangles(self) -> np.ndarray[int, int]:
        triangles: List[Tuple[int, int, int]] = []
        for cycle in self.graph.fundamental_cycles():
            pairs = list([(self.graph.es[e].source, self.graph.es[e].target) for e in cycle])
            pairs = SolidGraph.sort_pairs(pairs)
            vertices = [pairs[0][0]] + [pair[1] for pair in pairs]
            pivot = vertices[0]
            for i in range(0, len(vertices) - 2):
                triangles.append(
                    (
                        pivot,
                        vertices[i + 1],
                        vertices[i + 2],
                    )
                )

        return np.array(triangles).flatten()
    
    def get_vertices(self) -> np.ndarray[int, int]:
        return np.array([v.index for v in self.graph.vs])
    
class SolidCoordinates:
    def __init__(self, coords: Dict[VertexLabel, Point], is_polar=True):
        self.coords = coords
        self.is_polar = is_polar

    @classmethod
    def cartesian_point(cls, point: Point) -> Point:
        r: float = point[0]
        teta: float = point[1]
        phi: float = point[2]
        return (
            r * math.cos(phi) * math.cos(teta),
            r * math.cos(phi) * math.sin(teta),
            r * math.sin(phi),
        )

    def to_cartesian(self) -> 'SolidCoordinates':
        if not self.is_polar:
            raise RuntimeError("Already cartesian")
        
        cartesian_coords: Dict[VertexLabel, Point] = {}
        for k, v in self.coords.items():
            cartesian_coords[k] = SolidCoordinates.cartesian_point(v)
        return SolidCoordinates(cartesian_coords, is_polar=False)
    
class Solid:
    def __init__(self, sgraph: SolidGraph, scoord: SolidCoordinates) -> None:
        self.sgraph = sgraph
        self.scoord = scoord

    def to_coordinates(self, arr: np.ndarray[int, int]) -> np.ndarray[int, int]:
        out = np.ndarray(shape=(3 * arr.shape[0]),)
        for i, x in enumerate(np.nditer(arr)):
            cs  = self.scoord.coords[x.item()]
            out[3*i] = cs[0]
            out[3*i + 1] = cs[1]
            out[3*i + 2] = cs[2]
        return out

    def get_cover_line(self) -> np.ndarray[int, int]:
        graph_line = self.sgraph.get_cover_line()
        return self.to_coordinates(graph_line)
    
    def get_cover_triangles(self) -> np.ndarray[int, int]:
        triangles = self.sgraph.get_cover_triangles()
        return self.to_coordinates(triangles)
    
    def get_vertices(self) -> np.ndarray[int, int]:
        return self.to_coordinates(self.sgraph.get_vertices())

    def get_cover_line_idx(self) -> np.ndarray[int, int]:
        return self.sgraph.get_cover_line()

    def get_cover_triangles_idx(self) -> np.ndarray[int, int]:
        return self.sgraph.get_cover_triangles()


def createDodecahedron() -> Solid:
    graph = ig.Graph(20, edges=[
        [0, 8],
        [0, 13],
        [0, 18],
        [1, 9],
        [1, 10],
        [1, 18],
        [2, 10],
        [2, 11],
        [2, 16],
        [3, 12],
        [3, 13],
        [3, 16],
        [4, 9],
        [4, 15],
        [4, 19],
        [5, 11],
        [5, 15],
        [5, 17],
        [6, 12],
        [6, 14],
        [6, 17],
        [7, 8],
        [7, 14],
        [7, 19],
        [8, 9],
        [10, 15],
        [11, 12],
        [13, 14],
        [16, 18],
        [17, 19],
    ])

    R = 1.0
    RADIAN_DEGREE = math.pi / 180
    ALPHA = math.asin(math.sqrt(3) / 3)
    BETA = math.acos(math.sqrt(3) / (6 * math.sin(54 * RADIAN_DEGREE)))

    polar_coords: Dict[VertexLabel, Point] = {
        # [0, 1, 2, 3, 7, 4, 5, 6, 8, 9, 11, 12, 18, 16, 17, 19, 13, 14, 10, 15]
        # ['A', 'B', 'C', 'D', 'H', 'E', 'F', 'G', 'I', 'J', 'L', 'M', 'S', 'Q', 'R', 'T', 'N', 'O', 'K', 'P']
        0: (R, (math.pi / 4) + 0 *(math.pi / 2), ALPHA), # A
        1: (R, (math.pi / 4) + 1 *(math.pi / 2), ALPHA), # B
        2: (R, (math.pi / 4) + 2 *(math.pi / 2), ALPHA), # C
        3: (R, (math.pi / 4) + 3 *(math.pi / 2), ALPHA), # D
        7: (R, (math.pi / 4) + 0 * (math.pi / 2), -ALPHA), # H
        4: (R, (math.pi / 4) + 1 * (math.pi / 2), -ALPHA), # E
        5: (R, (math.pi / 4) + 2 * (math.pi / 2), -ALPHA), # F
        6: (R, (math.pi / 4) + 3 * (math.pi / 2), -ALPHA), # G
        8: (R, BETA, 0), # I
        9: (R, math.pi - BETA, 0), # J
        11: (R, math.pi + BETA, 0), # L
        12: (R, -BETA, 0), # M
        18: (R, math.pi / 2, BETA), # S
        16: (R, math.pi / 2, math.pi - BETA), # Q
        17: (R, math.pi / 2, math.pi + BETA), # R
        19: (R, math.pi / 2, -BETA), # T
        13: (R, 2 * math.pi, (math.pi/ 2 - BETA)), # N
        14: (R, 2 * math.pi, -(math.pi / 2 - BETA)), # O
        10: (R, math.pi, (math.pi / 2 - BETA)), # K
        15: (R, math.pi, -(math.pi / 2 - BETA)), # P
    }

    scoord = SolidCoordinates(polar_coords).to_cartesian()
    sgraph = SolidGraph(graph)

    return Solid(sgraph, scoord)

def createCube() -> Solid:
    graph = ig.Graph(8, edges=[
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

    R = 1.0
    RADIAN_DEGREE = math.pi / 180
    ALPHA = math.asin(math.sqrt(2) / math.sqrt(3))

    polar_coords: Dict[VertexLabel, Point] = {
        0: (R, 5 * math.pi / 4, -ALPHA),
        1: (R, 3 * math.pi / 4, -ALPHA),
        2: (R, 1 * math.pi / 4, -ALPHA),
        3: (R, 7 * math.pi / 4, -ALPHA),
        4: (R, 5 * math.pi / 4, ALPHA),
        5: (R, 3 * math.pi / 4, ALPHA),
        6: (R, 1 * math.pi / 4, ALPHA),
        7: (R, 7 * math.pi / 4, ALPHA),
    }

    scoord = SolidCoordinates(polar_coords).to_cartesian()
    sgraph = SolidGraph(graph)

    return Solid(sgraph, scoord)

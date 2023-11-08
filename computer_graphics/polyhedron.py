from typing import Dict, Tuple, Any, List
import math
import igraph as ig


VertexLabel = int
Point = Tuple[float, float, float]

# Return sorted left
# def sort_left(graph: ig.Graph, le: int, re: int) -> Tuple[int, int]:
#     les, let = graph.es[le].source, graph.es[le].target
#     res, ret = graph.es[re].source, graph.es[re].target
#     if (les == res) or (les == ret):
#         return (let, les)
#     elif (let == res) or (let == ret):
#         return (les, let)
#     else:
#         raise RuntimeError("edges not related")

# # Consider left already sorted
# def sort_right(graph: ig.Graph, les: int, let: int, re: int) -> Tuple[int, int]:
#     res, ret = graph.es[re].source, graph.es[re].target
#     # Few extra checks
#     if (ret == les) or (ret == let):
#         return (ret, res)
#     elif (res == les) or (res == let):
#         return (res, ret)
#     else:
#         raise RuntimeError("edges not related")

# def align_edges(graph: ig.Graph, edge_idx: List[int]) -> List[int]:
#     sorted_list = []
#     les, let = sort_left(graph, edge_idx[0], edge_idx[1])
#     for re in edge_idx[1:]:
#         res, ret = sort_right(graph, les, let, re)
#         sorted_list += [les, let]
#         les, let = res, ret
#     sorted_list += [les, let]
#     return sorted_list

def to_line(graph: ig.Graph) -> List[Tuple[int, int]]:
    linegraph: ig.Graph = graph.linegraph()
    tree: ig.Graph = linegraph.spanning_tree()
    edges, parents = tree.dfs(0)
    # edge_line = []
    # for i in range(len(edges) - 1):
    #     e, p = edges[i], parents[i]
    #     if len(edge_line) == 0:
    #         edge_line.append(e)
    #         continue

    #     path: list = tree.get_shortest_path(edge_line[-1], e)[1:]
    #     edge_line += path
    # return list([(graph.es[e].source, graph.es[e].target) for e in edge_line])
    return list([(graph.es[e].source, graph.es[e].target) for e in edges])

def to_cartesian(point: Point) -> Point:
  r: float = point[0]
  teta: float = point[1]
  phi: float = point[2]
  return (
    r * math.cos(phi) * math.cos(teta),
    r * math.cos(phi) * math.sin(teta),
    r * math.sin(phi),
  )

def to_triangulized(ingraph: ig.Graph) -> ig.Graph:
    graph = ingraph.copy()
    for cycle in graph.fundamental_cycles():
        for i in range(0, 2 * (len(cycle) - 3), 2):
            edgel = graph.es[cycle[i]]
            edger = graph.es[cycle[i+1]]
            vertices = [
                edgel.source,
                edgel.target,
                edger.source,
                edger.target,
            ]
            adj_vertices = filter(lambda x: vertices.count(x) == 1, vertices)
            graph.add_edge(*adj_vertices)
    return graph

class Polyhedron:
    def __init__(self, coords: Dict[VertexLabel, Point], graph: ig.Graph, is_polar=True):
        self.coords = coords
        self.graph = graph
        self.is_polar = is_polar

    def to_cartesian(self) -> 'Polyhedron':
        if not self.is_polar:
            raise RuntimeError("Already cartesian")
        
        cartesian_coords: Dict[VertexLabel, Point] = {}
        for k, v in self.coords.items():
            cartesian_coords[k] = to_cartesian(v)
        return Polyhedron(cartesian_coords, self.graph, is_polar=False)

    def get_cover_line(self) -> List[Point]:
        line = to_line(self.graph)
        cover_line = []
        for pair in line:
            for point in pair:
                cover_line.append(self.coords[point]) 
        return cover_line
    
    def get_cover_triangles(self) -> List[Tuple[Point, Point, Point]]:
        triangulized = to_triangulized(self.graph)
        triangles = []
        for triangle in triangulized.fundamental_cycles():
            vertices = set()
            for edge in triangle:
                vertices.add(triangulized.es[edge].source)
                vertices.add(triangulized.es[edge].target)
            ordered_vertices = list(vertices)
            triangles.append((
                self.coords[ordered_vertices[0]],
                self.coords[ordered_vertices[1]],
                self.coords[ordered_vertices[2]],
            ))
        return triangles
        

def createDodecahedron() -> Polyhedron:
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
        0: (R, (math.pi / 4) + 0*(math.pi / 2), ALPHA), # A
        1: (R, (math.pi / 4) + 1*(math.pi / 2), ALPHA), # B
        2: (R, (math.pi / 4) + 2*(math.pi / 2), ALPHA), # C
        3: (R, (math.pi / 4) + 3*(math.pi / 2), ALPHA), # D
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

    polar_dhedron = Polyhedron(polar_coords, graph)
    cartesian_dhedron = polar_dhedron.to_cartesian()

    return cartesian_dhedron

def createCube() -> Polyhedron:
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

    polar_cube = Polyhedron(polar_coords, graph)
    cartesian_cube = polar_cube.to_cartesian()

    return cartesian_cube

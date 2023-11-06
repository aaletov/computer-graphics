from typing import Dict, Tuple, Any, List
import math
import igraph as ig


VertexLabel = int
Point = Tuple[float, float, float]

def to_line(graph: ig.Graph) -> list:
    tree: ig.Graph = graph.spanning_tree()
    vertices, parents = tree.dfs(0)
    line = []
    for i in range(len(vertices)):
        v, p = vertices[i], parents[i]
        if len(line) == 0:
            line.append(v)
            continue

        path: list = tree.get_shortest_path(line[-1], v)[1:]
        line += path
    return line

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
        return self.__init__(cartesian_coords, self.graph, is_polar=False)

    def get_cover_line(self) -> List[Point]:
        line = to_line(self.graph)
        return list([self.coords[v] for v in line])
    
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
        0: (R, (math.pi / 4) + 0*(math.pi / 2), ALPHA),
        1: (R, (math.pi / 4) + 1*(math.pi / 2), ALPHA),
        2: (R, (math.pi / 4) + 2*(math.pi / 2), ALPHA),
        3: (R, (math.pi / 4) + 3*(math.pi / 2), ALPHA),
        4: (R, (math.pi / 4) + 0 * (math.pi / 2), -ALPHA),
        5: (R, (math.pi / 4) + 1 * (math.pi / 2), -ALPHA),
        6: (R, (math.pi / 4) + 2 * (math.pi / 2), -ALPHA),
        7: (R, (math.pi / 4) + 3 * (math.pi / 2), -ALPHA),
        8: (R, BETA, 0),
        9: (R, math.pi - BETA, 0),
        10: (R, math.pi + BETA, 0),
        11: (R, -BETA, 0),
        12: (R, math.pi / 2, BETA),
        13: (R, math.pi / 2, math.pi - BETA),
        14: (R, math.pi / 2, math.pi + BETA),
        15: (R, math.pi / 2, -BETA),
        16: (R, 2 * math.pi, (math.pi/ 2 - BETA)),
        17: (R, 2 * math.pi, -(math.pi / 2 - BETA)),
        18: (R, math.pi, (math.pi / 2 - BETA)),
        19: (R, math.pi, -(math.pi / 2 - BETA)),
    }

    polar_dhedron = Polyhedron(polar_coords, graph)
    cartesian_dhedron = polar_dhedron.to_cartesian()

    return cartesian_dhedron

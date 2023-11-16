from enum import Enum
import math
import pyrr
from typing import List, Tuple
import numpy as np
import igraph as ig

class Axis(Enum):
    X = 1
    Y = 2
    Z = 3

def get_rotation_matrix_x(angle: float) -> pyrr.Matrix33:
    return pyrr.Matrix33([
        1.0, 0.0, 0.0,
        0, math.cos(angle), - math.sin(angle),
        0, math.sin(angle), math.cos(angle),
    ], dtype='f4')

def get_rotation_matrix_y(angle: float) -> pyrr.Matrix33:
    return pyrr.Matrix33([
        math.cos(angle), 0, math.sin(angle),
        0.0, 1.0, 0.0,
        - math.sin(angle), 0, math.cos(angle),
    ], dtype='f4')

def get_rotation_matrix_z(angle: float) -> pyrr.Matrix33:
    return pyrr.Matrix33([
        math.cos(angle), - math.sin(angle), 0,
        math.sin(angle), math.cos(angle), 0,
        0.0, 0.0, 1.0,
    ], dtype='f4')

def rotate_vertex(vertex: pyrr.Vector3, axis: Axis, angle: np.float64) -> pyrr.Vector3:
    matrix_getters = {
        Axis.X: get_rotation_matrix_x,
        Axis.Y: get_rotation_matrix_y,
        Axis.Z: get_rotation_matrix_z,
    }

    matrix: pyrr.Matrix33 = matrix_getters[axis](angle)
    return matrix * vertex

def rotate_line(line: List[pyrr.Vector3], axis: Axis, angle: np.float64) -> List[pyrr.Vector3]:
    converter = lambda p: rotate_vertex(p, axis, angle)
    return list(map(converter, line))

def connect_revolution_line(graph: ig.Graph, prev_keys: List[str], curr_keys: List[str]) -> None:
    graph.add_edges(es=list(zip(prev_keys, curr_keys)))
    return

def add_revolution_line(graph: ig.Graph, keys: List[str]) -> None:
    graph.add_vertices(n=len(keys), attributes={
        "name": keys,
    })
    edges = [0] * (len(keys) - 1)
    for i in range(len(keys) - 1):
        edges[i] = (keys[i], keys[i+1])
    graph.add_edges(edges)
    return

def get_mesh_graph(shape=Tuple[int,int]) -> ig.Graph:
    v_num = shape[0] * shape[1]
    e_num = (shape[0] - 1) * shape[1] + shape[0] * (shape[1] - 1)
    edges = [0] * e_num
    edges_end = 0

    for i in range(shape[0]):
        for j in range(shape[1] - 1):
            v_idx = i * shape[1] + j
            edges[edges_end] = (v_idx, v_idx + 1)
            edges_end += 1

    for j in range(shape[1]):
        for i in range(shape[0] - 1):
            v_idx = i * shape[1] + j
            next_v_idx = (i + 1) * shape[1] + j
            edges[edges_end] = (v_idx, next_v_idx)
            edges_end += 1

    faces_num = (shape[0] - 1) * (shape[1] - 1)
    faces = [0] * faces_num
    face_attrs = list([[] for i in range(v_num)])
    for i in range (shape[0] - 1):
        for j in range(shape[1] - 1):
            f_idx = i * (shape[1] - 1) + j
            faces[f_idx] = str(f_idx)
            v_idxs = [
                i * shape[1] + j,
                i * shape[1] + j + 1,
                (i + 1) * shape[1] + j,
                (i + 1) * shape[1] + j + 1,
            ]
            for v in v_idxs:
                face_attrs[v].append(str(f_idx))


    graph = ig.Graph(n=v_num, graph_attrs={
                "faces": faces,
            },
            vertex_attrs={
                "name": [str(i) for i in range(v_num)],
                "faces": face_attrs,
            },
        edges=edges,
    )

    return graph
    

def create_revolution_graph(line: List[pyrr.Vector3], axis: Axis) -> List[pyrr.Vector3]:
    PIECES_NUM = 360
    ROTATIONS_NUM = PIECES_NUM - 1
    DELTA = (2 * math.pi) / PIECES_NUM

    shape = (len(line), PIECES_NUM)
    graph = get_mesh_graph(shape=shape)
    for i in range(len(line)):
        v_idx = i * shape[1]
        graph.vs[v_idx]["coord"] = line[i]

    angles = np.linspace(0 + DELTA, 2 * math.pi, num=ROTATIONS_NUM, endpoint=False)
    for j, angle in enumerate(angles, start=1):
        rotated_line = rotate_line(line, axis, angle)
        for i, row in enumerate(range(shape[0])):
            v_idx = row * shape[1] + j
            graph.vs[v_idx]["coord"] = rotated_line[i]

    graph["pieces"] = PIECES_NUM

    for i in range(shape[0]):
        s_idx = i * shape[1]
        e_idx = (i + 1) * shape[1] - 1
        graph.add_edge(s_idx, e_idx)

    for i in range(shape[0] - 1):
        v_idxs = [
            i * shape[1],
            (i + 1) * shape[1],
            (i + 1) * shape[1] - 1,
            (i + 2) * shape[1] - 1,
        ]
        new_face = str(int(graph["faces"][-1]) + 1)
        graph["faces"].append(new_face)
        for v in v_idxs:
            graph.vs[v]["faces"].append(new_face)

    return graph
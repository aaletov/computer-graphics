from typing import Callable
import numpy as np
import moderngl as mgl
import pyrr
from .polyhedron import Polyhedron

class CgBaseSolid:
    def __init__(self, ctx: mgl.Context, program: mgl.Program, polyhedron: Polyhedron) -> None:
        raise NotImplementedError()
    
    def render(self, model: pyrr.Matrix44):
        self.prog["model"].write(model.tobytes())
    
class CgLineSolid(CgBaseSolid):
    def __init__(self, ctx: mgl.Context, program: mgl.Program, polyhedron: Polyhedron) -> None:
        self.ctx = ctx
        self.prog = program
        raw_vertices = []
        lines = polyhedron.get_cover_line()
        for line in lines:
            raw_vertices += line
        vertices = np.array(raw_vertices, dtype='f4')

        self.vbo = self.ctx.buffer(vertices.tobytes())
        self.vao = self.ctx.vertex_array(self.prog, [
            (self.vbo, '3f', 'aVertexPosition'),
        ])

    def render(self, model: pyrr.Matrix44) -> None:
        super().render(model)
        self.vao.render(mode=mgl.LINES)
        

class CgDumbSolid(CgBaseSolid):
    def __init__(self, ctx: mgl.Context, program: mgl.Program, polyhedron: Polyhedron) -> None:
        self.ctx = ctx
        self.prog = program
        raw_vertices = []
        triangles = polyhedron.get_cover_triangles()
        for triangle in triangles:
            raw_vertices += [
                *triangle[0],
                *triangle[1],
                *triangle[2],
            ]
        vertices = np.array(raw_vertices, dtype='f4')

        self.vbo = self.ctx.buffer(vertices.tobytes())
        self.vao = self.ctx.vertex_array(self.prog, [
            (self.vbo, '3f', 'aVertexPosition'),
        ])

    def render(self, model: pyrr.Matrix44) -> None:
        super().render(model)
        self.vao.render(mode=mgl.TRIANGLES)
import math
import numpy as np
from pyrr import Matrix44
import moderngl

from .base import WindowBase
from .polyhedron import createDodecahedron, createCube, Polyhedron

from PIL import Image

class CgSolid:
    def __init__(self, ctx: moderngl.Context, program: moderngl.Program, polyhedron: Polyhedron) -> None:
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

    def render(self, x: float) -> None:
        model_matrix = Matrix44.from_translation(np.array([x, 0.0, 0.0]), dtype='f4')
        self.prog["model"].write(model_matrix.tobytes())
        self.vao.render(mode=moderngl.TRIANGLES)


class Hello(WindowBase):
    title = 'Hello Program'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.prog = self.ctx.program(
            vertex_shader='''
                #version 330 core

                in vec3 aVertexPosition;

                uniform mat4 model;
                uniform mat4 vp;

                void main(void) {
                    gl_Position = model * vp * vec4(aVertexPosition, 1.0);
                }
            ''',
            fragment_shader='''
                #version 330 core
                
                void main(void) {
                    gl_FragColor = vec4(1.0, 1.0, 1.0, 1.0);
                }
            ''',
        )

        self.solids = [
            CgSolid(self.ctx, self.prog, createCube()),
            CgSolid(self.ctx, self.prog, createDodecahedron()),
        ]

        # self.fbo = self.ctx.framebuffer(color_attachments=[self.ctx.texture((512, 512), 4)])


    def render(self, time: float, frame_time: float):
        # self.fbo.use()
        self.ctx.enable(moderngl.DEPTH_TEST)
        # self.ctx.clear(color=(0.0, 0.0, 0.0, 1.0))
        self.ctx.clear(0.0, 0.0, 0.0, 0.0)

        fieldOfView = (90 * math.pi) / 180 # in radians
        aspect = self.window_size[0] / self.window_size[1]
        zNear = 0.1
        zFar = 1000.0

        perspective = Matrix44.perspective_projection(fieldOfView, 
                                                            aspect, zNear, zFar, dtype='f4')
        lookat = Matrix44.look_at(
            (20, 20, 150),
            (0.0, 0.0, 0.0),
            (0.0, 1.0, 0.0),
            dtype='f4'
        )

        vp = perspective * lookat
        self.prog["vp"].write(vp.tobytes())

        # self.prog['model'].write(Matrix44.from_eulers((0.0, 0.1, 0.0), dtype='f4'))
        self.solids[0].render(0.0)
        self.solids[1].render(0.5)
        

if __name__ == '__main__':
    Hello.run()

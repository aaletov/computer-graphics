from typing import List, Callable

import math
import numpy as np
import pyrr
import moderngl as mgl

from .base import WindowBase
from .solid import Solid, createDodecahedron, createCube

class SimpleVertexScene(WindowBase):
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

        self.solids: List[BaseModel] = [
            LineModel(self.ctx, self.prog, createCube()),
            LineModel(self.ctx, self.prog, createDodecahedron()),
            DumbModel(self.ctx, self.prog, createCube()),
            DumbModel(self.ctx, self.prog, createDodecahedron()),
        ]

        # self.fbo = self.ctx.framebuffer(color_attachments=[self.ctx.texture((512, 512), 4)])


    def render(self, time: float, frame_time: float):
        # self.fbo.use()
        self.ctx.enable(mgl.DEPTH_TEST)
        # self.ctx.clear(color=(0.0, 0.0, 0.0, 1.0))
        self.ctx.clear(0.0, 0.0, 0.0, 0.0)

        fieldOfView = (90 * math.pi) / 180 # in radians
        aspect = self.window_size[0] / self.window_size[1]
        zNear = 0.1
        zFar = 1000.0

        perspective = pyrr.Matrix44.perspective_projection(fieldOfView, 
                                                            aspect, zNear, zFar, dtype='f4')
        lookat = pyrr.Matrix44.look_at(
            (20, 20, 150),
            (0.0, 0.0, 0.0),
            (0.0, 1.0, 0.0),
            dtype='f4'
        )

        vp = perspective * lookat
        self.prog["vp"].write(vp.tobytes())

        for solid, x in zip(self.solids, np.linspace(-0.75, 0.75, len(self.solids))):
            model = pyrr.Matrix44.from_translation(np.array([x, 0.0, 0.0]), dtype='f4')
            solid.render(model)

class BaseModel:
    def __init__(self, ctx: mgl.Context, program: mgl.Program, solid: Solid) -> None:
        raise NotImplementedError()
    
    def render(self, model: pyrr.Matrix44):
        self.prog["model"].write(model.tobytes())
    
class LineModel(BaseModel):
    def __init__(self, ctx: mgl.Context, program: mgl.Program, solid: Solid) -> None:
        self.ctx = ctx
        self.prog = program

        vertices = solid.get_cover_line()

        self.vbo = self.ctx.buffer(vertices.astype('f4').tobytes())
        self.vao = self.ctx.vertex_array(self.prog, [
            (self.vbo, '3f', 'aVertexPosition'),
        ])

    def render(self, model: pyrr.Matrix44) -> None:
        super().render(model)
        self.vao.render(mode=mgl.LINES)
        

class DumbModel(BaseModel):
    def __init__(self, ctx: mgl.Context, program: mgl.Program, solid: Solid) -> None:
        self.ctx = ctx
        self.prog = program

        vertices = solid.get_cover_triangles()

        self.vbo = self.ctx.buffer(vertices.astype('f4').tobytes())
        self.vao = self.ctx.vertex_array(self.prog, [
            (self.vbo, '3f', 'aVertexPosition'),
        ])

    def render(self, model: pyrr.Matrix44) -> None:
        super().render(model)
        self.vao.render(mode=mgl.TRIANGLES)
        

if __name__ == '__main__':
    Scene.run()

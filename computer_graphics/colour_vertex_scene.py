from typing import List, Callable

import math
import numpy as np
import pyrr
import moderngl as mgl

from .base import WindowBase
from .solid import Solid, createDodecahedron, createCube

class ColorVertexScene(WindowBase):
    title = 'Hello Program'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.prog = self.ctx.program(
            vertex_shader='''
                #version 330 core

                in vec3 aVertexPosition;
                in vec4 aVertexColor;

                uniform mat4 model;
                uniform mat4 vp;

                varying lowp vec4 vColor;

                void main(void) {
                    gl_Position = model * vp * vec4(aVertexPosition, 1.0);
                    vColor = aVertexColor;
                }
            ''',
            fragment_shader='''
                #version 330 core

                varying lowp vec4 vColor;
                
                void main(void) {
                    gl_FragColor = vColor;
                }
            ''',
        )

        self.models: List[BaseModel] = [
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

        for model, x in zip(self.models, np.linspace(-0.5, 0.5, len(self.models))):
            model_matrix = pyrr.Matrix44.from_translation(np.array([x, 0.0, 0.0]), dtype='f4')
            model.render(model_matrix)

class BaseModel:
    def __init__(self, ctx: mgl.Context, program: mgl.Program, solid: Solid) -> None:
        raise NotImplementedError()
    
    def render(self, model: pyrr.Matrix44):
        self.prog["model"].write(model.tobytes())
    
class DumbModel(BaseModel):
    def __init__(self, ctx: mgl.Context, program: mgl.Program, solid: Solid) -> None:
        self.ctx = ctx
        self.prog = program

        vertices = solid.get_vertices()
        indexes = solid.get_cover_triangles_idx()
        f = lambda x: (0.1, 0.1, 0.1, 0.5) if x % 2 == 0 else (0.75, 0.09, 0.03, 0.5)
        colors = np.array([f(i) for i in range(indexes.shape[0])])

        self.vbo = self.ctx.buffer(vertices.astype('f4').tobytes())
        self.cbo = self.ctx.buffer(colors.astype('f4').tobytes())
        self.ibo = self.ctx.buffer(indexes.astype('u2').tobytes())
        self.vao = self.ctx.vertex_array(self.prog, [
                (self.vbo, '3f', 'aVertexPosition'),
                (self.cbo, '4f', 'aVertexColor'),
            ],
            index_buffer=self.ibo,
            index_element_size=2,
        )

    def render(self, model: pyrr.Matrix44) -> None:
        super().render(model)
        self.vao.render(mode=mgl.TRIANGLES)
        

if __name__ == '__main__':
    ColorVertexScene.run()

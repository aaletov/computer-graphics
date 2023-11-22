from typing import List, Callable

import math
import numpy as np
import pyrr
import moderngl as mgl

from .base import WindowBase
from .solid import Solid, createDodecahedron, createCube

class MovingScene(WindowBase):
    title = 'Hello Program'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.prog = self.ctx.program(
            vertex_shader='''
                #version 330 core

                in vec3 aVertexPosition;
                in vec4 vColor;

                uniform mat4 model;
                uniform mat4 vp;

                out vec4 fColor;

                void main(void) {
                    gl_Position = vp * model * vec4(aVertexPosition, 1.0);
                    fColor = vColor;
                }
            ''',
            fragment_shader='''
                #version 330 core
                
                in vec4 fColor;

                void main(void) {
                    gl_FragColor = fColor;
                }
            ''',
        )

        self.models: List[MovingModel] = [
            MovingModel(self.ctx, self.prog, createCube(), [4, 0, 1] * 8),
        ]

    def render(self, time: float, frame_time: float):
        self.ctx.enable(mgl.DEPTH_TEST)
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
        model = pyrr.Matrix44.from_translation(np.array([0.0, 0.0, 0.0]), dtype='f4')
        self.prog["model"].write(model.tobytes())

        # rot = pyrr.Matrix44.from_x_rotation(time % (2 * math.pi), dtype='f4')
        # for model, x in zip(self.models, np.linspace(-0.75, 0.75, len(self.models))):
        #     trans = pyrr.Matrix44.from_translation(np.array([x, 0.0, 0.0]), dtype='f4')
        #     model.render(trans * rot)
        # self.models[0].roll(0, 1, math.pi / 180)
        self.models[0].render()

class MovingModel:
    def __init__(self, ctx: mgl.Context, program: mgl.Program, solid: Solid, rolls: List[int]) -> None:
        self.ctx = ctx
        self.prog = program
        self.solid = solid
        self.rolls = rolls
        self.roll_idx = 0
        self.roll_angle = 0

        vertices = solid.get_cover_triangles()
        f = lambda x: (0.1, 0.1, 0.1, 0.5) if x % 2 == 0 else (0.75, 0.09, 0.03, 0.5)
        colors = np.array([f(i) for i in range(vertices.shape[0])])

        self.vbo = self.ctx.buffer(vertices.astype('f4').tobytes(), dynamic=True)

        self.cbo = self.ctx.buffer(colors.astype('f4').tobytes())
        
        self.vao = self.ctx.vertex_array(self.prog, [
            (self.vbo, '3f', 'aVertexPosition'),
            (self.cbo, '4f', 'vColor')
            ],
        )

    def roll(self, lface: int, rface: int, angle: float) -> None:
        lv_idx, rv_idx = self.solid.get_common_edge(lface, rface)
        pos = self.solid.graph.vs[lv_idx]["coord"]
        rnormal = self.solid.get_face_normal(rface)
        rnormal[1] = 0.0
        k = np.array([0.0, 0.0, -1.0], dtype='f4')
        ang = self.solid.clockwise_angle(k, rnormal)

        trans = pyrr.Matrix44.from_translation(pos, dtype='f4')
        backtrans = pyrr.Matrix44.from_translation(-pos, dtype='f4')
        rot = pyrr.Matrix44.from_y_rotation(ang, dtype='f4')
        backrot = pyrr.Matrix44.from_y_rotation(-ang, dtype='f4')

        self.solid.transform(backrot * backtrans)
        self.solid.transform(pyrr.Matrix44.from_x_rotation(angle, dtype='f4'))
        self.solid.transform(trans * rot)
        return

    def render(self) -> None:
        self.vbo.clear()
        if self.roll_angle >= (math.pi / 2):
            self.roll_idx += 1
            self.roll_angle = 0
        self.roll(self.rolls[self.roll_idx], self.rolls[self.roll_idx + 1], math.pi / 30)
        self.roll_angle += math.pi / 30

        self.vbo.write(self.solid.get_cover_triangles().astype('f4').tobytes(), offset=0)
        self.vao.render(mode=mgl.TRIANGLES)
        

if __name__ == '__main__':
    MovingScene.run()

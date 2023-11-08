from typing import List

import math
import numpy as np
import pyrr
import moderngl

from .base import WindowBase
from .polyhedron import createDodecahedron, createCube, Polyhedron
from .cgsolid import CgLineSolid, CgDumbSolid, CgBaseSolid

from PIL import Image


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

        self.solids: List[CgBaseSolid] = [
            CgLineSolid(self.ctx, self.prog, createCube()),
            CgLineSolid(self.ctx, self.prog, createDodecahedron()),
            CgDumbSolid(self.ctx, self.prog, createCube()),
            CgDumbSolid(self.ctx, self.prog, createDodecahedron()),
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
        

if __name__ == '__main__':
    Hello.run()

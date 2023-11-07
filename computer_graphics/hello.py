import math
import numpy as np
from pyrr import Matrix44
import moderngl

import computer_graphics.base as base

from PIL import Image


class Hello(base.WindowBase):
    title = 'Hello Program'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.prog = self.ctx.program(
            vertex_shader='''
                #version 330 core

                in vec3 aVertexPosition;

                uniform mat4 mvp;

                void main(void) {
                    gl_Position = mvp * vec4(aVertexPosition, 1.0);
                }
            ''',
            fragment_shader='''
                #version 330 core
                
                void main(void) {
                    gl_FragColor = vec4(1.0, 1.0, 1.0, 1.0);
                }
            ''',
        )

        vertices = np.array([
            -1.0, -1.0, 0.0,
            -1.0, 1.0, 0.0,
            1.0, 1.0, 0.0,
            -1.0, -1.0, 0.0,
            -1.0, 1.0, 0.0,
            1.0, 1.0, 0.0,
            -1.0, -1.0, 0.0,
            -1.0, 1.0, 0.0,
            1.0, 1.0, 0.0,
            -1.0, -1.0, 0.0,
            -1.0, 1.0, 0.0,
            1.0, 1.0, 0.0,
            -1.0, -1.0, 0.0,
            -1.0, 1.0, 0.0,
            1.0, 1.0, 0.0,
            -1.0, -1.0, 0.0,
            -1.0, 1.0, 0.0,
            1.0, 1.0, 0.0,
            -1.0, -1.0, 0.0,
            -1.0, 1.0, 0.0,
            1.0, 1.0, 0.0,
            # 1.0, -1.0, 0.0,
            # -1.0, -1.0, 0.0,
        ], dtype='f4')

        self.vbo = self.ctx.buffer(vertices.tobytes())
        self.vao = self.ctx.vertex_array(self.prog, [
            (self.vbo, '3f', 'aVertexPosition'),
        ])

        # self.fbo = self.ctx.framebuffer(color_attachments=[self.ctx.texture((512, 512), 4)])


    def render(self, time: float, frame_time: float):
        # self.fbo.use()
        self.ctx.enable(moderngl.DEPTH_TEST)
        # self.ctx.clear(color=(0.0, 0.0, 0.0, 1.0))
        self.ctx.clear(0.0, 0.0, 0.0, 0.0)

        fieldOfView = (90 * math.pi) / 180 # in radians
        aspect = self.window_size[0] / self.window_size[1]
        zNear = 0.1
        zFar = 100.0

        perspective = Matrix44.perspective_projection(fieldOfView, 
                                                            aspect, zNear, zFar, dtype='f4')
        lookat = Matrix44.look_at(
            (4, 3, 2),
            (0.0, 0.0, 0.0),
            (0.0, 1.0, 0.0),
            dtype='f4'
        )

        mvp = perspective * lookat
        model_view_matrix = Matrix44()
        model_view_matrix.from_translation(np.array([0.0, 0.0, 0.0], dtype='f4'))
        self.prog["mvp"].write(mvp.tobytes())

        # self.prog['model'].write(Matrix44.from_eulers((0.0, 0.1, 0.0), dtype='f4'))
        self.vao.render(mode=moderngl.TRIANGLES)
        

if __name__ == '__main__':
    Hello.run()

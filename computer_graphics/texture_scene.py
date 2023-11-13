from typing import List, Callable, Tuple

import math
import numpy as np
import pyrr
import moderngl as mgl

from .base import WindowBase
from .solid import Solid, createDodecahedron, createCube, createTetrahedron

class TextureScene(WindowBase):
    title = 'Hello Program'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.prog = self.ctx.program(
            vertex_shader='''
                #version 330 core

                in vec3 aVertexPosition;
                in vec4 aVertexColor;
                in vec2 in_texcoord_0;

                uniform mat4 model;
                uniform mat4 vp;
                uniform mat4 rot;

                varying lowp vec4 vColor;

                out vec2 v_text;

                void main(void) {
                    gl_Position = model * vp * rot * vec4(aVertexPosition, 1.0);
                    vColor = aVertexColor;
                    v_text = in_texcoord_0;
                }
            ''',
            fragment_shader='''
                #version 330 core

                uniform sampler2D Texture;
                in vec2 v_text;

                out vec4 f_color;
                
                void main(void) {
                    f_color = vec4(texture(Texture, v_text).rgb * 1.0, 1.0);
                }
            ''',
        )

        tt_vertex_tex = [
            0.0, 0.0,
            0.5, 1.0,
            1.0, 0.0,
        ]

        cube_vertex_tex = [
            0.0, 0.0, # 0
            0.0, 1.0, # 1
            1.0, 1.0, # 2
            1.0, 0.0, # 3
        ]

        dd_vertex_tex = np.array([
            0.79, 0.1, # 0
            0.98, 0.65, # 1
            0.5, 1.0, # 2
            0.02, 0.65, # 3
            0.2, 0.1, # 4
        ], dtype='f4')

        self.models: List[BaseModel] = [
            DumbModel(self.ctx, self.prog, createTetrahedron(), tt_vertex_tex),
            DumbModel(self.ctx, self.prog, createCube(), cube_vertex_tex),
            DumbModel(self.ctx, self.prog, createDodecahedron(), dd_vertex_tex),
        ]

        # self.fbo = self.ctx.framebuffer(color_attachments=[self.ctx.texture((512, 512), 4)])
        self.texture = self.load_texture_2d('/home/aaletov/uni/7sem/computer-graphics/cm.jpg')
        print(self.texture.size)

    def render(self, time: float, frame_time: float):
        # self.fbo.use()
        self.ctx.enable(mgl.DEPTH_TEST)
        # self.ctx.clear(color=(0.0, 0.0, 0.0, 1.0))
        self.ctx.clear(0.0, 0.0, 0.0, 0.0, 1.0)

        fieldOfView = (90 * math.pi) / 180 # in radians
        aspect = self.window_size[0] / self.window_size[1]
        zNear = 0.1
        zFar = 1000.0

        # perspective = pyrr.Matrix44.orthogonal_projection(-1.0, 1.0, -1.0, 1.0,
                                                        #   zNear, zFar, dtype='f4')
        perspective = pyrr.Matrix44.perspective_projection(fieldOfView, aspect,
                                                           zNear, zFar, dtype='f4')
        lookat = pyrr.Matrix44.look_at(
            (30, 30, 180),
            (0.0, 0.0, 0.0),
            (0.0, 1.0, 0.0),
            dtype='f4'
        )
        
        vp = perspective * lookat
        self.prog["vp"].write(vp.tobytes())

        self.texture.use()

        self.prog["rot"].write(pyrr.Matrix44.from_x_rotation(time, dtype='f4').tobytes())
        for model, x in zip(self.models, np.linspace(-0.5, 0.5, len(self.models))):
            model_matrix = pyrr.Matrix44.from_translation(np.array([x, 0.0, -1.9]), dtype='f4')
            model.render(model_matrix)

class BaseModel:
    def __init__(self, ctx: mgl.Context, program: mgl.Program, solid: Solid) -> None:
        raise NotImplementedError()
    
    def render(self, model: pyrr.Matrix44):
        self.prog["model"].write(model.tobytes())
    
class DumbModel(BaseModel):
    def __init__(self, ctx: mgl.Context, program: mgl.Program, solid: Solid, texmap: List[Tuple[int, int]]) -> None:
        self.ctx = ctx
        self.prog = program

        vertices = solid.get_cover_triangles()
        f = lambda x: (0.1, 0.1, 0.1, 0.5) if x % 2 == 0 else (0.75, 0.09, 0.03, 0.5)
        # colors = np.array([f(i) for i in range(indexes.shape[0])])
        tex_indexes = solid.sgraph.get_cover_triangles_tex()

        tex_coords = [(texmap[2 * i], texmap[2 * i + 1]) for i in tex_indexes]
        tex = np.array(tex_coords, dtype="f4").flatten()

        self.vbo = self.ctx.buffer(vertices.astype('f4').tobytes())
        self.tbo = self.ctx.buffer(tex.astype('f4').tobytes())

        self.vao = self.ctx.vertex_array(self.prog, [
                (self.vbo, '3f', 'aVertexPosition'),
                (self.tbo, '2f', 'in_texcoord_0')
            ],
        )

    def render(self, model: pyrr.Matrix44) -> None:
        super().render(model)
        self.vao.render(mode=mgl.TRIANGLES)
        

if __name__ == '__main__':
    TextureScene.run()

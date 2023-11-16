from typing import List, Callable

import math
import numpy as np
import pyrr
import moderngl as mgl

from .base import WindowBase
from .solid import Solid, createDodecahedron, createCube

class LightScene(WindowBase):
    title = 'Hello Program'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.prog = self.ctx.program(
            vertex_shader='''
                #version 330 core

                in vec3 aVertexPosition;
                in vec3 aObjectColor;
                in vec3 aNormal;

                uniform mat4 model;
                uniform mat4 vp;
                uniform mat4 rot;

                out vec3 fObjectColor;
                out vec3 Normal;
                out vec3 FragPos; 

                void main(void) {
                    gl_Position = model * vp * rot * vec4(aVertexPosition, 1.0);
                    FragPos = vec3(model * rot * vec4(aVertexPosition, 1.0));
                    fObjectColor = aObjectColor;
                    Normal = aNormal;
                }
            ''',
            fragment_shader='''
                #version 330 core

                uniform vec3 lightColor;
                uniform vec3 lightPos;
                
                in vec3 fObjectColor;
                in vec3 Normal;
                in vec3 FragPos; 

                out vec4 FragColor;

                void main()
                {
                    float ambientStrength = 0.5;
                    vec3 ambient = ambientStrength * lightColor;
                    vec3 norm = normalize(Normal);
                    vec3 lightDir = normalize(lightPos - FragPos);
                    float diff = max(dot(norm, lightDir), 0.0);
                    vec3 diffuse = diff * lightColor;

                    vec3 result = (ambient + diffuse) * fObjectColor;
                    FragColor = vec4(result, 1.0);
                }  
            ''',
        )

        self.models: List[BaseModel] = [
            DumbModel(self.ctx, self.prog, createCube()),
            DumbModel(self.ctx, self.prog, createDodecahedron()),
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
        self.prog["lightColor"].write(np.array([1.0, 1.0, 1.0, 1.0], dtype='f4').tobytes())
        self.prog["lightPos"].write(np.array([0.0, 1.0, 1.0, 1.0], dtype='f4').tobytes())

        self.prog["rot"].write(pyrr.Matrix44.from_x_rotation(time, dtype='f4').tobytes())
        for model, x in zip(self.models, np.linspace(-0.5, 0.5, len(self.models))):
            model_matrix = pyrr.Matrix44.from_translation(np.array([x, 0.0, -1.0]), dtype='f4')
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

        vertices = solid.get_cover_triangles()
        f = lambda x: (0.75, 0.09, 0.03)
        colors = np.array([f(i) for i in range(vertices.shape[0] // 3)]).flatten()
        normales = solid.get_normales()

        self.vbo = self.ctx.buffer(vertices.astype('f4').tobytes())
        self.cbo = self.ctx.buffer(colors.astype('f4').tobytes())
        self.nbo = self.ctx.buffer(normales.astype('f4').tobytes())
        self.vao = self.ctx.vertex_array(self.prog, [
                (self.vbo, '3f', 'aVertexPosition'),
                (self.cbo, '3f', 'aObjectColor'),
                (self.nbo, '3f', 'aNormal'),
            ],
        )

    def render(self, model: pyrr.Matrix44) -> None:
        super().render(model)
        self.vao.render(mode=mgl.TRIANGLES)
        

if __name__ == '__main__':
    LightScene.run()

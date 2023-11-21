from typing import List, Callable, Dict, Any

import math
import struct
import numpy as np
import pyrr
import moderngl as mgl

from .base import WindowBase
from .solid import Solid, createCone, createDodecahedron, createCube
from .material import Material, BLACK_RUBBER, GOLD, RED_PLASTIC, PEARL_GLASS, SHINY_GOLD

class MaterialScene(WindowBase):
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

                out vec3 Normal;
                out vec3 FragPos; 

                void main(void) {
                    gl_Position = vp * model * vec4(aVertexPosition, 1.0);
                    FragPos = vec3(model * vec4(aVertexPosition, 1.0));
                    Normal = mat3(transpose(inverse(model))) * aNormal; 
                }
            ''',
            fragment_shader='''
                #version 330 core

                struct Material {
                    vec3 ambient;
                    vec3 diffuse;
                    vec3 specular;
                    float shininess;
                    float transparency;
                }; 
                
                uniform Material material;

                struct Light {
                    vec3 position;
                
                    vec3 ambient;
                    vec3 diffuse;
                    vec3 specular;
                };

                uniform Light light;  

                uniform vec3 viewPos;
                
                in vec3 Normal;
                in vec3 FragPos; 

                out vec4 FragColor;

                void main()
                {
                    vec3 ambient = light.ambient * material.ambient;

                    vec3 norm = normalize(Normal);
                    vec3 lightDir = normalize(light.position - FragPos);

                    float diff = max(dot(norm, lightDir), 0.0);
                    vec3 diffuse = light.diffuse * (diff * material.diffuse);

                    vec3 viewDir = normalize(viewPos - FragPos);
                    vec3 reflectDir = reflect(-lightDir, norm);
                    float spec = pow(max(dot(viewDir, reflectDir), 0.0), material.shininess);
                    vec3 specular = light.specular * (spec * material.specular);

                    vec3 result = ambient + diffuse + specular;
                    FragColor = vec4(result, material.transparency);
                }  
            ''',
        )

        self.models: List[BaseModel] = [
            DumbModel(self.ctx, self.prog, createCone(), SHINY_GOLD),
            DumbModel(self.ctx, self.prog, createCube(), PEARL_GLASS),
            DumbModel(self.ctx, self.prog, createDodecahedron(), BLACK_RUBBER),
        ]

        self.room = DumbModel(self.ctx, self.prog, createCube(), RED_PLASTIC)


    def render(self, time: float, frame_time: float):
        self.ctx.enable(mgl.DEPTH_TEST)
        self.ctx.enable(mgl.BLEND)

        self.ctx.clear(0.0, 0.0, 0.0, 0.0)

        fieldOfView = (90 * math.pi) / 180 # in radians
        aspect = self.window_size[0] / self.window_size[1]
        zNear = 0.1
        zFar = 1000.0

        perspective = pyrr.Matrix44.perspective_projection(fieldOfView, 
                                                            aspect, zNear, zFar, dtype='f4')
        
        cameraPos = (0, 200, 200)
        lookat = pyrr.Matrix44.look_at(
            cameraPos,
            (0.0, 0.0, 0.0),
            (0.0, 1.0, 0.0),
            dtype='f4'
        )

        vp = perspective * lookat
        self.prog["vp"].write(vp.tobytes())
        self.prog["viewPos"].write(np.array(cameraPos, dtype='f4').tobytes())


        def new_light_source(position: pyrr.Vector3,
                ambient: pyrr.Vector3,
                diffuse: pyrr.Vector3,
                specular: pyrr.Vector3) -> Dict[str, bytes]:
            return [
                struct.pack("3f", *tuple(position)),
                struct.pack("3f", *tuple(ambient)),
                struct.pack("3f", *tuple(diffuse)),
                struct.pack("3f", *tuple(specular)),
            ]
        
        def write_light_source(material: List[bytes]) -> None:
            self.prog["light.position"].write(material[0])
            self.prog["light.ambient"].write(material[1])
            self.prog["light.diffuse"].write(material[2])
            self.prog["light.specular"].write(material[3])

        light = new_light_source(
            (0.0, 20.0, 20.0),
            (0.2, 0.2, 0.2),
            (0.5, 0.5, 0.5),
            (0.9, 0.9, 0.9),
        )

        write_light_source(light)
        room_scale = pyrr.Matrix44.from_scale(np.array([50.0, 50.0, 50.0]), dtype='f4')
        room_trans = pyrr.Matrix44.from_translation(np.array([0.0, -30.0, 0.0]), dtype='f4')
        self.room.render(room_trans * room_scale)

        rotY = pyrr.Matrix44.from_y_rotation(time % (2 * math.pi), dtype='f4')
        rot = rotY * pyrr.Matrix44.from_z_rotation(time % (2 * math.pi), dtype='f4')
        for model, x in zip(self.models, np.linspace(-3.0, 3.0, len(self.models))):
            trans = pyrr.Matrix44.from_translation(np.array([x, 0.0, -1.0]), dtype='f4')
            model_matrix = trans * rot
            model.render(model_matrix)

class BaseModel:
    def __init__(self, ctx: mgl.Context, program: mgl.Program, solid: Solid) -> None:
        raise NotImplementedError()
    
    def render(self, model: pyrr.Matrix44):
        self.prog["model"].write(model.tobytes())
    
class DumbModel(BaseModel):
    def __init__(self, ctx: mgl.Context, program: mgl.Program, solid: Solid, material: Material) -> None:
        self.ctx = ctx
        self.prog = program
        self.material = material

        vertices = solid.get_cover_triangles()
        normales = solid.get_normales_repeated()

        self.vbo = self.ctx.buffer(vertices.astype('f4').tobytes())
        self.nbo = self.ctx.buffer(normales.astype('f4').tobytes())

        self.vao = self.ctx.vertex_array(self.prog, [
                (self.vbo, '3f', 'aVertexPosition'),
                (self.nbo, '3f', 'aNormal'),
            ],
        )

    def render(self, model: pyrr.Matrix44) -> None:
        super().render(model)
        self.write_material()
        self.vao.render(mode=mgl.TRIANGLES)

    def write_material(self):
        keys = [
            "material.ambient",
            "material.diffuse",
            "material.specular",
            "material.shininess",
            "material.transparency",
        ]
        values = [
            struct.pack("3f", *tuple(self.material.ambient)),
            struct.pack("3f", *tuple(self.material.diffuse)),
            struct.pack("3f", *tuple(self.material.specular)),
            struct.pack("f", self.material.shininess),
            struct.pack("f", self.material.transparency),
        ]
        for k, v in zip(keys, values):
            self.prog[k].write(v)

if __name__ == '__main__':
    MaterialScene.run()

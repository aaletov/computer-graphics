from typing import List, Callable, Dict, Any

import math
import struct
import numpy as np
import pyrr
import moderngl as mgl

from .base import WindowBase
from .solid import Solid, createCone, createDodecahedron, createCube
from .material import Material, SHINY_GOLD, DIM_PEARL, DIM_PEARL_GLASS, DIM_SILVER

class AdvancedMovingScene(WindowBase):
    title = 'Hello Program'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.prog = self.ctx.program(
            vertex_shader='''
                #version 330 core

                in vec3 aVertexPosition;
                in vec3 aObjectColor;
                in vec3 aNormal;
                in vec2 in_texcoord_0;

                uniform mat4 model;
                uniform mat4 vp;

                out vec3 Normal;
                out vec3 FragPos;
                out vec2 v_text;

                void main(void) {
                    gl_Position = vp * model * vec4(aVertexPosition, 1.0);
                    FragPos = vec3(model * vec4(aVertexPosition, 1.0));
                    Normal = mat3(transpose(inverse(model))) * aNormal;
                    v_text = in_texcoord_0;
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

                uniform sampler2D Texture;
                in vec2 v_text;

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
                    FragColor = vec4(texture(Texture, v_text).rgb * result, material.transparency);
                }  
            ''',
        )

        texture = self.load_texture_2d('/home/aaletov/uni/7sem/computer-graphics/cm.jpg')

        dd_texmap = np.array([
            0.79, 0.1, # 0
            0.98, 0.65, # 1
            0.5, 1.0, # 2
            0.02, 0.65, # 3
            0.2, 0.1, # 4
        ], dtype='f4')

        self.models: List[BaseModel] = [
            DumbModel(self.ctx, self.prog, createCone(), SHINY_GOLD),
            DumbModel(self.ctx, self.prog, createCube(), DIM_PEARL_GLASS),
            DumbModel(self.ctx, self.prog, createDodecahedron(), DIM_PEARL, texture, dd_texmap),
        ]

        self.back = DumbModel(self.ctx, self.prog, createCube(), DIM_SILVER)
        self.floor = DumbModel(self.ctx, self.prog, createCube(), DIM_SILVER)


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
        
        cameraPos = (0, 100, 200)
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

        def get_light_position(phi: float) -> np.ndarray:
            r = 1.0
            return np.array((
                r * np.cos(phi),
                1.0,
                r * np.sin(phi),
            ), dtype='f4')

        light = new_light_source(
            get_light_position(time % (2 * math.pi)),
            (1.0, 1.0, 1.0),
            (0.9, 0.9, 0.9),
            (0.9, 0.9, 0.9),
        )

        write_light_source(light)
        back_scale = pyrr.Matrix44.from_scale(np.array([50.0, 50.0, 1.0]), dtype='f4')
        back_trans = pyrr.Matrix44.from_translation(np.array([0.0, 25.0, -5.0]), dtype='f4')
        self.back.render(back_trans * back_scale)
        floor_scale = pyrr.Matrix44.from_scale(np.array([50.0, 50.0, 50.0]), dtype='f4')
        floor_trans = pyrr.Matrix44.from_translation(np.array([0.0, -30.0, 0.0]), dtype='f4')
        self.floor.render(floor_trans * floor_scale)

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
    def __init__(self, ctx: mgl.Context, program: mgl.Program, solid: Solid,
                 material: Material, texture: mgl.Texture | None = None,
                 texmap: np.ndarray | None = None) -> None:
        self.ctx = ctx
        self.prog = program
        self.material = material
        self.texture = texture

        vertices = solid.get_cover_triangles()
        normales = solid.get_normales_repeated()

        self.vbo = self.ctx.buffer(vertices.astype('f4').tobytes())
        self.nbo = self.ctx.buffer(normales.astype('f4').tobytes())

        vao_args = [
            (self.vbo, '3f', 'aVertexPosition'),
            (self.nbo, '3f', 'aNormal'),
        ]

        if texmap is not None:
            tex_indexes = solid.get_cover_triangles_tex()
            tex_coords = [(texmap[2 * i], texmap[2 * i + 1]) for i in tex_indexes]
            tex = np.array(tex_coords, dtype="f4").flatten()
            self.tbo = self.ctx.buffer(tex.astype('f4').tobytes())
            vao_args.append((self.tbo, '2f', 'in_texcoord_0'))

        self.vao = self.ctx.vertex_array(self.prog, vao_args)

    def render(self, model: pyrr.Matrix44) -> None:
        super().render(model)
        self.write_material()
        if self.texture is not None:
            self.texture.use()
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
    AdvancedMovingScene.run()

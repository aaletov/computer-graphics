from typing import List, Callable, Dict, Any

import math
import struct
import numpy as np
import pyrr
import moderngl as mgl

from .base import WindowBase
from .solid import Solid, createCone, createDodecahedron, createCube
from .material import Material, SHINY_GOLD, DIM_PEARL, DIM_PEARL_GLASS, SILVER

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

        texture = self.load_texture_2d('/home/aaletov/uni/7sem/computer-graphics/texture.png')
        floortex = self.load_texture_2d('/home/aaletov/uni/7sem/computer-graphics/grass.jpg')

        dd_texmap = np.array([
            0.79, 0.1, # 0
            0.98, 0.65, # 1
            0.5, 1.0, # 2
            0.02, 0.65, # 3
            0.2, 0.1, # 4
        ], dtype='f4')

        cube_vertex_tex = np.array([
            0.0, 0.0, # 0
            0.0, 50.0, # 1
            50.0, 50.0, # 2
            50.0, 0.0, # 3
        ], dtype='f4')


        ddh = createDodecahedron()
        ddh.transform(pyrr.Matrix44.from_z_rotation(math.acos(-1 / math.sqrt(5)) / 2, dtype='f4'))
        ddh.transform(pyrr.Matrix44.from_translation(np.array([0.0, 0.79465445, 0.0]), dtype='f4'))

        self.model = MovingModel(self.ctx, self.prog, ddh, [1] + [10, 7, 0, 4, 8] * 100,
                                 DIM_PEARL, texture, dd_texmap)

        self.back = DumbModel(self.ctx, self.prog, createCube(), SILVER)
        self.floor = DumbModel(self.ctx, self.prog, createCube(), SILVER, floortex, cube_vertex_tex)


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
        
        cameraPos = (1, 50, 200)
        lookat = pyrr.Matrix44.look_at(
            cameraPos,
            (1.0, 0.0, 0.0),
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
            (0.0, 10.0, 1.0),
            (1.0, 1.0, 1.0),
            (0.9, 0.9, 0.9),
            (0.9, 0.9, 0.9),
        )

        write_light_source(light)
        back_scale = pyrr.Matrix44.from_scale(np.array([50.0, 50.0, 1.0]), dtype='f4')
        back_trans = pyrr.Matrix44.from_translation(np.array([0.0, 25.0, -5.0]), dtype='f4')
        self.back.render(back_trans * back_scale)
        floor_scale = pyrr.Matrix44.from_scale(np.array([50.0, 50.0, 50.0]), dtype='f4')
        floor_trans = pyrr.Matrix44.from_translation(np.array([0.0, -50 * 0.57735027, 0.0]), dtype='f4')
        self.floor.render(floor_trans * floor_scale)

        model = pyrr.Matrix44.from_translation(np.array([0.0, 0.0, 0.0]), dtype='f4')
        self.prog["model"].write(model.tobytes())
        self.model.render()

class MovingModel:
    def __init__(self, ctx: mgl.Context, program: mgl.Program, solid: Solid, rolls: List[int], 
                 material: Material, texture: mgl.Texture | None = None,
                 texmap: np.ndarray | None = None) -> None:
        self.ctx = ctx
        self.prog = program
        self.solid = solid
        self.rolls = rolls
        self.roll_idx = 0
        self.roll_angle = 0
        self.material = material
        self.texture = texture
        self.rnormal: np.ndarray | None = None
        quad = np.array(np.linspace(0.0, 2.0, num=15)**2)
        full_angle = math.pi - math.acos(-1 / math.sqrt(5))
        self.move = (quad * (full_angle / np.sum(quad))).tolist()

        vertices = solid.get_cover_triangles()
        normales = solid.get_normales_repeated()

        self.vbo = self.ctx.buffer(vertices.astype('f4').tobytes(), dynamic=True)
        self.nbo = self.ctx.buffer(normales.astype('f4').tobytes(), dynamic=True)

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

    def roll(self, lface: int, rface: int, angle: float) -> None:
        lv_idx, rv_idx = self.solid.get_common_edge(lface, rface)
        pos = self.solid.graph.vs[lv_idx]["coord"]
        if self.rnormal is None:
            self.rnormal = self.solid.get_face_normal(rface)
            self.rnormal[1] = 0.0
        k = np.array([0.0, 0.0, -1.0], dtype='f4')
        ang = self.solid.clockwise_angle(k, self.rnormal)

        trans = pyrr.Matrix44.from_translation(pos, dtype='f4')
        backtrans = pyrr.Matrix44.from_translation(-pos, dtype='f4')
        rot = pyrr.Matrix44.from_y_rotation(ang, dtype='f4')
        backrot = pyrr.Matrix44.from_y_rotation(-ang, dtype='f4')

        self.solid.transform(backrot * backtrans)
        self.solid.transform(pyrr.Matrix44.from_x_rotation(angle, dtype='f4'))
        self.solid.transform(trans * rot)
        return

    def render(self) -> None:
        self.write_material()
        if self.texture is not None:
            self.texture.use()
        self.vbo.clear()
        self.nbo.clear()
        full_angle = math.pi - math.acos(-1 / math.sqrt(5))
        if np.allclose(self.roll_angle, full_angle, rtol=1e-2) or (self.roll_angle >= full_angle):
            self.roll_idx += 1
            self.roll_angle = 0
            self.rnormal = None
        step = self.move.pop(0)
        self.roll(self.rolls[self.roll_idx], self.rolls[self.roll_idx + 1], step)
        self.roll_angle += step
        self.move.append(step)

        self.vbo.write(self.solid.get_cover_triangles().astype('f4').tobytes(), offset=0)
        self.nbo.write(self.solid.get_normales_repeated().astype('f4').tobytes(), offset=0)

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

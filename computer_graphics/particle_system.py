from typing import List, Callable, Any

import math
import random as rand
import numpy as np
import pyrr
import moderngl as mgl

from .base import WindowBase
from .solid import Solid, createDodecahedron, createCube, createCone, createCilinder

class ParticleScene(WindowBase):
    title = 'Hello Program'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.particle_prog = self.ctx.program(
            vertex_shader='''
                #version 330 core

                uniform mat4 mvp;
                uniform vec3 emmiterPos;
                
                in vec3 aPointPosition;
                out float emmiterDist;

                void main()
                {
                    gl_Position = mvp * vec4(aPointPosition, 1.0);
                    emmiterDist = length(emmiterPos - aPointPosition);
                    if (emmiterDist < 0.1)
                    {
                        emmiterDist = 100;
                    }
                    gl_PointSize = 10.0 / emmiterDist;
                }
            ''',
            fragment_shader='''
                #version 330 core

                uniform sampler2D tex;

                in float emmiterDist;
                out vec4 color;

                void main()
                {
                    color = vec4(texture(tex, gl_PointCoord).rgb * 1.0, 1.0 / emmiterDist);
                }
            ''',
        )

        self.solid_prog = self.ctx.program(
            vertex_shader='''
                #version 330 core

                in vec3 aVertexPosition;
                in vec4 aVertexColor;

                uniform mat4 mvp;

                varying lowp vec4 vColor;

                void main(void) {
                    gl_Position = mvp * vec4(aVertexPosition, 1.0);
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

        snowflake_texture = self.load_texture_2d('/home/aaletov/uni/7sem/computer-graphics/snowflake.png')
        antiat = AntiAttractor(pyrr.Vector3(np.array([-2.0, 2.0, 2.0]), dtype='f4'), 1e+8)
        cone = createCone()
        cil = createCilinder()
        cube = createCube()
        anticube = createCube()

        anticube_scale = pyrr.Matrix44.from_scale(np.array([0.2, 0.2, 0.2]), dtype='f4')
        anticube_trans = pyrr.Matrix44.from_translation(np.array([-2.0, 2.0, 6.0]), dtype='f4')
        anticube.transform(anticube_trans * anticube_scale)

        cil_scale = pyrr.Matrix44.from_scale(np.array([0.4, 1.0, 0.4]), dtype='f4')
        cil_rot_z = pyrr.Matrix44.from_z_rotation(math.pi / 2, dtype='f4')
        cil_rot_y = pyrr.Matrix44.from_y_rotation(math.pi / 4, dtype='f4')
        cil_trans = pyrr.Matrix44.from_translation(np.array([2.0, 2.0, -1.0]), dtype='f4')
        cil.transform(cil_trans * cil_rot_y * cil_rot_z * cil_scale)
        cube.transform(cil_trans * cil_rot_y * cil_rot_z * cil_scale)

        self.particle_system = ParticleSystem(self.ctx, self.particle_prog, 
                                              snowflake_texture, cone, cube, antiat)

        self.anticube = DumbModel(self.ctx, self.solid_prog, anticube)
        self.emitter = DumbModel(self.ctx, self.solid_prog, cone)
        self.collider = DumbModel(self.ctx, self.solid_prog, cil)

    def render(self, time: float, frame_time: float):
        self.ctx.enable(mgl.DEPTH_TEST | mgl.PROGRAM_POINT_SIZE | mgl.BLEND)
        self.ctx.clear(0.0, 0.0, 0.0, 0.0)

        fieldOfView = (90 * math.pi) / 180 # in radians
        aspect = self.window_size[0] / self.window_size[1]
        zNear = 0.1
        zFar = 1000.0

        perspective = pyrr.Matrix44.perspective_projection(fieldOfView, 
                                                            aspect, zNear, zFar, dtype='f4')
        lookat = pyrr.Matrix44.look_at(
            (0, 100, 200),
            (0.0, 0.0, 0.0),
            (0.0, 1.0, 0.0),
            dtype='f4'
        )

        model = pyrr.Matrix44.from_translation(np.array([0.0, 0.0, 0.0]), dtype='f4')
        mvp = perspective * lookat * model
        self.solid_prog["mvp"].write(mvp.tobytes())
        self.particle_prog["mvp"].write(mvp.tobytes())
        self.particle_prog["emmiterPos"].write(np.array([0.0, 0.0, 0.0], dtype='f4').tobytes())
        self.anticube.render()
        self.emitter.render()
        self.collider.render()
        self.particle_system.tick()
        self.particle_system.render()

class AntiAttractor:
    def __init__(self, coord: pyrr.Vector3, mass: float):
        self.coord = coord
        self.mass = mass

class Particle:
    def __init__(self, coord: pyrr.Vector3, mass: float, velocity: pyrr.Vector3,
                 acceleration: pyrr.Vector3, collider: Solid, antiat: AntiAttractor):
        self.coord = coord
        self.mass = mass
        self.velocity = velocity
        self.acceleration = acceleration
        self.collider = collider
        self.antiat = antiat

    def tick(self):
        if self.collider.is_in(self.coord):
            self.velocity = - self.velocity
        self.coord = self.coord + self.velocity
        self.velocity = self.velocity + self.acceleration
        antivector = self.coord - self.antiat.coord
        antivector = antivector / np.power(np.linalg.norm(antivector), 3)
        self.acceleration = self.mass * self.antiat.mass * antivector


class ParticleSystem:
    def __init__(self, ctx: mgl.Context, program: mgl.Program, texture: mgl.Texture,
                 emitter: Solid, collider: Solid, antiat: AntiAttractor):
        self.ctx = ctx
        self.program = program
        self.texture = texture
        self.emitter = emitter
        self.collider = collider
        self.antiat = antiat
        self.mass = 1e-9
        self.starting_velocity = 0.2
        self.particles: List[Particle] = []
        self.max_age = 50

        self.vbo = self.ctx.buffer(dynamic=True, reserve=4096)

        self.vao = self.ctx.vertex_array(self.program, [
                (self.vbo, '3f', 'aPointPosition'),
            ],
        )

    def gen(self):
        faces_count = len(self.emitter.graph["faces"])
        face_idx = self.emitter.graph["faces"][rand.randint(0, faces_count - 1)]
        vertices = filter(lambda v: face_idx in v["faces"], self.emitter.graph.vs)
        vcoords = np.array([v["coord"] for v in vertices])
        coord = np.average(vcoords, axis=0)
        normal = self.emitter.get_face_normal(face_idx)
        velocity = self.starting_velocity * (normal / np.linalg.norm(normal))

        self.particles.append(Particle(coord, self.mass, velocity,
                                       pyrr.Vector3(), self.collider, self.antiat))
        
    def tick(self):
        if len(self.particles) == self.max_age:
            self.particles.pop(0)
        for p in self.particles:
            p.tick()

        self.gen()

    def get_points_array(self) -> np.ndarray:
        return np.array([p.coord for p in self.particles], dtype='f4')

    def render(self):
        self.vbo.clear()
        self.vbo.write(self.get_points_array().astype('f4').tobytes(), offset=0)

        self.texture.use()
        self.vao.render(mode=mgl.POINTS)
    
class DumbModel:
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

    def render(self) -> None:
        self.vao.render(mode=mgl.TRIANGLES)
        

if __name__ == '__main__':
    ParticleScene.run()

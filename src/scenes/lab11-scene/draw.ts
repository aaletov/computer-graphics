import { mat4 } from 'gl-matrix';
import { getLab1ShaderProgram } from './shader';
import { initLab1PositionBuffer } from './buffers';
import { setLab1PositionAttribute } from './attributes';
import { PolyhedronFactory } from '../../polyhedron/polyhedron';
import { buffer } from 'stream/consumers';
import { drawLab1Cube } from './cube';
import { drawLab1Dodecahedron } from './dodecahedron';

export async function initLab1Program(gl: WebGLRenderingContext) {
  const shaderProgram = await getLab1ShaderProgram(gl);
  const programInfo = {
    program: shaderProgram,
    attribLocations: {
      vertexPosition: gl.getAttribLocation(shaderProgram, "aVertexPosition"),
    },
    uniformLocations: {
      projectionMatrix: gl.getUniformLocation(shaderProgram, "uProjectionMatrix"),
      modelViewMatrix: gl.getUniformLocation(shaderProgram, "uModelViewMatrix"),
    },
  }
  const positionBuffer = initLab1PositionBuffer(gl, []);
  return {
    shaderProgram,
    programInfo,
    positionBuffer,
  }
}

function setCubeBuffer(positionBuffer: any): void {
  const positions = [
    // Mini-jump
    -1.0, -1.0, -1.0,
    -1.0, 1.0, -1.0,
    // Jump
    1.0, 1.0, -1.0,
    1.0, -1.0, -1.0,
    1.0, 1.0, -1.0,
    // Jump
    1.0, 1.0, 1.0,
    1.0, -1.0, 1.0,
    1.0, 1.0, 1.0,
    // Jump
    -1.0, 1.0, 1.0,
    -1.0, -1.0, 1.0,
    -1.0, 1.0, 1.0,
    // Jump
    -1.0, 1.0, -1.0,
    -1.0, -1.0, -1.0,
    -1.0, 1.0, -1.0,
    // Traverse bottom
    -1.0, -1.0, -1.0,
    1.0, -1.0, -1.0,
    1.0, -1.0, 1.0,
    -1.0, -1.0, 1.0,
    -1.0, -1.0, -1.0,
  ];
  positionBuffer.load(positions);
}

function setDodecahedronBuffer(positionBuffer: any) {
  const polyFactory = new PolyhedronFactory();
  const positions = polyFactory.getDodecahedron(1).getCartesianCover();
  positionBuffer.load(positions);
}

function initScene(gl: WebGLRenderingContext) {
  gl.clearColor(0.0, 0.0, 0.0, 1.0); // Clear to black, fully opaque
  gl.clearDepth(1.0); // Clear everything
  gl.enable(gl.DEPTH_TEST); // Enable depth testing
  gl.depthFunc(gl.LEQUAL); // Near things obscure far things

  // Clear the canvas before we start drawing on it.

  gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);
}

export async function drawLab1(
  gl: WebGLRenderingContext,
) {
  const program = await initLab1Program(gl);
  let i = 0;
  function render(now: DOMHighResTimeStamp) {
    initScene(gl);
    setCubeBuffer(program.positionBuffer);
    drawLab1Cube(gl, program, i * (Math.PI / 4));
    setDodecahedronBuffer(program.positionBuffer);
    drawLab1Dodecahedron(gl, program, i * (Math.PI / 2));

    i = (i == 1) ? 0 : 1;
    setTimeout(() => {
      requestAnimationFrame(render);
    }, 5000);
  }
  requestAnimationFrame(render);

};

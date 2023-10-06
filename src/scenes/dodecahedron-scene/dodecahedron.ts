import { mat4 } from 'gl-matrix';
import { setDodecahedronPositionAttribute } from './attributes';
import { getDodecahedronShaderProgram } from './shader';
import { initDodecahedronPositionBuffer } from './buffers';
import { PolyhedronFactory } from '../../polyhedron/polyhedron';

export async function initDodecahedronProgram(gl: WebGLRenderingContext) {
  const shaderProgram = await getDodecahedronShaderProgram(gl);
  const programInfo = {
    program: shaderProgram,
    attribLocations: {
      vertexPosition: gl.getAttribLocation(shaderProgram, "aVertexPosition"),
    },
    uniformLocations: {
      projectionMatrix: gl.getUniformLocation(shaderProgram, "uProjectionMatrix"),
      modelViewMatrix: gl.getUniformLocation(shaderProgram, "uModelViewMatrix"),
    },
  };

  // Now create an array of positions for the square.
  const polyFactory = new PolyhedronFactory();
  const positions = polyFactory.getDodecahedron(1).getCartesianCover();
  console.log(polyFactory.getDodecahedron(1));
  console.log(positions);

  const positionBuffer = initDodecahedronPositionBuffer(gl, positions);
  return {
    shaderProgram: shaderProgram,
    positionBuffer: positionBuffer,
    programInfo: programInfo,
  };
}

export function drawDodecahedron(
  gl: WebGLRenderingContext,
  dodecahedronProgram: any,
) {
  const dodecahedronRotation = 0.030;
  gl.clearColor(0.0, 0.0, 0.0, 1.0); // Clear to black, fully opaque
  gl.clearDepth(1.0); // Clear everything
  gl.enable(gl.DEPTH_TEST); // Enable depth testing
  gl.depthFunc(gl.LEQUAL); // Near things obscure far things

  // Clear the canvas before we start drawing on it.

  gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);

  // Create a perspective matrix, a special matrix that is
  // used to simulate the distortion of perspective in a camera.
  // Our field of view is 45 degrees, with a width/height
  // ratio that matches the display size of the canvas
  // and we only want to see objects between 0.1 units
  // and 100 units away from the camera.

  const fieldOfView = (45 * Math.PI) / 180; // in radians
  const canvas = <HTMLCanvasElement> gl.canvas;
  const aspect = canvas.clientWidth / canvas.clientHeight;
  const zNear = 0.1;
  const zFar = 100.0;
  const projectionMatrix = mat4.create();

  // note: glmatrix.js always has the first argument
  // as the destination to receive the result.
  mat4.perspective(projectionMatrix, fieldOfView, aspect, zNear, zFar);

  // Set the drawing position to the "identity" point, which is
  // the center of the scene.
  const modelViewMatrix = mat4.create();

  // Now move the drawing position a bit to where we want to
  // start drawing the square.
  mat4.translate(
    modelViewMatrix, // destination matrix
    modelViewMatrix, // matrix to translate
    [0.0, 0.0, -5.0],
  ); // amount to translate

  mat4.rotate(
    modelViewMatrix, // destination matrix
    modelViewMatrix, // matrix to rotate
    dodecahedronRotation * 15.0, // amount to rotate in radians
    [0, 0, 1],
  ); // axis to rotate around (Z)
  mat4.rotate(
    modelViewMatrix, // destination matrix
    modelViewMatrix, // matrix to rotate
    dodecahedronRotation * 10.0, // amount to rotate in radians
    [0, 1, 0],
  ); // axis to rotate around (Y)
  mat4.rotate(
    modelViewMatrix, // destination matrix
    modelViewMatrix, // matrix to rotate
    dodecahedronRotation * 10.0, // amount to rotate in radians
    [1, 0, 0],
  ); // axis to rotate around (X)

  // Tell WebGL how to pull out the positions from the position
  // buffer into the vertexPosition attribute.
  setDodecahedronPositionAttribute(gl, dodecahedronProgram.programInfo);

  // Tell WebGL to use our program when drawing
  gl.useProgram(dodecahedronProgram.programInfo.program);

  // Set the shader uniforms
  gl.uniformMatrix4fv(
    dodecahedronProgram.programInfo.uniformLocations.projectionMatrix,
    false,
    projectionMatrix,
  );
  gl.uniformMatrix4fv(
    dodecahedronProgram.programInfo.uniformLocations.modelViewMatrix,
    false,
    modelViewMatrix,
  );

  {
    const vertexCount = 116;
    const type = gl.UNSIGNED_SHORT;
    const offset = 0;
    gl.drawArrays(gl.LINE_STRIP, offset, vertexCount);
  }
};

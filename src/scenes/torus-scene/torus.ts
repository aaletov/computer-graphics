import { mat4 } from 'gl-matrix';
import { setTorusPositionAttribute } from './attributes';
import { getTorusShaderProgram } from './shader';
import { initTorusPositionBuffer } from './buffers';
import { createTorus, rotateLine } from '../../revolution/revolution';

export async function initTorusProgram(gl: WebGLRenderingContext) {
  const shaderProgram = await getTorusShaderProgram(gl);
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
  const positions = createTorus(0.5, 16, 0.5, 20).coordinates;
  console.log(positions);
  // const positions = [
  //   0.5, 0.5, 0.0,
  //   0.75, 0.5, 0.0,
  //   0.75, 0.25, 0.0,
  //   0.5, 0.25, 0.0,
  // ];

  const positionBuffer = initTorusPositionBuffer(gl, positions);
  return {
    shaderProgram: shaderProgram,
    positionBuffer: positionBuffer,
    programInfo: programInfo,
  };
}

export function drawTorus(
  gl: WebGLRenderingContext,
  torusProgram: any,
) {
  const torusRotation = 0.030;
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
    [-0.0, 0.0, -6.0],
  ); // amount to translate

  mat4.rotate(
    modelViewMatrix, // destination matrix
    modelViewMatrix, // matrix to rotate
    Math.PI * (0 / 180), // amount to rotate in radians
    [0, 0, 1],
  ); // axis to rotate around (Z)
  mat4.rotate(
    modelViewMatrix, // destination matrix
    modelViewMatrix, // matrix to rotate
    Math.PI * (0 / 180), // amount to rotate in radians
    [0, 1, 0],
  ); // axis to rotate around (Y)
  mat4.rotate(
    modelViewMatrix, // destination matrix
    modelViewMatrix, // matrix to rotate
    Math.PI * (45 / 180), // amount to rotate in radians
    [1, 0, 0],
  ); // axis to rotate around (X)

  // Tell WebGL how to pull out the positions from the position
  // buffer into the vertexPosition attribute.
  setTorusPositionAttribute(gl, torusProgram.programInfo);

  // Tell WebGL to use our program when drawing
  gl.useProgram(torusProgram.programInfo.program);

  // Set the shader uniforms
  gl.uniformMatrix4fv(
    torusProgram.programInfo.uniformLocations.projectionMatrix,
    false,
    projectionMatrix,
  );
  gl.uniformMatrix4fv(
    torusProgram.programInfo.uniformLocations.modelViewMatrix,
    false,
    modelViewMatrix,
  );

  {
    const vertexCount = 1175;
    const type = gl.UNSIGNED_SHORT;
    const offset = 0;
    gl.drawArrays(gl.LINE_STRIP, offset, vertexCount);
  }
};

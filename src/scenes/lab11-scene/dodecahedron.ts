import { mat4 } from 'gl-matrix';
import { PolyhedronFactory } from '../../polyhedron/polyhedron';
import { getLab1ShaderProgram } from './shader';
import { initLab1PositionBuffer } from './buffers';
import { setLab1PositionAttribute } from './attributes';

export function drawLab1Dodecahedron(
  gl: WebGLRenderingContext,
  dodecahedronProgram: any,
  yRotation: number,
) {
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
    [-2.0, 0.0, -7.0],
  ); // amount to translate

  mat4.rotate(
    modelViewMatrix, // destination matrix
    modelViewMatrix, // matrix to rotate
    yRotation, // amount to rotate in radians
    [0, 1, 0],
  ); // axis to rotate around (Y)

  // Tell WebGL how to pull out the positions from the position
  // buffer into the vertexPosition attribute.
  setLab1PositionAttribute(gl, dodecahedronProgram.programInfo);

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

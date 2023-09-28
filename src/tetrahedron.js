import { initShaderProgram } from './low-level/shaders';
import { initBuffers } from './low-level/buffers';
import { drawCube } from './draw';

async function initLowLevel(gl) {
  const vsSourceResponse = await fetch('./cubeVertex.glsl');
  const vsSource = await vsSourceResponse.text();
  const fsSourceResponse = await fetch('./cubeFragment.glsl');
  const fsSource = await fsSourceResponse.text();
  
  const shaderProgram = initShaderProgram(gl, vsSource, fsSource);

  const programInfo = {
    program: shaderProgram,
    attribLocations: {
      vertexPosition: gl.getAttribLocation(shaderProgram, "aVertexPosition"),
      vertexColor: gl.getAttribLocation(shaderProgram, "aVertexColor"),
    },
    uniformLocations: {
      projectionMatrix: gl.getUniformLocation(shaderProgram, "uProjectionMatrix"),
      modelViewMatrix: gl.getUniformLocation(shaderProgram, "uModelViewMatrix"),
    },
  };

  const buffers = initBuffers(gl);

  return {
    'buffers': buffers,
    'programInfo': programInfo,
  }
}

export function cube(gl) {
  initLowLevel(gl).then((lowLevel) => {
    let cubeRotation = 0.0;
    let deltaTime = 0;
    let then = 0;
  
    // Draw the scene repeatedly
    function render(now) {
      now *= 0.001; // convert to seconds
      deltaTime = now - then;
      then = now;
  
      drawCube(gl, lowLevel.buffers, lowLevel.programInfo, cubeRotation);
      cubeRotation += deltaTime;
  
      requestAnimationFrame(render);
    }
    requestAnimationFrame(render);
  });
}
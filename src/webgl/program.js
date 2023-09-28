import { getDefaultShaderProgram } from "./shader";
import { createBuffers } from "./buffers";

export async function createProgram(gl) {
  const defaultShaderProgram = await getDefaultShaderProgram(gl);

  const programInfo = {
    program: defaultShaderProgram,
    attribLocations: {
      vertexPosition: gl.getAttribLocation(defaultShaderProgram, "aVertexPosition"),
      vertexColor: gl.getAttribLocation(defaultShaderProgram, "aVertexColor"),
    },
    uniformLocations: {
      projectionMatrix: gl.getUniformLocation(defaultShaderProgram, "uProjectionMatrix"),
      modelViewMatrix: gl.getUniformLocation(defaultShaderProgram, "uModelViewMatrix"),
    },
  };

  const buffers = createBuffers(gl);

  return {
    'shaderProgram': defaultShaderProgram,
    'buffers': buffers,
    'programInfo': programInfo,
  }
}
function createPositionBuffer(gl) {
  const glBuffer = gl.createBuffer();
  // Select the positionBuffer as the one to apply buffer
  // operations to from here out.
  gl.bindBuffer(gl.ARRAY_BUFFER, glBuffer);

  function load(positions) {
    // Now pass the list of positions into WebGL to build the
    // shape. We do this by creating a Float32Array from the
    // JavaScript array, then use it to fill the current buffer.
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(positions), gl.STATIC_DRAW);
  }

  return {
    load,
    glBuffer
  }
}

export function initLab1PositionBuffer(gl, positions) {
  const positionBuffer = createPositionBuffer(gl);
  positionBuffer.load(positions);
  return positionBuffer;
}

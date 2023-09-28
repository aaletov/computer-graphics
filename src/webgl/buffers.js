// function initIndexBuffer(gl, indices) {


//   return indexBuffer;
// }

// function initColorBuffer(gl, faceColors) {  


//   return colorBuffer;
// }

// function initPositionBuffer(gl, positions) {


//   return positionBuffer;
// }

export function createPositionBuffer(gl) {
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

export function createColorBuffer(gl) {
  const glBuffer = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, glBuffer);

  function load(faceColors) {
    // Convert the array of colors into a table for all the vertices.
    var colors = [];
    
    for (var j = 0; j < faceColors.length; ++j) {
      const c = faceColors[j];
      // Repeat each color four times for the four vertices of the face
      colors = colors.concat(c, c, c, c);
    }

    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(colors), gl.STATIC_DRAW);
  }

  return {
    load,
    glBuffer,
  }
}

export function createIndexBuffer(gl) {
  const glBuffer = gl.createBuffer();
  gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, glBuffer);

  function load(indices) {
    // Now send the element array to GL
    gl.bufferData(
      gl.ELEMENT_ARRAY_BUFFER,
      new Uint16Array(indices),
      gl.STATIC_DRAW,
    );
  }

  return {
    load,
    glBuffer,
  }
}

export function createBuffers(gl) {
  return {
    position: createPositionBuffer(gl),
    color: createColorBuffer(gl),
    index: createIndexBuffer(gl),
  };
}

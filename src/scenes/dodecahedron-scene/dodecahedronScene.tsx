import { useEffect, useRef } from 'react';
import { drawDodecahedron, initDodecahedronProgram } from './dodecahedron';

export function DodecahedronScene() {
  const ref = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    const canvas = ref.current;
    if (canvas == null) {
      return;
    }

    const gl = canvas.getContext("webgl");

    if (gl === null) {
      alert(
        "Unable to initialize WebGL. Your browser or machine may not support it.",
      );
      return;
    }
    initDodecahedronProgram(gl).then((dodecahedronProgram) => {
      drawDodecahedron(gl, dodecahedronProgram);
    });
  });

  return <canvas id="glcanvas" width="640" height="480" ref={ref}></canvas>
}
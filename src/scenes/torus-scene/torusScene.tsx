import { useEffect, useRef } from 'react';
import { drawTorus, initTorusProgram } from './torus';

export function TorusScene() {
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
    initTorusProgram(gl).then((torusProgram) => {
      drawTorus(gl, torusProgram);
    });
  });

  return <canvas id="glcanvas" width="640" height="480" ref={ref}></canvas>
}
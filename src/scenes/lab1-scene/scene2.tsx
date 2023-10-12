import { useEffect, useRef } from 'react';
import { drawLab1Scene1, drawLab1Scene2 } from './draw';

export function Lab1Scene2() {
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
    
    drawLab1Scene2(gl);
  });

  return <canvas id="glcanvas" width="640" height="480" ref={ref}></canvas>
}
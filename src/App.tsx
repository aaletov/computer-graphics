import './App.css';
import { useEffect, useRef } from 'react';
import { tetrahedronAnimation } from './figures/tetrahedron';
import { CubeScene } from './scenes/cube-scene/cubeScene';

function Canvas() {
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

    tetrahedronAnimation(gl);
  });

  return <canvas id="glcanvas" width="640" height="480" ref={ref}></canvas>
}

function App() {
  return (
    <div className="App">
      <CubeScene/>
    </div>
  );
}

export default App;

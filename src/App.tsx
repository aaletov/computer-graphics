import './App.css';
import { useEffect, useRef } from 'react';
import { tetrahedronAnimation } from './figures/tetrahedron';
import { CubeScene } from './scenes/cube-scene/cubeScene';
import { TetrahedronScene } from './scenes/tetrahedron-scene/tetrahedronScene';

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
      <TetrahedronScene/>
    </div>
  );
}

export default App;

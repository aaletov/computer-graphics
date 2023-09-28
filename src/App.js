import './App.css';
import { useEffect, useRef } from 'react';
import { cube } from './cube'; 

function Canvas() {
  const ref = useRef(null);
  useEffect(() => {
    const gl = ref.current.getContext("webgl");

    if (gl === null) {
      alert(
        "Unable to initialize WebGL. Your browser or machine may not support it.",
      );
      return;
    }

    cube(gl);
  });

  return <canvas id="glcanvas" width="640" height="480" ref={ref}></canvas>
}

function App() {
  return (
    <div className="App">
      <Canvas/>
    </div>
  );
}

export default App;

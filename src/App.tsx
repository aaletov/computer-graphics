import './App.css';
import { useEffect, useRef } from 'react';
import { RotatingCubeScene } from './scenes/rotating-cube-scene/rotatingCubeScene';

function App() {
  return (
    <div className="App">
      <RotatingCubeScene/>
    </div>
  );
}

export default App;

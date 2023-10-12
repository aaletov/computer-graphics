import './App.css';
import { useEffect, useRef } from 'react';
import { TorusScene } from './scenes/torus-scene/torusScene';
import { ConeScene } from './scenes/cone-scene/coneScene';
import { Lab1Scene } from './scenes/lab11-scene/scene';

function App() {
  return (
    <div className="App">
      <Lab1Scene/>
    </div>
  );
}

export default App;

import './App.css';
import { useEffect, useRef } from 'react';
import { TorusScene } from './scenes/torus-scene/torusScene';
import { ConeScene } from './scenes/cone-scene/coneScene';

function App() {
  return (
    <div className="App">
      <ConeScene/>
    </div>
  );
}

export default App;

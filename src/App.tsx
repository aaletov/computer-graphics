import './App.css';
import { useEffect, useRef } from 'react';
import { Lab1Scene1 } from './scenes/lab1-scene/scene1';
import { Lab1Scene2 } from './scenes/lab1-scene/scene2';

function App() {
  return (
    <div className="App">
      <Lab1Scene1/>
      <Lab1Scene2/>
    </div>
  );
}

export default App;

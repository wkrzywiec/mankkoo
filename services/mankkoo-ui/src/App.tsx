import React from 'react';
import { Navbar } from './components/Navbar'
import { Main } from './pages/Main'
import './App.css';

function App() {
  return (
    <div>
      <div id="page-content">
        <Navbar />
        <Main />
      </div>
    </div>
  );
}

export default App;

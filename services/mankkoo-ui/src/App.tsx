import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Navbar } from './components/Navbar'
import { Main } from './pages/Main'
import { Account } from './pages/Account'
import './App.css';

function App() {
  return (
    <div>
      <div id="page-content">
        <Navbar />
        <Routes>
          <Route path="/" element={<Main />} />
          <Route path="/main" element={<Main />} />
          <Route path="/home" element={<Main />} />
          <Route path="/accounts" element={<Account />} />
        </Routes>
      </div>
    </div>
  );
}

export default App;

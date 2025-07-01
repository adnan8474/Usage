import React from 'react';
import Home from './Home.jsx';
import Dashboard from './Dashboard.jsx';
import Instructions from './Instructions.jsx';

export default function App() {
  const [page, setPage] = React.useState('home');

  return (
    <div className="min-h-screen flex flex-col">
      <nav className="bg-blue-600 text-white p-4 flex justify-between">
        <div className="font-bold">POCTIFY</div>
        <div className="space-x-4">
          <button onClick={() => setPage('home')}>Home</button>
          <button onClick={() => setPage('dashboard')}>Dashboard</button>
          <button onClick={() => setPage('instructions')}>Instructions</button>
        </div>
      </nav>
      <main className="flex-grow p-4">
        {page === 'home' && <Home onLaunch={() => setPage('dashboard')} />}
        {page === 'dashboard' && <Dashboard />}
        {page === 'instructions' && <Instructions />}
      </main>
    </div>
  );
}

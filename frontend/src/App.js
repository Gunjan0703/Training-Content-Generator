import React from 'react';
import Dashboard from './components/Dashboard';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>AI Corporate Training Platform</h1>
        <p>Powered by Amazon Bedrock and LangChain</p>
      </header>
      <main>
        <Dashboard />
      </main>
      <footer className="App-footer">
        <p>Microservices Edition - 2025</p>
      </footer>
    </div>
  );
}

export default App;

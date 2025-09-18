import React, { useState } from 'react';
import { personalizeContent } from '../services/api';

const PersonalizationEngine = () => {
  const [topic, setTopic] = useState('');
  const [user_id, setUserId] = useState('user-123-sales');
  const [user_role, setUserRole] = useState('Sales');
  const [result, setResult] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setResult('Adapting content using RAG...');
    try {
      const response = await personalizeContent(topic, user_id, user_role);
      setResult(response.data);
    } catch (error) {
      setResult(`Error: ${error.response?.data?.error || error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="feature-card">
      <h2>3. Personalization Engine (RAG)</h2>
      <p>Generate adaptive content. Use User ID 'user-123-sales' to test the RAG feature.</p>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="Enter topic (e.g., 'Handling Objections')"
          required
        />
        <input
          type="text"
          value={user_id}
          onChange={(e) => setUserId(e.target.value)}
          placeholder="Enter User ID"
          required
        />
        <input
          type="text"
          value={user_role}
          onChange={(e) => setUserRole(e.target.value)}
          placeholder="Enter User Role"
          required
        />
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Adapting...' : 'Generate Personalized Module'}
        </button>
      </form>
      {result && <div className="result-box"><pre>{result}</pre></div>}
    </div>
  );
};

export default PersonalizationEngine;

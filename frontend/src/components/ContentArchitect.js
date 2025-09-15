import React, { useState } from 'react';
import { createCurriculum } from '../services/api';

const ContentArchitect = () => {
  const [topic, setTopic] = useState('');
  const [result, setResult] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setResult('Architecting curriculum... this may take a while as it involves multiple AI steps.');
    try {
      const response = await createCurriculum(topic);
      setResult(response.data.curriculum);
    } catch (error) {
      setResult(`Error: ${error.response?.data?.error || error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="feature-card">
      <h2>1. Content Architect</h2>
      <p>Generate a full curriculum from a single topic using an AI agent.</p>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="Enter a broad topic (e.g., 'Digital Marketing')"
          required
        />
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Building...' : 'Create Curriculum'}
        </button>
      </form>
      {result && <div className="result-box"><pre>{result}</pre></div>}
    </div>
  );
};

export default ContentArchitect;

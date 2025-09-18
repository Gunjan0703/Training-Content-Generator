import React, { useState } from 'react';
import { personalizeContent } from '../services/api';

const PersonalizationEngine = () => {
  const [topic, setTopic] = useState('');
  const [user_id, setUserId] = useState('user-123-sales');
  const [user_role, setUserRole] = useState('Sales');
  const [content, setContent] = useState('');
  const [weaknessUsed, setWeaknessUsed] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setContent('Adapting content using RAG...');
    setWeaknessUsed(false);

    try {
      const response = await personalizeContent(topic, user_id, user_role);
      const data = response.data;

      setContent(data.personalized_content || '');
      setWeaknessUsed(data.weakness_context_used || false);
    } catch (error) {
      setContent(`Error: ${error.response?.data?.error || error.message}`);
      setWeaknessUsed(false);
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

      {content && (
        <div className="result-box">
          {/* <p><strong>Weakness Context Used:</strong> {weaknessUsed ? 'Yes' : 'No'}</p> */}
          <pre>{content}</pre>
        </div>
      )}
    </div>
  );
};

export default PersonalizationEngine;

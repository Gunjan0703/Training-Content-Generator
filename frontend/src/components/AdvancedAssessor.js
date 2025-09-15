import React, { useState } from 'react';
import { createAssessment } from '../services/api';

const AdvancedAssessor = () => {
  const [content, setContent] = useState('');
  const [assessment_type, setType] = useState('multiple_choice');
  const [result, setResult] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setResult('Generating assessment...');
    try {
      const response = await createAssessment(content, assessment_type);
      setResult(response.data);
    } catch (error) {
      setResult(`Error: ${error.response?.data?.error || error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="feature-card">
      <h2>2. Advanced Assessor</h2>
      <p>Generate diverse assessments from any text content.</p>
      <form onSubmit={handleSubmit}>
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Paste course content here..."
          required
        />
        <select value={assessment_type} onChange={(e) => setType(e.target.value)}>
          <option value="multiple_choice">Multiple Choice</option>
          <option value="scenario">Scenario-Based</option>
          <option value="fill_in_the_blanks">Fill-in-the-Blanks</option>
        </select>
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Generating...' : 'Create Assessment'}
        </button>
      </form>
      {result && <div className="result-box"><pre>{result}</pre></div>}
    </div>
  );
};

export default AdvancedAssessor;

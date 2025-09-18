import React, { useState } from 'react';
import { createAssessment } from '../services/api';

const AdvancedAssessor = () => {
  const [content, setContent] = useState('');
  const [assessmentType, setAssessmentType] = useState('multiple_choice');
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setResult(null); // clear previous
    try {
      const response = await createAssessment(content, assessmentType);
      setResult(response.data);
    } catch (error) {
      setResult({ error: error.response?.data?.error || error.message });
    } finally {
      setIsLoading(false);
    }
  };

  // Helper to render a single assessment object
  const renderAssessment = (item, idx) => (
    <div key={idx} className="assessment-item">
      {item.assessment && <p><strong>Question:</strong> {item.assessment}</p>}
      {item.type && <p><strong>Type:</strong> {item.type}</p>}
    </div>
  );

  // Decide how to render result
  const renderResult = () => {
    if (!result) return null;

    // If backend returned an error
    if (result.error) return <p style={{ color: 'red' }}>{result.error}</p>;

    // If result is an array of assessments
    if (Array.isArray(result)) {
      return result.map(renderAssessment);
    }

    // If result is a single object
    if (typeof result === 'object') {
      return renderAssessment(result, 0);
    }

    // If result is a plain string
    return <pre>{result}</pre>;
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
        <select value={assessmentType} onChange={(e) => setAssessmentType(e.target.value)}>
          <option value="multiple_choice">Multiple Choice</option>
          <option value="scenario">Scenario-Based</option>
          <option value="fill_in_the_blanks">Fill-in-the-Blanks</option>
        </select>
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Generating...' : 'Create Assessment'}
        </button>
      </form>
      <div className="result-box">{renderResult()}</div>
    </div>
  );
};

export default AdvancedAssessor;

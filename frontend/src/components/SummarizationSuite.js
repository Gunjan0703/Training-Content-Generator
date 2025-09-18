import React, { useState } from 'react';
import { summarizeText } from '../services/api';

const SummarizationSuite = () => {
    const [text, setText] = useState('');
    const [format_type, setFormat] = useState('bulleted list');
    const [length, setLength] = useState('medium');
    const [result, setResult] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setResult('Summarizing...');
        try {
            const response = await summarizeText(text, format_type, length);

            // Extract summary if response.data is an object
            const summaryText = typeof response.data === 'object'
                ? response.data.summary || JSON.stringify(response.data, null, 2)
                : response.data;

            setResult(summaryText);

        } catch (error) {
            setResult(`Error: ${error.response?.data?.error || error.message}`);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="feature-card">
            <h2>4. Summarization Suite</h2>
            <p>Create customized summaries from long text.</p>
            <form onSubmit={handleSubmit}>
                <textarea
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    placeholder="Paste long text here..."
                    required
                />
                <select value={format_type} onChange={(e) => setFormat(e.target.value)}>
                    <option value="bulleted list">Bulleted List</option>
                    <option value="paragraph">Paragraph</option>
                </select>
                <select value={length} onChange={(e) => setLength(e.target.value)}>
                    <option value="short">Short</option>
                    <option value="medium">Medium</option>
                    <option value="long">Long</option>
                </select>
                <button type="submit" disabled={isLoading}>
                    {isLoading ? 'Summarizing...' : 'Summarize Text'}
                </button>
            </form>
            {result && (
                <div className="result-box">
                    <pre>{typeof result === 'object' ? JSON.stringify(result, null, 2) : result}</pre>
                </div>
            )}
        </div>
    );
};

export default SummarizationSuite;

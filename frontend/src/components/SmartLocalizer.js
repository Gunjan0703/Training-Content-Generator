import React, { useState } from 'react';
import { localizeText } from '../services/api';

const SmartLocalizer = () => {
    const [text, setText] = useState('Our Key Performance Indicators are strong this quarter.');
    const [target_language, setLang] = useState('German');
    const [glossary, setGlossary] = useState('{"Key Performance Indicators": "Leistungskennzahlen"}');
    const [localize, setLocalize] = useState(true);
    const [result, setResult] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setResult('Localizing...');
        try {
            let glossaryObj = glossary ? JSON.parse(glossary) : null;
            const response = await localizeText(text, target_language, glossary, localize);
            setResult(response.data);
        } catch (error) {
            setResult(`Error: ${error.response?.data?.error || 'Invalid JSON in glossary'}`);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="feature-card">
            <h2>5. Smart Localizer</h2>
            <p>Translate with context, glossaries, and cultural adaptation.</p>
            <form onSubmit={handleSubmit}>
                <textarea value={text} onChange={(e) => setText(e.target.value)} required />
                <input type="text" value={target_language} onChange={(e) => setLang(e.target.value)} placeholder="Target Language" required />
                <textarea
                    value={glossary}
                    onChange={(e) => setGlossary(e.target.value)}
                    placeholder='Enter glossary as JSON (e.g., {"Term": "Translation"})'
                />
                <label>
                    <input type="checkbox" checked={localize} onChange={(e) => setLocalize(e.target.checked)} />
                    Perform full localization (adapt dates, currency, etc.)
                </label>
                <button type="submit" disabled={isLoading}>
                    {isLoading ? 'Processing...' : 'Localize Text'}
                </button>
            </form>
            {result && <div className="result-box"><pre>{result}</pre></div>}
        </div>
    );
};

export default SmartLocalizer;

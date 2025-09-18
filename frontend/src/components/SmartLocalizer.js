import React, { useState } from 'react';
import { localizeText } from '../services/api';

const glossaryMap = {
    German: { "Key Performance Indicators": "Leistungskennzahlen" },
    Spanish: { "Key Performance Indicators": "Indicadores Clave de Rendimiento" },
    French: { "Key Performance Indicators": "Indicateurs Clés de Performance" }
};

const SmartLocalizer = () => {
    const [text, setText] = useState('Our Key Performance Indicators are strong this quarter.');
    const [target_language, setLang] = useState('German');
    const [glossary, setGlossary] = useState(glossaryMap['German']);
    const [localize, setLocalize] = useState(true);
    const [result, setResult] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleLangChange = (e) => {
        const lang = e.target.value;
        setLang(lang);

        // Auto-set glossary based on language
        setGlossary(glossaryMap[lang] || {});
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setResult('Localizing...');
        try {
            const response = await localizeText(text, target_language, glossary, localize);
            setResult(response.data.localized_text);
        } catch (error) {
            setResult(`Error: ${error.response?.data?.error || 'Failed to localize'}`);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="feature-card">
            <h2>5. Smart Localizer</h2>
            <p>Translate with context, glossaries, and cultural adaptation.</p>
            <form onSubmit={handleSubmit}>
                <textarea 
                    value={text} 
                    onChange={(e) => setText(e.target.value)} 
                    required 
                />
                <input 
                    type="text" 
                    value={target_language} 
                    onChange={handleLangChange} 
                    placeholder="Target Language" 
                    required 
                />
                <div>
                    <strong>Auto Glossary:</strong>
                    <pre>{JSON.stringify(glossary, null, 2)}</pre>
                </div>
                <label>
                    <input 
                        type="checkbox" 
                        checked={localize} 
                        onChange={(e) => setLocalize(e.target.checked)} 
                    />
                    Perform full localization (adapt dates, currency, etc.)
                </label>
                <button type="submit" disabled={isLoading}>
                    {isLoading ? 'Processing...' : 'Localize Text'}
                </button>
            </form>
            {result && (
                <div className="result-box">
                    <pre>{result}</pre>
                </div>
            )}
        </div>
    );
};

export default SmartLocalizer;

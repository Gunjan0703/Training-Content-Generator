import React, { useState } from 'react';
import { generateImage, generateLLMFlow } from '../services/api';

const MultimediaStudio = () => {
    const [prompt, setPrompt] = useState('');
    const [imageType, setImageType] = useState('general');
    const [result, setResult] = useState('');
    const [imageUrl, setImageUrl] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setResult(`Generating ${imageType === 'flowchart' ? 'flow chart' : 'image'}...`);
        setImageUrl('');
        try {
            const response = await generateImage(prompt, imageType);
            if (response.data.image_url) {
                const fullUrl = response.data.image_url.startsWith('http') ? 
                    response.data.image_url : 
                    `${process.env.REACT_APP_MULTIMEDIA_SERVICE_URL || 'http://localhost:8001'}${response.data.image_url}`;
                setImageUrl(fullUrl);
                setResult(response.data.message || 'Generated successfully!');
            }
        } catch (error) {
            setResult(`Error: ${error.response?.data?.detail || error.message}`);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="feature-card">
            <h2>6. Multimedia Studio</h2>
            <p>Generate images, diagrams, and flowcharts using AI.</p>
            
            <form onSubmit={handleSubmit} className="generation-form">
                <div className="input-group">
                    <input
                        type="text"
                        value={prompt}
                        onChange={(e) => setPrompt(e.target.value)}
                        placeholder={imageType === 'flowchart' ? 
                            "Enter steps for flowchart (e.g., 'Step 1, Step 2, Step 3' or 'LLM Architecture')" :
                            "Enter prompt for image generation..."}
                        required
                    />
                    <select 
                        value={imageType} 
                        onChange={(e) => setImageType(e.target.value)}
                        disabled={isLoading}
                    >
                        <option value="general">General Image</option>
                        <option value="flowchart">Flow Chart</option>
                    </select>
                </div>
                <button type="submit" disabled={isLoading}>
                    {isLoading ? 'Generating...' : `Generate ${imageType === 'flowchart' ? 'Flow Chart' : 'Image'}`}
                </button>
            </form>

            {imageUrl && (
                <div className="result-box">
                    <img 
                        src={imageUrl} 
                        alt={prompt} 
                        style={{ maxWidth: '100%', marginTop: '20px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }} 
                    />
                </div>
            )}

            {result && <div className="status-message">{result}</div>}

            <style jsx>{`
                .generation-form {
                    margin-top: 20px;
                }
                .input-group {
                    display: flex;
                    gap: 10px;
                    margin-bottom: 10px;
                }
                .input-group input {
                    flex: 1;
                }
                .input-group select {
                    width: 150px;
                }
                .result-box {
                    margin-top: 20px;
                    padding: 10px;
                    border-radius: 4px;
                    background: white;
                }
                .status-message {
                    margin-top: 10px;
                    padding: 10px;
                    border-radius: 4px;
                    background: #f5f5f5;
                }
            `}</style>
        </div>
    );
};

export default MultimediaStudio;

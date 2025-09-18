import React, { useState } from 'react';
import { generateImage } from '../services/api';

const MultimediaStudio = () => {
    const [prompt, setPrompt] = useState('');
    const [result, setResult] = useState('');
    const [imageUrl, setImageUrl] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setResult('Generating image with Bedrock Titan...');
        setImageUrl('');
        try {
            const response = await generateImage(prompt);
            setImageUrl(response.data.image_url);
            setResult('Image generated successfully!');
        } catch (error) {
            setResult(`Error: ${error.response?.data?.error || error.message}`);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="feature-card">
            <h2>6. Multimedia Studio</h2>
            <p>Generate images from text prompts.</p>
            <form onSubmit={handleSubmit}>
                <input
                    type="text"
                    value={prompt}
                    onChange={(e) => setPrompt(e.target.value)}
                    placeholder="Enter prompt for image generation..."
                    required
                />
                <button type="submit" disabled={isLoading}>
                    {isLoading ? 'Generating...' : 'Generate Image'}
                </button>
            </form>
            {result && <div className="result-box">
                <p>{result}</p>
                {imageUrl && <img src={imageUrl} alt={prompt} style={{ maxWidth: '100%', marginTop: '10px' }} />}
            </div>}
        </div>
    );
};

export default MultimediaStudio;

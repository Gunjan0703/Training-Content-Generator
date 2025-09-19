import React, { useState } from "react";

const MultimediaStudio = () => {
  const [prompt, setPrompt] = useState("");
  const [imageType, setImageType] = useState("general");
  const [imageUrl, setImageUrl] = useState("");
  const [loading, setLoading] = useState(false);

  const generateImage = async () => {
    setLoading(true);
    setImageUrl("");

    try {
      const response = await fetch("http://localhost:8001/generate-image", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt, image_type: imageType }),
      });

      const data = await response.json();

      if (response.ok) {
        setImageUrl(`http://localhost:8001${data.image_url}`);
      } else {
        alert(data.error || "Image generation failed");
      }
    } catch (error) {
      console.error("Error generating image:", error);
      alert("Error generating image");
    }

    setLoading(false);
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">🎨 Multimedia Studio</h1>

      <input
        type="text"
        placeholder="Enter prompt..."
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        className="border p-2 rounded w-full mb-3"
      />

      <select
        value={imageType}
        onChange={(e) => setImageType(e.target.value)}
        className="border p-2 rounded mb-3"
      >
        <option value="general">General</option>
        <option value="flowchart">Flowchart</option>
      </select>

      <button
        onClick={generateImage}
        disabled={loading}
        className="bg-blue-500 text-white px-4 py-2 rounded"
      >
        {loading ? "Generating..." : "Generate Image"}
      </button>

      {imageUrl && (
        <div className="mt-4">
          <p className="mb-2 font-medium">Generated Image:</p>
          <img src={imageUrl} alt="Generated" className="border rounded" />
        </div>
      )}
    </div>
  );
};

export default MultimediaStudio;

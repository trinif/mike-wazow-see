"use client";

import { useState } from "react";

export default function DichromatSimulation() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [blindness, setBlindness] = useState("deutan");
  const [resultUrl, setResultUrl] = useState<string | null>(null);
  const [inputUrl, setInputUrl] = useState<string | null>(null);

  const handleUpload = async () => {
    console.log("Uploading");
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append("image", selectedFile);

    // TODO: update route
    const res = await fetch(`http://localhost:5000/output?blindness=${encodeURIComponent(
      blindness
    )}`, {
      method: "POST",
      body: formData,
    });

    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    setResultUrl(url);
  };

  function handleFileChange(e: any) {
    const file = e.target.files?.[0];
    setSelectedFile(file);

    if (file) {
      setInputUrl(URL.createObjectURL(file));
    }
  }

  return (
    <div>
      <div>
        <p>Upload an image, choose a type of colorblindness, and see what the image looks like recolored for accessibility.</p>
      </div>
      <div className="upload-box">
        <h1>Parameters</h1>
        <div className="input-row">
          <div className="form-group">
            <label className="input-label">File to Upload</label>
            <input
              type="file"
              accept="image/*"
              onChange={handleFileChange}
            />
          </div>

          <div className="form-group">
            <label className="input-label">Condition</label>
            <select
                value={blindness}
                onChange={(e) => setBlindness(e.target.value)}
            >
                <option value="protan">Protanopia</option>
                <option value="deutan">Deuteranopia</option>
            </select>
          </div>    
        </div>

        <div>
          <button onClick={handleUpload}>Upload</button>
        </div>
      </div>

      {resultUrl && (
        <div className="input-row">
          <div className="form-group">
            <label className="input-label">Original Image: </label>
            <img
              src={inputUrl!!}
              alt="Input result"
              style={{ maxWidth: "300px" }}
            />
          </div>
          <div className="form-group">
            <label className="input-label">Full Recolored Image:</label>
            <img
              src={resultUrl}
              alt="Processed result"
              style={{ maxWidth: "300px" }}
            />
          </div>
        </div>
      )}

      <h2>Pipeline:</h2>
      <div className="form-group">
        <label className="input-label">Representative Colors:</label>
        {resultUrl && <img
            src={resultUrl /* TODO: replace resultUrl with Representative Colors */}
            alt="Processed result"
            style={{ maxWidth: "300px" }}
        />}
      </div>
      
      <h3></h3>
    </div>
  );
}

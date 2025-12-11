"use client";

import { useState } from "react";

export default function DichromatSimulation() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [blindness, setBlindness] = useState("deutan");
  const [resultUrls, setResultUrls] = useState([]);
  const [inputUrl, setInputUrl] = useState<string | null>(null);

  const handleUpload = async () => {
    console.log("Uploading");
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append("image", selectedFile);

    const res = await fetch(`http://localhost:5000/output?blindness=${encodeURIComponent(
      blindness
    )}`, {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    setResultUrls(data.urls);

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

      {resultUrls.length > 0 && (
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
              src={resultUrls[0]}
              alt="Processed result"
              style={{ maxWidth: "300px" }}
            />
          </div>
        </div>
      )}

      <h2>Pipeline:</h2>
      <div className="form-group">
        <label className="input-label">Representative Colors:</label>
        {resultUrls.length > 0 && <img
            src={resultUrls[1]}
            alt="Processed result"
            style={{ maxWidth: "300px" }}
        />}
      </div>
      <div className="input-row">
        <div className="form-group">
            <label className="input-label">Confusing Representative Colors:</label>
            {resultUrls.length > 0 && <img
                src={resultUrls[2]}
                alt="Processed result"
                style={{ maxWidth: "300px" }}
            />}
        </div>
        <div className="form-group">
            <label className="input-label">Non-Confusing Representative Colors:</label>
            {resultUrls.length > 0 && <img
                src={resultUrls[3]}
                alt="Processed result"
                style={{ maxWidth: "300px" }}
            />}
        </div>
      </div>
      
      <div className="input-row">
        <div className="form-group">
            <label className="input-label">Clusters of Non-Confusing Key Colors:</label>
            {resultUrls.length > 0 && <img
                src={resultUrls[4]}
                alt="Processed result"
                style={{ width: "150px", height: "50%" }}
            />}
        </div>
        <div className="form-group">
            <label className="input-label">Clusters of Confusing Key Colors:</label>
            {resultUrls.length > 0 && <img
                src={resultUrls[5]}
                alt="Processed result"
                style={{ width: "150px", height: "50%" }}
            />}
        </div>
      </div>
      <div className="form-group">
        <label className="input-label">Clusters of Confusing Key Colors With Cardinalities:</label>
        {resultUrls.length > 0 && <img
            src={resultUrls[6]}
            alt="Processed result"
            style={{ maxWidth: "300px" }}
        />}
      </div>
      <div className="form-group">
        <label className="input-label">Confusion Lines with Colors:</label>
        {resultUrls.length > 0 && <img
            src={resultUrls[7]}
            alt="Processed result"
            style={{ maxWidth: "300px" }}
        />}
      </div>
      <div className="form-group">
        <label className="input-label">Colors Transformed with Luminance:</label>
        {resultUrls.length > 0 && <img
            src={resultUrls[8]}
            alt="Processed result"
            style={{ maxWidth: "300px" }}
        />}
      </div>
      <div className="form-group">
        <label className="input-label">Dichromat Simulation of Final Image:</label>
        {resultUrls.length > 0 && <img
            src={resultUrls[9]}
            alt="Processed result"
            style={{ maxWidth: "300px" }}
        />}
      </div>
    </div>
  );
}

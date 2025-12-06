"use client";

import { useState } from "react";

export default function KeyColorExtraction() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [blindness, setBlindness] = useState("deutan");
  const [resultUrl, setResultUrl] = useState<string | null>(null);
  const [inputUrl, setInputUrl] = useState<string | null>(null);

  const handleUpload = async () => {
    console.log("Uploading");
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append("image", selectedFile);

    const res = await fetch(`http://localhost:5000/rep_colors`, {
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
      <input
        type="file"
        accept="image/*"
        onChange={handleFileChange}
      />

      <select
          value={blindness}
          onChange={(e) => setBlindness(e.target.value)}
        >
          <option value="protan">Protanopia</option>
          <option value="deutan">Deuteranopia</option>
      </select>

      <div>
        <button onClick={handleUpload}>Upload</button>
      </div>

      {resultUrl && (
        <div>
          <h3>Original Image: </h3>
          <img
            src={inputUrl!!}
            alt="Input result"
            style={{ maxWidth: "300px" }}
          />
          <h3>Representative Colors of Image:</h3>
          <img
            src={resultUrl}
            alt="Processed result"
            style={{ maxWidth: "300px" }}
          />
        </div>
      )}
    </div>
  );
}

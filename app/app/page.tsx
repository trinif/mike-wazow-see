"use client";

import { useState } from "react";
import DichromatSimulation from "../components/DichromatSimulation";
import KeyColorExtraction from "../components/KeyColorExtraction";
import FullImageRecoloring from "../components/FullImageRecoloring";

export default function Page() {
  const [tab, setTab] = useState("dichromat");
  return (
    <main style={{ padding: "2rem" }}>
      <h1>Image Recoloring</h1>
      {/* ----- Tabs  ----- */}
      <div className="tabs">
        <button
          onClick={() => setTab("dichromat")}
          className={tab === "dichromat" ? "tab-active" : "tab-inactive"}
        >
          Dichromat Simulation
        </button>

        <button
          onClick={() => setTab("recoloring")}
          className={tab === "recoloring" ? "tab-active" : "tab-inactive"}
        >
          Full Image Recoloring
        </button>
      </div>
      {/* ---- Content ---- */}
      <div style={{ marginTop: "2rem" }}>
        {tab === "dichromat" && <DichromatSimulation />}
        {tab === "recoloring" && <FullImageRecoloring />}
      </div>
    </main>
  );
}

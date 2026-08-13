import { useState } from "react";
import type { FormEvent } from "react";
import type { AssessmentRequest } from "../types";

interface PresetLocation {
  label: string;
  lat: number;
  lon: number;
}

const PRESETS: PresetLocation[] = [
  { label: "Phoenix, AZ (hot & sunny)", lat: 33.4484, lon: -112.074 },
  { label: "Seattle, WA (wet & windy)", lat: 47.6062, lon: -122.3321 },
  { label: "Denver, CO (high plains)", lat: 39.7392, lon: -104.9903 },
  { label: "Miami, FL (coastal humid)", lat: 25.7617, lon: -80.1918 },
];

interface Props {
  onSubmit: (payload: AssessmentRequest) => void;
  isSubmitting: boolean;
}

export default function LocationForm({ onSubmit, isSubmitting }: Props) {
  const [siteName, setSiteName] = useState("");
  const [lat, setLat] = useState(33.4484);
  const [lon, setLon] = useState(-112.074);
  const [panelArea, setPanelArea] = useState(20);
  const [rotorArea, setRotorArea] = useState(10);
  const [hubHeight, setHubHeight] = useState(20);

  function applyPreset(preset: PresetLocation) {
    setLat(preset.lat);
    setLon(preset.lon);
    setSiteName(preset.label.split(" (")[0]);
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    onSubmit({
      lat,
      lon,
      site_name: siteName || undefined,
      panel_area_m2: panelArea,
      turbine_rotor_area_m2: rotorArea,
      turbine_hub_height_m: hubHeight,
    });
  }

  return (
    <form className="card" onSubmit={handleSubmit}>
      <h2>Assess a site</h2>

      <div className="preset-row">
        {PRESETS.map((preset) => (
          <button
            type="button"
            key={preset.label}
            className="preset-button"
            onClick={() => applyPreset(preset)}
          >
            {preset.label}
          </button>
        ))}
      </div>

      <label>
        Site name
        <input value={siteName} onChange={(e) => setSiteName(e.target.value)} placeholder="Optional" />
      </label>

      <div className="field-row">
        <label>
          Latitude
          <input
            type="number"
            step="0.0001"
            value={lat}
            onChange={(e) => setLat(Number(e.target.value))}
            required
          />
        </label>
        <label>
          Longitude
          <input
            type="number"
            step="0.0001"
            value={lon}
            onChange={(e) => setLon(Number(e.target.value))}
            required
          />
        </label>
      </div>

      <div className="field-row">
        <label>
          Panel area (m²)
          <input
            type="number"
            min="1"
            value={panelArea}
            onChange={(e) => setPanelArea(Number(e.target.value))}
            required
          />
        </label>
        <label>
          Rotor area (m²)
          <input
            type="number"
            min="1"
            value={rotorArea}
            onChange={(e) => setRotorArea(Number(e.target.value))}
            required
          />
        </label>
        <label>
          Hub height (m)
          <input
            type="number"
            min="1"
            value={hubHeight}
            onChange={(e) => setHubHeight(Number(e.target.value))}
            required
          />
        </label>
      </div>

      <button type="submit" className="primary-button" disabled={isSubmitting}>
        {isSubmitting ? "Assessing…" : "Run assessment"}
      </button>
    </form>
  );
}

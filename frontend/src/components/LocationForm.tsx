import { useState } from "react";
import type { FormEvent } from "react";
import PlaceSearch from "./PlaceSearch";
import type { AssessmentRequest, PlaceSuggestion } from "../types";

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

  const [showSavingsFields, setShowSavingsFields] = useState(false);
  const [electricityPrice, setElectricityPrice] = useState("");
  const [currencySymbol, setCurrencySymbol] = useState("$");
  const [systemCost, setSystemCost] = useState("");
  const [gridIntensity, setGridIntensity] = useState("");

  function applyPreset(preset: PresetLocation) {
    setLat(preset.lat);
    setLon(preset.lon);
    setSiteName(preset.label.split(" (")[0]);
  }

  function applyPlace(place: PlaceSuggestion) {
    setLat(place.lat);
    setLon(place.lon);
    setSiteName(place.name);
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const price = parseFloat(electricityPrice);
    const cost = parseFloat(systemCost);
    const intensity = parseFloat(gridIntensity);

    onSubmit({
      lat,
      lon,
      site_name: siteName || undefined,
      panel_area_m2: panelArea,
      turbine_rotor_area_m2: rotorArea,
      turbine_hub_height_m: hubHeight,
      electricity_price_per_kwh: Number.isFinite(price) ? price : undefined,
      currency_symbol: currencySymbol || undefined,
      system_cost: Number.isFinite(cost) ? cost : undefined,
      grid_intensity_kg_per_kwh: Number.isFinite(intensity) ? intensity : undefined,
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

      <PlaceSearch onSelect={applyPlace} />

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

      <button
        type="button"
        className="text-button toggle-savings"
        onClick={() => setShowSavingsFields((v) => !v)}
      >
        {showSavingsFields ? "− Hide" : "+ Add"} local pricing &amp; grid details (optional)
      </button>

      {showSavingsFields && (
        <div className="field-row">
          <label>
            Price / kWh
            <input
              type="number"
              min="0"
              step="0.01"
              value={electricityPrice}
              onChange={(e) => setElectricityPrice(e.target.value)}
              placeholder="e.g. 0.15"
            />
          </label>
          <label>
            Currency symbol
            <input
              value={currencySymbol}
              onChange={(e) => setCurrencySymbol(e.target.value)}
              placeholder="$, €, ₹, ..."
              maxLength={6}
            />
          </label>
          <label>
            System cost (optional)
            <input
              type="number"
              min="0"
              value={systemCost}
              onChange={(e) => setSystemCost(e.target.value)}
              placeholder="for payback estimate"
            />
          </label>
          <label>
            Grid intensity (kg CO₂/kWh)
            <input
              type="number"
              min="0"
              step="0.01"
              value={gridIntensity}
              onChange={(e) => setGridIntensity(e.target.value)}
              placeholder="0.475 (global avg)"
            />
          </label>
        </div>
      )}

      <button type="submit" className="primary-button" disabled={isSubmitting}>
        {isSubmitting ? "Assessing…" : "Run assessment"}
      </button>
    </form>
  );
}

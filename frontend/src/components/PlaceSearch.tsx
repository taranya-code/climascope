import { useState } from "react";
import type { FormEvent } from "react";
import { searchPlaces } from "../api/client";
import type { PlaceSuggestion } from "../types";

interface Props {
  onSelect: (place: PlaceSuggestion) => void;
}

function formatPlace(place: PlaceSuggestion): string {
  return [place.name, place.admin1, place.country].filter(Boolean).join(", ");
}

export default function PlaceSearch({ onSelect }: Props) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<PlaceSuggestion[] | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLocating, setIsLocating] = useState(false);

  async function handleSearch(event: FormEvent) {
    event.preventDefault();
    if (!query.trim()) return;

    setIsSearching(true);
    setError(null);
    try {
      const places = await searchPlaces(query.trim());
      setResults(places);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Search failed");
      setResults(null);
    } finally {
      setIsSearching(false);
    }
  }

  function handleSelect(place: PlaceSuggestion) {
    onSelect(place);
    setResults(null);
    setError(null);
    setQuery(formatPlace(place));
  }

  function handleUseMyLocation() {
    if (!navigator.geolocation) {
      setError("Geolocation isn't supported by this browser.");
      return;
    }

    setIsLocating(true);
    setError(null);
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setIsLocating(false);
        handleSelect({
          name: "My current location",
          country: null,
          admin1: null,
          lat: Number(position.coords.latitude.toFixed(5)),
          lon: Number(position.coords.longitude.toFixed(5)),
        });
      },
      (geoError) => {
        setIsLocating(false);
        setError(
          geoError.code === geoError.PERMISSION_DENIED
            ? "Location permission denied — search for a place instead, or enter coordinates manually."
            : "Couldn't determine your location — search for a place instead.",
        );
      },
      { timeout: 10_000, maximumAge: 5 * 60_000 },
    );
  }

  return (
    <div className="place-search">
      <label>
        Search for a place (any city, anywhere)
        <div className="search-row">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g. Nairobi, São Paulo, Chiang Mai"
          />
          <button type="button" className="secondary-button" onClick={handleSearch} disabled={isSearching}>
            {isSearching ? "…" : "Search"}
          </button>
        </div>
      </label>

      <button
        type="button"
        className="text-button locate-button"
        onClick={handleUseMyLocation}
        disabled={isLocating}
      >
        {isLocating ? "Locating…" : "📍 Use my current location"}
      </button>

      {error && <p className="muted error-text">{error}</p>}

      {results && (
        <ul className="search-results">
          {results.length === 0 ? (
            <li className="muted">No matches found.</li>
          ) : (
            results.map((place, i) => (
              <li key={`${place.name}-${place.lat}-${place.lon}-${i}`}>
                <button type="button" className="search-result-button" onClick={() => handleSelect(place)}>
                  {formatPlace(place)}
                </button>
              </li>
            ))
          )}
        </ul>
      )}
    </div>
  );
}

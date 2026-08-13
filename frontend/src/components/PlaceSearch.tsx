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
    setQuery(formatPlace(place));
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

"""Client for Open-Meteo's free, keyless global geocoding API.

Docs: https://open-meteo.com/en/docs/geocoding-api

Lets a user type a place name ("Nairobi", "Chiang Mai", "Porto Alegre")
instead of needing to already know its latitude/longitude -- this is what
makes the app usable by someone anywhere in the world, not just people who
know how to look up coordinates. Global gazetteer, no API key or account
required, same no-secrets-management rationale as the NASA POWER client.
"""

from dataclasses import dataclass

import httpx

BASE_URL = "https://geocoding-api.open-meteo.com/v1/search"
REQUEST_TIMEOUT_S = 10.0
DEFAULT_RESULT_LIMIT = 5


class GeocodingError(RuntimeError):
    """Raised when the geocoding API is unreachable or returns unexpected data."""


@dataclass(frozen=True)
class PlaceResult:
    name: str
    country: str | None
    admin1: str | None
    lat: float
    lon: float


def search_places(
    query: str,
    limit: int = DEFAULT_RESULT_LIMIT,
    http_client: httpx.Client | None = None,
) -> list[PlaceResult]:
    """Search for places by (partial) name. Returns an empty list for no matches."""
    query = query.strip()
    if not query:
        raise ValueError("query must not be empty")
    if limit <= 0:
        raise ValueError("limit must be positive")

    params = {"name": query, "count": limit, "language": "en", "format": "json"}

    owns_client = http_client is None
    client = http_client or httpx.Client(timeout=REQUEST_TIMEOUT_S)
    try:
        response = client.get(BASE_URL, params=params)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise GeocodingError(f"Failed to reach geocoding API: {exc}") from exc
    finally:
        if owns_client:
            client.close()

    try:
        raw_results = response.json().get("results", [])
    except ValueError as exc:
        raise GeocodingError("Unexpected geocoding API response shape") from exc

    try:
        return [
            PlaceResult(
                name=item["name"],
                country=item.get("country"),
                admin1=item.get("admin1"),
                lat=float(item["latitude"]),
                lon=float(item["longitude"]),
            )
            for item in raw_results
        ]
    except (KeyError, TypeError, ValueError) as exc:
        raise GeocodingError("Unexpected geocoding API result shape") from exc

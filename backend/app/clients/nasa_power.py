"""Client for NASA's free, keyless POWER climatology API.

Docs: https://power.larc.nasa.gov/docs/services/api/temporal/climatology/

Returns 30-year monthly-average climate normals for a lat/lon point. No API
key or account is required, which is what makes it usable in a public-facing
tool like this one without any secrets management.

Note on units: PRECTOTCORR is NASA's bias-corrected precipitation parameter,
returned here as mean daily precipitation (mm/day) *for each month* -- not a
monthly total. The climate_risk module's variability index only cares about
the relative spread across months, so this unit choice doesn't affect it.
"""

from dataclasses import dataclass

import httpx

BASE_URL = "https://power.larc.nasa.gov/api/temporal/climatology/point"
PARAMETERS = ("ALLSKY_SFC_SW_DWN", "T2M", "T2M_MAX", "WS10M", "PRECTOTCORR")
MONTH_KEYS = ("JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC")
REQUEST_TIMEOUT_S = 15.0


class NasaPowerError(RuntimeError):
    """Raised when the NASA POWER API is unreachable or returns unexpected data."""


@dataclass(frozen=True)
class ClimatologyData:
    avg_irradiance_kwh_m2_day: float
    avg_wind_speed_10m_ms: float
    monthly_max_temps_c: list[float]
    monthly_mean_temps_c: list[float]
    monthly_precip_mm_day: list[float]


def _extract_monthly(parameter_block: dict, parameter_name: str) -> list[float]:
    try:
        series = parameter_block[parameter_name]
        return [float(series[month]) for month in MONTH_KEYS]
    except (KeyError, TypeError, ValueError) as exc:
        raise NasaPowerError(
            f"Missing or malformed '{parameter_name}' in NASA POWER response"
        ) from exc


def fetch_climatology(lat: float, lon: float, http_client: httpx.Client | None = None) -> ClimatologyData:
    """Fetch and reshape climatology normals for a point.

    Accepts an optional pre-built `http_client` so tests can inject a stub
    without any real network access, and so callers can share a connection
    pool across multiple requests.
    """
    if not (-90 <= lat <= 90):
        raise ValueError("lat must be between -90 and 90")
    if not (-180 <= lon <= 180):
        raise ValueError("lon must be between -180 and 180")

    params = {
        "parameters": ",".join(PARAMETERS),
        "community": "RE",
        "longitude": lon,
        "latitude": lat,
        "format": "JSON",
    }

    owns_client = http_client is None
    client = http_client or httpx.Client(timeout=REQUEST_TIMEOUT_S)
    try:
        response = client.get(BASE_URL, params=params)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise NasaPowerError(f"Failed to reach NASA POWER API: {exc}") from exc
    finally:
        if owns_client:
            client.close()

    try:
        parameter_block = response.json()["properties"]["parameter"]
    except (KeyError, ValueError, TypeError) as exc:
        raise NasaPowerError("Unexpected NASA POWER response shape") from exc

    monthly_irradiance = _extract_monthly(parameter_block, "ALLSKY_SFC_SW_DWN")
    monthly_wind = _extract_monthly(parameter_block, "WS10M")

    return ClimatologyData(
        avg_irradiance_kwh_m2_day=round(sum(monthly_irradiance) / 12, 3),
        avg_wind_speed_10m_ms=round(sum(monthly_wind) / 12, 3),
        monthly_max_temps_c=_extract_monthly(parameter_block, "T2M_MAX"),
        monthly_mean_temps_c=_extract_monthly(parameter_block, "T2M"),
        monthly_precip_mm_day=_extract_monthly(parameter_block, "PRECTOTCORR"),
    )

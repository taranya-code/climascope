"""Solar PV energy potential from average irradiance.

Formula: daily_kWh = panel_area_m2 * irradiance_kwh_m2_day * efficiency * performance_ratio

`efficiency` is the panel's rated conversion efficiency (fraction of incident
sunlight converted to DC electricity). `performance_ratio` (PR) captures the
real-world losses a rated efficiency doesn't: inverter conversion, wiring,
temperature derating, soiling, shading. 0.75 is a widely used industry default
for a well-sited residential/commercial array.
"""

DEFAULT_PANEL_EFFICIENCY = 0.20
DEFAULT_PERFORMANCE_RATIO = 0.75
DAYS_PER_YEAR = 365


def solar_potential(
    panel_area_m2: float,
    avg_irradiance_kwh_m2_day: float,
    efficiency: float = DEFAULT_PANEL_EFFICIENCY,
    performance_ratio: float = DEFAULT_PERFORMANCE_RATIO,
) -> dict:
    if panel_area_m2 <= 0:
        raise ValueError("panel_area_m2 must be positive")
    if avg_irradiance_kwh_m2_day < 0:
        raise ValueError("avg_irradiance_kwh_m2_day cannot be negative")
    if not (0 < efficiency <= 1):
        raise ValueError("efficiency must be between 0 and 1")
    if not (0 < performance_ratio <= 1):
        raise ValueError("performance_ratio must be between 0 and 1")

    daily_kwh = panel_area_m2 * avg_irradiance_kwh_m2_day * efficiency * performance_ratio
    annual_kwh = daily_kwh * DAYS_PER_YEAR

    return {
        "daily_kwh": round(daily_kwh, 2),
        "annual_kwh": round(annual_kwh, 2),
        "efficiency": efficiency,
        "performance_ratio": performance_ratio,
    }

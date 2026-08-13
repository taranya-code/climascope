"""Small wind turbine energy potential from average 10m wind speed.

Two-step model:
1. Extrapolate the measured 10m wind speed to hub height using the wind
   power law (Hellmann exponent alpha=1/7, standard for open/suburban terrain).
2. Apply the wind power equation P = 0.5 * rho * A * v^3 * Cp to get instantaneous
   power, then integrate over a day/year.

Known simplification: using the *average* wind speed cubed underestimates true
energy yield, since power scales with v^3 and wind speed distributions are
right-skewed (Jensen's inequality: E[v^3] > E[v]^3). A production model would
use a full Weibull distribution instead of a single average. Documented here
rather than silently baked in, since it's a natural follow-up question.
"""

AIR_DENSITY_KG_M3 = 1.225
DEFAULT_POWER_COEFFICIENT = 0.35  # realistic achievable Cp; Betz limit is ~0.593
WIND_SHEAR_EXPONENT = 1 / 7
REFERENCE_HEIGHT_M = 10.0
DAYS_PER_YEAR = 365

_WIND_CLASS_BANDS = (
    (4.0, "poor"),
    (5.6, "marginal"),
    (7.0, "good"),
    (8.8, "excellent"),
)


def extrapolate_wind_speed(
    speed_at_10m_ms: float,
    hub_height_m: float,
    shear_exponent: float = WIND_SHEAR_EXPONENT,
) -> float:
    if speed_at_10m_ms < 0:
        raise ValueError("speed_at_10m_ms cannot be negative")
    if hub_height_m <= 0:
        raise ValueError("hub_height_m must be positive")

    return speed_at_10m_ms * (hub_height_m / REFERENCE_HEIGHT_M) ** shear_exponent


def classify_wind_class(hub_height_speed_ms: float) -> str:
    for threshold, label in _WIND_CLASS_BANDS:
        if hub_height_speed_ms < threshold:
            return label
    return "outstanding"


def wind_potential(
    rotor_area_m2: float,
    avg_wind_speed_10m_ms: float,
    hub_height_m: float,
    power_coefficient: float = DEFAULT_POWER_COEFFICIENT,
) -> dict:
    if rotor_area_m2 <= 0:
        raise ValueError("rotor_area_m2 must be positive")
    if not (0 < power_coefficient <= 0.593):
        raise ValueError("power_coefficient must be between 0 and the Betz limit (0.593)")

    hub_speed = extrapolate_wind_speed(avg_wind_speed_10m_ms, hub_height_m)
    power_watts = 0.5 * AIR_DENSITY_KG_M3 * rotor_area_m2 * hub_speed**3 * power_coefficient
    daily_kwh = (power_watts * 24) / 1000
    annual_kwh = daily_kwh * DAYS_PER_YEAR

    return {
        "hub_height_wind_speed_ms": round(hub_speed, 3),
        "daily_kwh": round(daily_kwh, 2),
        "annual_kwh": round(annual_kwh, 2),
        "wind_class": classify_wind_class(hub_speed),
    }

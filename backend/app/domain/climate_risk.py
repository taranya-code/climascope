"""Climate risk indicators derived from monthly climatology normals.

All three functions take 12 monthly values (Jan..Dec) as produced by NASA
POWER's climatology endpoint and turn them into interpretable annual metrics:

- heat_stress_days: estimated days/year where peak temperature is dangerously
  high. Coarse by design (a month is counted as fully "in stress" once its
  mean daily max crosses the threshold) since only monthly-mean data is
  available here; a finer model would need daily records.
- degree_days: standard HVAC sizing metric, base 18C (65F).
- precipitation_variability_index: coefficient of variation of monthly
  precipitation. High values indicate a rainfall pattern concentrated into
  a few months rather than spread evenly -- a proxy for drought/flood risk.
"""

import statistics

DEGREE_DAY_BASE_C = 18.0
DEFAULT_HEAT_STRESS_THRESHOLD_C = 35.0
AVG_DAYS_PER_MONTH = 30.4368


def _validate_monthly(values: list[float], name: str) -> None:
    if len(values) != 12:
        raise ValueError(f"{name} must contain exactly 12 monthly values")


def heat_stress_days(
    monthly_max_temps_c: list[float],
    threshold_c: float = DEFAULT_HEAT_STRESS_THRESHOLD_C,
) -> float:
    _validate_monthly(monthly_max_temps_c, "monthly_max_temps_c")
    months_over_threshold = sum(1 for t in monthly_max_temps_c if t >= threshold_c)
    return round(months_over_threshold * AVG_DAYS_PER_MONTH, 1)


def degree_days(monthly_mean_temps_c: list[float], base_c: float = DEGREE_DAY_BASE_C) -> dict:
    _validate_monthly(monthly_mean_temps_c, "monthly_mean_temps_c")

    cooling = sum(max(0.0, t - base_c) * AVG_DAYS_PER_MONTH for t in monthly_mean_temps_c)
    heating = sum(max(0.0, base_c - t) * AVG_DAYS_PER_MONTH for t in monthly_mean_temps_c)

    return {
        "cooling_degree_days": round(cooling, 1),
        "heating_degree_days": round(heating, 1),
    }


def precipitation_variability_index(monthly_precip_mm: list[float]) -> float:
    _validate_monthly(monthly_precip_mm, "monthly_precip_mm")

    mean = statistics.mean(monthly_precip_mm)
    if mean == 0:
        return 0.0

    stdev = statistics.pstdev(monthly_precip_mm)
    return round(stdev / mean, 3)


def climate_risk_profile(
    monthly_max_temps_c: list[float],
    monthly_mean_temps_c: list[float],
    monthly_precip_mm: list[float],
    heat_threshold_c: float = DEFAULT_HEAT_STRESS_THRESHOLD_C,
) -> dict:
    dd = degree_days(monthly_mean_temps_c)

    return {
        "heat_stress_days_per_year": heat_stress_days(monthly_max_temps_c, heat_threshold_c),
        "cooling_degree_days": dd["cooling_degree_days"],
        "heating_degree_days": dd["heating_degree_days"],
        "precipitation_variability_index": precipitation_variability_index(monthly_precip_mm),
    }

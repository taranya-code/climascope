"""Estimated cost savings and payback period from renewable energy output.

Deliberately currency-agnostic: callers supply a local electricity price per
kWh (and, on the API surface, a currency symbol used only for display), not
this module assuming USD. Electricity prices and currencies vary enormously
by country -- from a few cents to well over 40 cents per kWh -- so hardcoding
a currency would make the feature useless for most of the world.
"""


def estimate_savings(solar_annual_kwh: float, wind_annual_kwh: float, price_per_kwh: float) -> dict:
    if solar_annual_kwh < 0 or wind_annual_kwh < 0:
        raise ValueError("annual kwh values cannot be negative")
    if price_per_kwh < 0:
        raise ValueError("price_per_kwh cannot be negative")

    total_annual_kwh = solar_annual_kwh + wind_annual_kwh
    annual_savings = total_annual_kwh * price_per_kwh
    monthly_savings = annual_savings / 12

    return {
        "total_annual_kwh": round(total_annual_kwh, 2),
        "annual_savings": round(annual_savings, 2),
        "monthly_savings": round(monthly_savings, 2),
    }


def simple_payback_years(system_cost: float | None, annual_savings: float) -> float | None:
    """Years to recoup `system_cost` at a constant `annual_savings` rate.

    Returns None when payback isn't meaningful: no cost was given, or savings
    are zero/negative so the system would never pay for itself under this
    simple (non-discounted, no-degradation) model.
    """
    if system_cost is None:
        return None
    if system_cost < 0:
        raise ValueError("system_cost cannot be negative")
    if annual_savings <= 0:
        return None

    return round(system_cost / annual_savings, 1)

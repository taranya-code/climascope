"""Combines solar/wind potential and climate risk into ranked recommendations.

This is the synthesis layer: none of the individual numbers (kWh/year, degree
days, variability index) tell a site owner what to *do*. Each rule below pairs
a single signal with a concrete adaptation action; priority 1 = renewable
opportunities (revenue/savings), priority 2 = risk mitigation (resilience),
priority 3 = fallback when nothing crosses a threshold.

Thresholds are simplifying assumptions, not calibrated against real adoption
data -- an obvious discussion point for a review of this code.
"""

from dataclasses import dataclass, asdict

SOLAR_ANNUAL_KWH_GOOD_THRESHOLD = 2000.0
WIND_ANNUAL_KWH_GOOD_THRESHOLD = 8000.0
HEAT_STRESS_DAYS_HIGH_THRESHOLD = 60.0
PRECIP_VARIABILITY_HIGH_THRESHOLD = 0.5


@dataclass(frozen=True)
class Recommendation:
    title: str
    rationale: str
    priority: int  # 1 = highest


def rank_recommendations(solar: dict, wind: dict, risk: dict) -> list[dict]:
    recs: list[Recommendation] = []

    if solar["annual_kwh"] >= SOLAR_ANNUAL_KWH_GOOD_THRESHOLD:
        recs.append(
            Recommendation(
                title="Prioritize solar PV installation",
                rationale=(
                    f"Estimated {solar['annual_kwh']:.0f} kWh/year exceeds the "
                    f"{SOLAR_ANNUAL_KWH_GOOD_THRESHOLD:.0f} kWh/year viability threshold."
                ),
                priority=1,
            )
        )

    if wind["annual_kwh"] >= WIND_ANNUAL_KWH_GOOD_THRESHOLD:
        recs.append(
            Recommendation(
                title="Evaluate small wind turbine installation",
                rationale=(
                    f"Wind class '{wind['wind_class']}' with an estimated "
                    f"{wind['annual_kwh']:.0f} kWh/year output."
                ),
                priority=1,
            )
        )

    if risk["heat_stress_days_per_year"] >= HEAT_STRESS_DAYS_HIGH_THRESHOLD:
        recs.append(
            Recommendation(
                title="Invest in passive cooling / reflective roofing",
                rationale=(
                    f"{risk['heat_stress_days_per_year']:.0f} estimated heat-stress days/year "
                    "indicates high cooling demand and heat-health risk."
                ),
                priority=2,
            )
        )

    if risk["precipitation_variability_index"] >= PRECIP_VARIABILITY_HIGH_THRESHOLD:
        recs.append(
            Recommendation(
                title="Add rainwater harvesting / drought-resilient landscaping",
                rationale=(
                    f"Precipitation variability index of {risk['precipitation_variability_index']:.2f} "
                    "indicates an inconsistent, drought-prone rainfall pattern."
                ),
                priority=2,
            )
        )

    if not recs:
        recs.append(
            Recommendation(
                title="No high-priority interventions identified",
                rationale="Renewable potential and climate risk are both within moderate ranges for this site.",
                priority=3,
            )
        )

    recs.sort(key=lambda r: r.priority)
    return [asdict(r) for r in recs]

from app.domain.adaptation import rank_recommendations

GOOD_SOLAR = {"annual_kwh": 3000}
POOR_SOLAR = {"annual_kwh": 500}
GOOD_WIND = {"annual_kwh": 10000, "wind_class": "excellent"}
POOR_WIND = {"annual_kwh": 1000, "wind_class": "poor"}
HIGH_HEAT_RISK = {"heat_stress_days_per_year": 90, "precipitation_variability_index": 0.1}
LOW_RISK = {"heat_stress_days_per_year": 5, "precipitation_variability_index": 0.1}
HIGH_PRECIP_RISK = {"heat_stress_days_per_year": 5, "precipitation_variability_index": 0.7}


def test_recommends_solar_when_potential_is_good():
    recs = rank_recommendations(GOOD_SOLAR, POOR_WIND, LOW_RISK)
    titles = [r["title"] for r in recs]
    assert "Prioritize solar PV installation" in titles


def test_recommends_wind_when_potential_is_good():
    recs = rank_recommendations(POOR_SOLAR, GOOD_WIND, LOW_RISK)
    titles = [r["title"] for r in recs]
    assert "Evaluate small wind turbine installation" in titles


def test_recommends_cooling_measures_under_high_heat_risk():
    recs = rank_recommendations(POOR_SOLAR, POOR_WIND, HIGH_HEAT_RISK)
    titles = [r["title"] for r in recs]
    assert "Invest in passive cooling / reflective roofing" in titles


def test_recommends_rainwater_harvesting_under_high_precip_variability():
    recs = rank_recommendations(POOR_SOLAR, POOR_WIND, HIGH_PRECIP_RISK)
    titles = [r["title"] for r in recs]
    assert "Add rainwater harvesting / drought-resilient landscaping" in titles


def test_renewable_recommendations_outrank_risk_recommendations():
    recs = rank_recommendations(GOOD_SOLAR, POOR_WIND, HIGH_HEAT_RISK)
    priorities = [r["priority"] for r in recs]
    assert priorities == sorted(priorities)
    assert recs[0]["title"] == "Prioritize solar PV installation"


def test_fallback_recommendation_when_nothing_crosses_threshold():
    recs = rank_recommendations(POOR_SOLAR, POOR_WIND, LOW_RISK)
    assert len(recs) == 1
    assert recs[0]["title"] == "No high-priority interventions identified"


def test_every_recommendation_has_a_rationale():
    recs = rank_recommendations(GOOD_SOLAR, GOOD_WIND, HIGH_HEAT_RISK)
    assert all(r["rationale"] for r in recs)

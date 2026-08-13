import pytest

from app.domain.climate_risk import (
    climate_risk_profile,
    degree_days,
    heat_stress_days,
    precipitation_variability_index,
)

MONTHLY_MAX_TEMPS_C = [20, 22, 25, 30, 35, 38, 40, 39, 36, 30, 24, 20]
MONTHLY_MEAN_TEMPS_C = [10, 12, 15, 20, 25, 28, 30, 29, 26, 20, 15, 10]
MONTHLY_PRECIP_MM = [50, 45, 60, 70, 90, 100, 110, 105, 95, 80, 60, 50]


def test_heat_stress_days_counts_months_over_threshold():
    # 5 of 12 months (35, 38, 40, 39, 36) are >= the 35C default threshold
    assert heat_stress_days(MONTHLY_MAX_TEMPS_C) == pytest.approx(152.2)


def test_heat_stress_days_zero_when_all_months_mild():
    mild = [15] * 12
    assert heat_stress_days(mild) == 0


def test_degree_days_matches_hand_calculation():
    result = degree_days(MONTHLY_MEAN_TEMPS_C)

    assert result["cooling_degree_days"] == pytest.approx(1582.7)
    assert result["heating_degree_days"] == pytest.approx(852.2)


def test_precipitation_variability_index_matches_hand_calculation():
    assert precipitation_variability_index(MONTHLY_PRECIP_MM) == pytest.approx(0.293)


def test_precipitation_variability_index_zero_for_constant_rainfall():
    assert precipitation_variability_index([50] * 12) == 0.0


def test_climate_risk_profile_combines_all_three_metrics():
    profile = climate_risk_profile(MONTHLY_MAX_TEMPS_C, MONTHLY_MEAN_TEMPS_C, MONTHLY_PRECIP_MM)

    assert profile == {
        "heat_stress_days_per_year": pytest.approx(152.2),
        "cooling_degree_days": pytest.approx(1582.7),
        "heating_degree_days": pytest.approx(852.2),
        "precipitation_variability_index": pytest.approx(0.293),
    }


@pytest.mark.parametrize(
    "fn,args",
    [
        (heat_stress_days, ([20] * 11,)),
        (degree_days, ([20] * 13,)),
        (precipitation_variability_index, ([20] * 5,)),
    ],
)
def test_rejects_non_12_month_input(fn, args):
    with pytest.raises(ValueError):
        fn(*args)

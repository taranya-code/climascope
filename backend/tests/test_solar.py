import pytest

from app.domain.solar import solar_potential


def test_solar_potential_matches_hand_calculation():
    result = solar_potential(panel_area_m2=10, avg_irradiance_kwh_m2_day=5.5)

    assert result["daily_kwh"] == pytest.approx(8.25)
    assert result["annual_kwh"] == pytest.approx(3011.25)
    assert result["efficiency"] == 0.20
    assert result["performance_ratio"] == 0.75


def test_solar_potential_scales_linearly_with_area():
    small = solar_potential(panel_area_m2=5, avg_irradiance_kwh_m2_day=5.5)
    large = solar_potential(panel_area_m2=10, avg_irradiance_kwh_m2_day=5.5)

    assert large["daily_kwh"] == pytest.approx(small["daily_kwh"] * 2, abs=0.01)


def test_solar_potential_zero_irradiance_yields_zero_output():
    result = solar_potential(panel_area_m2=10, avg_irradiance_kwh_m2_day=0)

    assert result["daily_kwh"] == 0
    assert result["annual_kwh"] == 0


@pytest.mark.parametrize(
    "kwargs",
    [
        {"panel_area_m2": 0, "avg_irradiance_kwh_m2_day": 5},
        {"panel_area_m2": -5, "avg_irradiance_kwh_m2_day": 5},
        {"panel_area_m2": 10, "avg_irradiance_kwh_m2_day": -1},
        {"panel_area_m2": 10, "avg_irradiance_kwh_m2_day": 5, "efficiency": 0},
        {"panel_area_m2": 10, "avg_irradiance_kwh_m2_day": 5, "efficiency": 1.5},
        {"panel_area_m2": 10, "avg_irradiance_kwh_m2_day": 5, "performance_ratio": 0},
    ],
)
def test_solar_potential_rejects_invalid_inputs(kwargs):
    with pytest.raises(ValueError):
        solar_potential(**kwargs)

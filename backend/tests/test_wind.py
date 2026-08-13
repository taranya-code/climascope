import pytest

from app.domain.wind import (
    classify_wind_class,
    extrapolate_wind_speed,
    wind_potential,
)


def test_extrapolate_wind_speed_no_change_at_reference_height():
    assert extrapolate_wind_speed(6.0, hub_height_m=10.0) == pytest.approx(6.0)


def test_extrapolate_wind_speed_increases_with_height():
    result = extrapolate_wind_speed(5.0, hub_height_m=30.0)
    assert result == pytest.approx(5.85, abs=0.01)


@pytest.mark.parametrize(
    "speed,expected_class",
    [(3.0, "poor"), (5.0, "marginal"), (6.5, "good"), (8.0, "excellent"), (10.0, "outstanding")],
)
def test_classify_wind_class_bands(speed, expected_class):
    assert classify_wind_class(speed) == expected_class


def test_wind_potential_matches_hand_calculation():
    result = wind_potential(rotor_area_m2=50, avg_wind_speed_10m_ms=6.0, hub_height_m=10.0)

    assert result["hub_height_wind_speed_ms"] == pytest.approx(6.0)
    assert result["daily_kwh"] == pytest.approx(55.57, abs=0.01)
    assert result["annual_kwh"] == pytest.approx(20281.59, abs=0.5)
    assert result["wind_class"] == "good"


def test_wind_potential_is_cubic_in_wind_speed():
    slow = wind_potential(rotor_area_m2=50, avg_wind_speed_10m_ms=4.0, hub_height_m=10.0)
    fast = wind_potential(rotor_area_m2=50, avg_wind_speed_10m_ms=8.0, hub_height_m=10.0)

    # doubling wind speed should ~8x the power output (P ~ v^3)
    assert fast["daily_kwh"] == pytest.approx(slow["daily_kwh"] * 8, abs=0.1)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"rotor_area_m2": 0, "avg_wind_speed_10m_ms": 5, "hub_height_m": 10},
        {"rotor_area_m2": 50, "avg_wind_speed_10m_ms": -1, "hub_height_m": 10},
        {"rotor_area_m2": 50, "avg_wind_speed_10m_ms": 5, "hub_height_m": 0},
        {"rotor_area_m2": 50, "avg_wind_speed_10m_ms": 5, "hub_height_m": 10, "power_coefficient": 0.6},
    ],
)
def test_wind_potential_rejects_invalid_inputs(kwargs):
    with pytest.raises(ValueError):
        wind_potential(**kwargs)

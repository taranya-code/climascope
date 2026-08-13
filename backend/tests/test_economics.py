import pytest

from app.domain.economics import estimate_savings, simple_payback_years


def test_estimate_savings_matches_hand_calculation():
    result = estimate_savings(solar_annual_kwh=3000, wind_annual_kwh=1000, price_per_kwh=0.15)

    assert result["total_annual_kwh"] == pytest.approx(4000)
    assert result["annual_savings"] == pytest.approx(600)
    assert result["monthly_savings"] == pytest.approx(50)


def test_estimate_savings_is_currency_agnostic_linear_scale():
    cheap = estimate_savings(solar_annual_kwh=1000, wind_annual_kwh=0, price_per_kwh=0.05)
    expensive = estimate_savings(solar_annual_kwh=1000, wind_annual_kwh=0, price_per_kwh=0.50)

    # a 10x higher local price should mean 10x the estimated savings
    assert expensive["annual_savings"] == pytest.approx(cheap["annual_savings"] * 10)


def test_estimate_savings_zero_price_yields_zero_savings():
    result = estimate_savings(solar_annual_kwh=3000, wind_annual_kwh=1000, price_per_kwh=0)
    assert result["annual_savings"] == 0
    assert result["monthly_savings"] == 0


@pytest.mark.parametrize(
    "kwargs",
    [
        {"solar_annual_kwh": -1, "wind_annual_kwh": 0, "price_per_kwh": 0.1},
        {"solar_annual_kwh": 0, "wind_annual_kwh": -1, "price_per_kwh": 0.1},
        {"solar_annual_kwh": 0, "wind_annual_kwh": 0, "price_per_kwh": -0.1},
    ],
)
def test_estimate_savings_rejects_invalid_inputs(kwargs):
    with pytest.raises(ValueError):
        estimate_savings(**kwargs)


def test_simple_payback_years_matches_hand_calculation():
    assert simple_payback_years(system_cost=6000, annual_savings=600) == pytest.approx(10.0)


def test_simple_payback_years_none_when_no_cost_given():
    assert simple_payback_years(system_cost=None, annual_savings=600) is None


def test_simple_payback_years_none_when_savings_not_positive():
    assert simple_payback_years(system_cost=6000, annual_savings=0) is None
    assert simple_payback_years(system_cost=6000, annual_savings=-100) is None


def test_simple_payback_years_rejects_negative_cost():
    with pytest.raises(ValueError):
        simple_payback_years(system_cost=-1, annual_savings=600)

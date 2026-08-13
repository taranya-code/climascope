import pytest

from app.domain.emissions import estimate_co2_avoided


def test_estimate_co2_avoided_uses_global_default_when_unspecified():
    result = estimate_co2_avoided(total_annual_kwh=4000)

    assert result["annual_co2_avoided_kg"] == pytest.approx(1900.0)
    assert result["equivalent_trees_planted"] == pytest.approx(90.5, abs=0.1)


def test_estimate_co2_avoided_matches_hand_calculation_with_custom_intensity():
    # a coal-heavy grid at 0.9 kg CO2/kWh
    result = estimate_co2_avoided(total_annual_kwh=1000, grid_intensity_kg_per_kwh=0.9)

    assert result["annual_co2_avoided_kg"] == pytest.approx(900.0)


def test_estimate_co2_avoided_scales_linearly_with_intensity():
    clean_grid = estimate_co2_avoided(total_annual_kwh=1000, grid_intensity_kg_per_kwh=0.05)
    dirty_grid = estimate_co2_avoided(total_annual_kwh=1000, grid_intensity_kg_per_kwh=0.5)

    # 10x higher grid intensity should mean 10x the CO2 avoided by going renewable
    assert dirty_grid["annual_co2_avoided_kg"] == pytest.approx(clean_grid["annual_co2_avoided_kg"] * 10)


def test_estimate_co2_avoided_zero_output_yields_zero_avoided():
    result = estimate_co2_avoided(total_annual_kwh=0)
    assert result["annual_co2_avoided_kg"] == 0
    assert result["equivalent_trees_planted"] == 0


@pytest.mark.parametrize(
    "kwargs",
    [
        {"total_annual_kwh": -1},
        {"total_annual_kwh": 1000, "grid_intensity_kg_per_kwh": -0.1},
    ],
)
def test_estimate_co2_avoided_rejects_invalid_inputs(kwargs):
    with pytest.raises(ValueError):
        estimate_co2_avoided(**kwargs)

"""CO2 emissions avoided by generating renewable energy instead of drawing
from the local electricity grid.

Grid carbon intensity varies enormously by country -- from under 50 gCO2/kWh
in hydro/nuclear-heavy grids (Norway, France) to over 700 gCO2/kWh in
coal-heavy ones -- so, like the savings estimate, this takes a configurable
intensity rather than assuming one country's mix. Defaults to a global
average (IEA, low-to-mid-2020s figures) when the caller doesn't know their
local number.
"""

GLOBAL_AVERAGE_GRID_INTENSITY_KG_PER_KWH = 0.475
MATURE_TREE_CO2_ABSORPTION_KG_PER_YEAR = 21.0  # commonly cited estimate for a mature tree


def estimate_co2_avoided(
    total_annual_kwh: float,
    grid_intensity_kg_per_kwh: float = GLOBAL_AVERAGE_GRID_INTENSITY_KG_PER_KWH,
) -> dict:
    if total_annual_kwh < 0:
        raise ValueError("total_annual_kwh cannot be negative")
    if grid_intensity_kg_per_kwh < 0:
        raise ValueError("grid_intensity_kg_per_kwh cannot be negative")

    annual_co2_avoided_kg = total_annual_kwh * grid_intensity_kg_per_kwh
    equivalent_trees_planted = annual_co2_avoided_kg / MATURE_TREE_CO2_ABSORPTION_KG_PER_YEAR

    return {
        "annual_co2_avoided_kg": round(annual_co2_avoided_kg, 1),
        "equivalent_trees_planted": round(equivalent_trees_planted, 1),
    }

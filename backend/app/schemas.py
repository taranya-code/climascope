from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PlaceSuggestion(BaseModel):
    name: str
    country: str | None
    admin1: str | None
    lat: float
    lon: float


class SiteCreate(BaseModel):
    name: str
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)


class SiteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    lat: float
    lon: float
    created_at: datetime


class AssessmentRequest(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    site_name: str | None = None
    panel_area_m2: float = Field(gt=0, default=20.0)
    turbine_rotor_area_m2: float = Field(gt=0, default=10.0)
    turbine_hub_height_m: float = Field(gt=0, default=20.0)

    # Optional: lets a user in any country get a savings estimate in their own
    # currency, instead of the app assuming USD.
    electricity_price_per_kwh: float | None = Field(default=None, ge=0)
    currency_symbol: str = Field(default="$", max_length=6)
    system_cost: float | None = Field(default=None, ge=0)


class Recommendation(BaseModel):
    title: str
    rationale: str
    priority: int


class AssessmentReport(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    site_id: int

    panel_area_m2: float
    turbine_rotor_area_m2: float
    turbine_hub_height_m: float

    solar_daily_kwh: float
    solar_annual_kwh: float

    wind_daily_kwh: float
    wind_annual_kwh: float
    wind_class: str
    hub_height_wind_speed_ms: float

    heat_stress_days_per_year: float
    cooling_degree_days: float
    heating_degree_days: float
    precipitation_variability_index: float

    monthly_mean_temps_c: list[float]
    monthly_max_temps_c: list[float]
    monthly_precip_mm_day: list[float]

    currency_symbol: str
    electricity_price_per_kwh: float | None
    estimated_annual_savings: float | None
    estimated_monthly_savings: float | None
    system_cost: float | None
    payback_years: float | None

    recommendations: list[Recommendation]
    created_at: datetime

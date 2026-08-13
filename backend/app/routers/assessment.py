from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.clients.nasa_power import NasaPowerError, fetch_climatology
from app.db import get_db
from app.domain.adaptation import rank_recommendations
from app.domain.climate_risk import climate_risk_profile
from app.domain.economics import estimate_savings, simple_payback_years
from app.domain.solar import solar_potential
from app.domain.wind import wind_potential

router = APIRouter()


@router.post("/assess", response_model=schemas.AssessmentReport, status_code=201)
def create_assessment(payload: schemas.AssessmentRequest, db: Session = Depends(get_db)):
    try:
        climatology = fetch_climatology(payload.lat, payload.lon)
    except NasaPowerError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    solar = solar_potential(payload.panel_area_m2, climatology.avg_irradiance_kwh_m2_day)
    wind = wind_potential(
        payload.turbine_rotor_area_m2,
        climatology.avg_wind_speed_10m_ms,
        payload.turbine_hub_height_m,
    )
    risk = climate_risk_profile(
        climatology.monthly_max_temps_c,
        climatology.monthly_mean_temps_c,
        climatology.monthly_precip_mm_day,
    )
    recommendations = rank_recommendations(solar, wind, risk)

    estimated_annual_savings = None
    estimated_monthly_savings = None
    payback_years = None
    if payload.electricity_price_per_kwh is not None:
        savings = estimate_savings(
            solar["annual_kwh"], wind["annual_kwh"], payload.electricity_price_per_kwh
        )
        estimated_annual_savings = savings["annual_savings"]
        estimated_monthly_savings = savings["monthly_savings"]
        payback_years = simple_payback_years(payload.system_cost, estimated_annual_savings)

    site = (
        db.query(models.Site)
        .filter(models.Site.lat == payload.lat, models.Site.lon == payload.lon)
        .first()
    )
    if site is None:
        site = models.Site(
            name=payload.site_name or f"Site ({payload.lat:.3f}, {payload.lon:.3f})",
            lat=payload.lat,
            lon=payload.lon,
        )
        db.add(site)
        db.flush()

    assessment = models.Assessment(
        site_id=site.id,
        panel_area_m2=payload.panel_area_m2,
        turbine_rotor_area_m2=payload.turbine_rotor_area_m2,
        turbine_hub_height_m=payload.turbine_hub_height_m,
        solar_daily_kwh=solar["daily_kwh"],
        solar_annual_kwh=solar["annual_kwh"],
        wind_daily_kwh=wind["daily_kwh"],
        wind_annual_kwh=wind["annual_kwh"],
        wind_class=wind["wind_class"],
        hub_height_wind_speed_ms=wind["hub_height_wind_speed_ms"],
        heat_stress_days_per_year=risk["heat_stress_days_per_year"],
        cooling_degree_days=risk["cooling_degree_days"],
        heating_degree_days=risk["heating_degree_days"],
        precipitation_variability_index=risk["precipitation_variability_index"],
        monthly_mean_temps_c=climatology.monthly_mean_temps_c,
        monthly_max_temps_c=climatology.monthly_max_temps_c,
        monthly_precip_mm_day=climatology.monthly_precip_mm_day,
        currency_symbol=payload.currency_symbol,
        electricity_price_per_kwh=payload.electricity_price_per_kwh,
        estimated_annual_savings=estimated_annual_savings,
        estimated_monthly_savings=estimated_monthly_savings,
        system_cost=payload.system_cost,
        payback_years=payback_years,
        recommendations=recommendations,
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    return assessment

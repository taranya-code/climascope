from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Site(Base):
    __tablename__ = "sites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lon: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    assessments: Mapped[list["Assessment"]] = relationship(
        back_populates="site", cascade="all, delete-orphan"
    )


class Assessment(Base):
    __tablename__ = "assessments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    site_id: Mapped[int] = mapped_column(ForeignKey("sites.id"), nullable=False)

    panel_area_m2: Mapped[float] = mapped_column(Float)
    turbine_rotor_area_m2: Mapped[float] = mapped_column(Float)
    turbine_hub_height_m: Mapped[float] = mapped_column(Float)

    solar_daily_kwh: Mapped[float] = mapped_column(Float)
    solar_annual_kwh: Mapped[float] = mapped_column(Float)

    wind_daily_kwh: Mapped[float] = mapped_column(Float)
    wind_annual_kwh: Mapped[float] = mapped_column(Float)
    wind_class: Mapped[str] = mapped_column(String)
    hub_height_wind_speed_ms: Mapped[float] = mapped_column(Float)

    heat_stress_days_per_year: Mapped[float] = mapped_column(Float)
    cooling_degree_days: Mapped[float] = mapped_column(Float)
    heating_degree_days: Mapped[float] = mapped_column(Float)
    precipitation_variability_index: Mapped[float] = mapped_column(Float)

    monthly_mean_temps_c: Mapped[list[float]] = mapped_column(JSON)
    monthly_max_temps_c: Mapped[list[float]] = mapped_column(JSON)
    monthly_precip_mm_day: Mapped[list[float]] = mapped_column(JSON)

    currency_symbol: Mapped[str] = mapped_column(String, default="$")
    electricity_price_per_kwh: Mapped[float | None] = mapped_column(Float, nullable=True)
    estimated_annual_savings: Mapped[float | None] = mapped_column(Float, nullable=True)
    estimated_monthly_savings: Mapped[float | None] = mapped_column(Float, nullable=True)
    system_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    payback_years: Mapped[float | None] = mapped_column(Float, nullable=True)

    recommendations: Mapped[list[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    site: Mapped["Site"] = relationship(back_populates="assessments")

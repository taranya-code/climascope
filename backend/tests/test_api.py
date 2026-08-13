import pytest

from app.clients.nasa_power import ClimatologyData, NasaPowerError
from app.routers import assessment as assessment_module

PHOENIX_LIKE_CLIMATOLOGY = ClimatologyData(
    avg_irradiance_kwh_m2_day=6.5,
    avg_wind_speed_10m_ms=3.5,
    monthly_max_temps_c=[20, 22, 26, 31, 36, 41, 42, 41, 38, 32, 25, 20],
    monthly_mean_temps_c=[13, 15, 19, 23, 28, 33, 35, 34, 31, 24, 17, 12],
    monthly_precip_mm_day=[0.6, 0.7, 0.5, 0.2, 0.1, 0.0, 0.3, 0.5, 0.3, 0.3, 0.4, 0.6],
)


@pytest.fixture()
def mock_climatology(monkeypatch):
    monkeypatch.setattr(assessment_module, "fetch_climatology", lambda lat, lon: PHOENIX_LIKE_CLIMATOLOGY)


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_assess_creates_site_and_returns_full_report(client, mock_climatology):
    response = client.post(
        "/assess",
        json={"lat": 33.45, "lon": -112.07, "site_name": "Phoenix Warehouse Roof", "panel_area_m2": 40},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["solar_annual_kwh"] > 0
    assert body["wind_class"] in {"poor", "marginal", "good", "excellent", "outstanding"}
    assert body["heat_stress_days_per_year"] > 0
    assert isinstance(body["recommendations"], list)
    assert len(body["recommendations"]) >= 1

    sites = client.get("/sites").json()
    assert len(sites) == 1
    assert sites[0]["name"] == "Phoenix Warehouse Roof"


def test_assess_reuses_existing_site_for_same_coordinates(client, mock_climatology):
    client.post("/assess", json={"lat": 10.0, "lon": 20.0})
    client.post("/assess", json={"lat": 10.0, "lon": 20.0})

    sites = client.get("/sites").json()
    assert len(sites) == 1

    history = client.get(f"/sites/{sites[0]['id']}/assessments").json()
    assert len(history) == 2


def test_assess_returns_502_when_nasa_power_unreachable(client, monkeypatch):
    def raise_error(lat, lon):
        raise NasaPowerError("simulated outage")

    monkeypatch.setattr(assessment_module, "fetch_climatology", raise_error)

    response = client.post("/assess", json={"lat": 0, "lon": 0})
    assert response.status_code == 502


def test_assess_rejects_invalid_coordinates(client):
    response = client.post("/assess", json={"lat": 999, "lon": 0})
    assert response.status_code == 422


def test_delete_site_removes_it(client, mock_climatology):
    client.post("/assess", json={"lat": 1.0, "lon": 2.0})
    site_id = client.get("/sites").json()[0]["id"]

    delete_response = client.delete(f"/sites/{site_id}")
    assert delete_response.status_code == 204
    assert client.get("/sites").json() == []


def test_get_assessments_for_unknown_site_returns_404(client):
    response = client.get("/sites/999/assessments")
    assert response.status_code == 404

# ClimaScope backend

FastAPI service with the domain logic, NASA POWER integration, and persistence.

## Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload
```

The API is served at `http://127.0.0.1:8000`; interactive docs at `http://127.0.0.1:8000/docs`.

## Test

```bash
pytest
```

76 tests: pure-function unit tests for each domain module (`tests/test_solar.py`,
`test_wind.py`, `test_climate_risk.py`, `test_adaptation.py`, `test_economics.py`)
against hand-computed expected values, mocked-HTTP tests for the NASA POWER and
geocoding clients (`test_nasa_power_client.py`, `test_geocoding_client.py`), and
API integration tests against an in-memory SQLite database (`test_api.py`). No
test hits the network.

## Layout

- `app/domain/` — pure calculation functions (solar, wind, climate risk, adaptation
  recommendations, currency-agnostic savings/payback). No I/O; this is where the
  interesting logic lives.
- `app/clients/nasa_power.py` — client for NASA's free POWER climatology API.
- `app/clients/geocoding.py` — client for Open-Meteo's free, global place-search API.
- `app/models.py`, `app/schemas.py`, `app/db.py` — SQLAlchemy models, Pydantic
  schemas, SQLite session management.
- `app/routers/` — `POST /assess`, the `/sites` CRUD endpoints, and `GET /geocode`.

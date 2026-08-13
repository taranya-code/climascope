# ClimaScope

A full-stack tool that assesses a site's renewable energy potential and climate
risk from just a latitude/longitude, using real climatology data from NASA's
free [POWER API](https://power.larc.nasa.gov/docs/services/api/temporal/climatology/).

**The problem**: deciding whether a site is worth investing in for solar/wind,
and understanding how exposed it is to heat stress, drought, or erratic
rainfall, usually means pulling data from several different sources by hand.
ClimaScope does it in one request: give it coordinates and a panel/turbine
spec, and it returns

- solar energy potential (kWh/day, kWh/year),
- wind energy potential (kWh/day, kWh/year, wind class),
- a climate risk profile (heat-stress days, cooling/heating degree days,
  precipitation variability), and
- ranked adaptation recommendations synthesized from all of the above.

Every input can be a real place — try Phoenix, AZ vs. Seattle, WA from the
built-in presets and the numbers move in opposite, physically sensible
directions (solar/heat vs. rain/mild-heat).

## Architecture

```
┌─────────────────────┐        ┌──────────────────────────────┐        ┌────────────────────┐
│  React + TS frontend │──────▶│  FastAPI backend               │──────▶│  NASA POWER API      │
│  (Vite, recharts)    │  REST │  app/routers/  →  app/domain/  │ HTTPS │  (climatology, free,  │
│  localhost:5173      │◀──────│  →  SQLite (SQLAlchemy)        │◀──────│   no API key)         │
└─────────────────────┘        └──────────────────────────────┘        └────────────────────┘
```

`app/domain/` holds pure, dependency-free functions (solar/wind physics,
degree-day math, the recommendation ranking) — that's the part with real
substance, and it's unit tested against hand-computed values independent of
the implementation. `app/clients/nasa_power.py` is the only network-facing
piece and is tested with a mocked HTTP client, so the full test suite runs
offline.

## Setup

Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # .venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend (separate terminal):

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The dev server proxies `/api/*` to the backend
on port 8000.

## Testing

```bash
cd backend && pytest        # 54 tests, domain logic + mocked API client + integration
cd frontend && npm run build # typechecks and builds the production bundle
```

## Known simplifications

Documented in code rather than hidden, since they're the natural follow-up
questions:

- **Wind energy** uses the *average* wind speed cubed, which underestimates
  true yield (`E[v³] > E[v]³` for a right-skewed wind speed distribution). A
  production model would integrate over a Weibull distribution instead.
- **Heat-stress days** are estimated per-month (a month counts as fully
  "in stress" once its mean daily max crosses the threshold) since only
  monthly climate normals are available here, not daily records.
- **Recommendation thresholds** (kWh/year cutoffs, degree-day bands) are
  reasonable defaults, not calibrated against real adoption data.

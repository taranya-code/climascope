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
  precipitation variability),
- ranked adaptation recommendations synthesized from all of the above, and
- an optional cost-savings and payback estimate, in whatever local currency
  and electricity price you give it.

**Built for anywhere, not just one country**: instead of requiring a
latitude/longitude, you can search for a place by name — "Nairobi", "São
Paulo", "Chiang Mai" — using a free global geocoding API. The savings estimate
is currency-agnostic: it takes a raw price-per-kWh and a currency symbol you
type in, rather than assuming USD. Try Phoenix, AZ vs. Seattle, WA vs. Mumbai,
India and the climate numbers move in physically sensible, very different
directions (Mumbai in particular has a precipitation variability index over
2x Phoenix's or Seattle's, correctly reflecting its monsoon season).

## Architecture

```
┌─────────────────────┐        ┌──────────────────────────────┐        ┌────────────────────────┐
│  React + TS frontend │──────▶│  FastAPI backend               │──────▶│  NASA POWER API          │
│  (Vite, recharts)    │  REST │  app/routers/  →  app/domain/  │ HTTPS │  (climatology, free, no  │
│  localhost:5173      │◀──────│  →  SQLite (SQLAlchemy)        │◀──────│   API key)               │
└─────────────────────┘        └──────────────────────────────┘        └────────────────────────┘
                                            │                    HTTPS  ┌────────────────────────┐
                                            └───────────────────────▶  │  Open-Meteo Geocoding    │
                                                                   ◀───│  (place search, global,  │
                                                                        │   free, no API key)     │
                                                                        └────────────────────────┘
```

`app/domain/` holds pure, dependency-free functions (solar/wind physics,
degree-day math, the recommendation ranking, currency-agnostic savings/payback
math) — that's the part with real substance, and it's unit tested against
hand-computed values independent of the implementation. `app/clients/` holds
the two network-facing pieces (NASA POWER, Open-Meteo geocoding), each tested
with a mocked HTTP client, so the full test suite runs offline.

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
cd backend && pytest        # 76 tests, domain logic + mocked API clients + integration
cd frontend && npm run build # typechecks and builds the production bundle
```

## Deploying

Backend on [Render](https://render.com): New → Blueprint → connect this repo
(picks up `render.yaml` automatically), or manually create a Web Service with
root directory `backend`, build command `pip install -r requirements.txt`,
start command `uvicorn app.main:app --host 0.0.0.0 --port $PORT`. Note the
free tier's disk is ephemeral, so saved sites reset on redeploy/restart --
fine for a demo, swap to Postgres or a persistent disk for anything long-lived.

Frontend on [Vercel](https://vercel.com): New Project → import this repo →
root directory `frontend` (Vite is auto-detected) → add an environment
variable `VITE_API_BASE_URL` set to the Render backend's URL (e.g.
`https://climascope-api.onrender.com`, no trailing slash) → Deploy.

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

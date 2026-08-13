import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db import init_db
from app.routers import assessment, sites

# No auth, no cookies, no user data beyond what's typed into the form -- so a
# wildcard is a safe default for this public demo API. Override with a
# comma-separated ALLOWED_ORIGINS env var to lock it down to a specific
# frontend origin instead.
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "*").split(",")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="ClimaScope API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(assessment.router, tags=["assessment"])
app.include_router(sites.router, tags=["sites"])


@app.get("/health")
def health():
    return {"status": "ok"}

from fastapi import APIRouter, HTTPException, Query

from app import schemas
from app.clients.geocoding import GeocodingError, search_places

router = APIRouter()


@router.get("/geocode", response_model=list[schemas.PlaceSuggestion])
def geocode(q: str = Query(min_length=1)):
    try:
        results = search_places(q)
    except GeocodingError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return [schemas.PlaceSuggestion(**vars(r)) for r in results]

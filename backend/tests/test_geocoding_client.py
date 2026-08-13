import httpx
import pytest

from app.clients.geocoding import GeocodingError, PlaceResult, search_places


def _fake_response(body: dict) -> httpx.Response:
    return httpx.Response(200, json=body, request=httpx.Request("GET", "https://example.test"))


class _StubClient:
    def __init__(self, response: httpx.Response | None = None, error: Exception | None = None):
        self._response = response
        self._error = error
        self.calls = []

    def get(self, url, params=None):
        self.calls.append((url, params))
        if self._error is not None:
            raise self._error
        return self._response


SAMPLE_BODY = {
    "results": [
        {
            "name": "Nairobi",
            "country": "Kenya",
            "admin1": "Nairobi County",
            "latitude": -1.28333,
            "longitude": 36.81667,
        },
        {
            "name": "Nairobi",
            "country": "United States",
            "admin1": "Florida",
            "latitude": 28.5,
            "longitude": -81.0,
        },
    ]
}


def test_search_places_parses_results():
    stub = _StubClient(response=_fake_response(SAMPLE_BODY))

    results = search_places("Nairobi", http_client=stub)

    assert results == [
        PlaceResult(name="Nairobi", country="Kenya", admin1="Nairobi County", lat=-1.28333, lon=36.81667),
        PlaceResult(name="Nairobi", country="United States", admin1="Florida", lat=28.5, lon=-81.0),
    ]
    assert stub.calls[0][1]["name"] == "Nairobi"


def test_search_places_returns_empty_list_for_no_matches():
    stub = _StubClient(response=_fake_response({}))

    assert search_places("asdkjhaskjdh", http_client=stub) == []


def test_search_places_respects_limit_param():
    stub = _StubClient(response=_fake_response(SAMPLE_BODY))

    search_places("Nairobi", limit=3, http_client=stub)

    assert stub.calls[0][1]["count"] == 3


def test_search_places_rejects_empty_query():
    with pytest.raises(ValueError):
        search_places("   ", http_client=_StubClient())


def test_search_places_rejects_non_positive_limit():
    with pytest.raises(ValueError):
        search_places("Paris", limit=0, http_client=_StubClient())


def test_search_places_wraps_network_errors():
    stub = _StubClient(error=httpx.ConnectError("boom"))

    with pytest.raises(GeocodingError):
        search_places("Paris", http_client=stub)


def test_search_places_raises_on_malformed_result():
    bad_body = {"results": [{"name": "Nowhere"}]}  # missing lat/lon
    stub = _StubClient(response=_fake_response(bad_body))

    with pytest.raises(GeocodingError):
        search_places("Nowhere", http_client=stub)

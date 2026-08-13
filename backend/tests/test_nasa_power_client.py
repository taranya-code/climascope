import httpx
import pytest

from app.clients.nasa_power import MONTH_KEYS, NasaPowerError, fetch_climatology


def _fake_response(parameter_block: dict) -> httpx.Response:
    payload = {"properties": {"parameter": parameter_block}}
    return httpx.Response(200, json=payload, request=httpx.Request("GET", "https://example.test"))


class _StubClient:
    """Duck-types the subset of httpx.Client this module calls, with no network access."""

    def __init__(self, response: httpx.Response | None = None, error: Exception | None = None):
        self._response = response
        self._error = error
        self.calls = []

    def get(self, url, params=None):
        self.calls.append((url, params))
        if self._error is not None:
            raise self._error
        return self._response


def _full_parameter_block(irradiance=5.0, wind=4.0, max_t=30.0, mean_t=20.0, precip=3.0):
    return {
        "ALLSKY_SFC_SW_DWN": {m: irradiance for m in MONTH_KEYS},
        "WS10M": {m: wind for m in MONTH_KEYS},
        "T2M_MAX": {m: max_t for m in MONTH_KEYS},
        "T2M": {m: mean_t for m in MONTH_KEYS},
        "PRECTOTCORR": {m: precip for m in MONTH_KEYS},
    }


def test_fetch_climatology_parses_and_averages_response():
    stub = _StubClient(response=_fake_response(_full_parameter_block(irradiance=5.5, wind=6.0)))

    result = fetch_climatology(lat=33.45, lon=-112.07, http_client=stub)

    assert result.avg_irradiance_kwh_m2_day == pytest.approx(5.5)
    assert result.avg_wind_speed_10m_ms == pytest.approx(6.0)
    assert len(result.monthly_max_temps_c) == 12
    assert len(result.monthly_mean_temps_c) == 12
    assert len(result.monthly_precip_mm_day) == 12
    assert stub.calls[0][1]["latitude"] == 33.45
    assert stub.calls[0][1]["longitude"] == -112.07


def test_fetch_climatology_averages_varying_monthly_values():
    block = _full_parameter_block()
    block["ALLSKY_SFC_SW_DWN"] = {m: i for i, m in enumerate(MONTH_KEYS, start=1)}  # 1..12
    stub = _StubClient(response=_fake_response(block))

    result = fetch_climatology(lat=0, lon=0, http_client=stub)

    assert result.avg_irradiance_kwh_m2_day == pytest.approx(6.5)  # mean of 1..12


@pytest.mark.parametrize("lat,lon", [(91, 0), (-91, 0), (0, 181), (0, -181)])
def test_fetch_climatology_rejects_out_of_range_coordinates(lat, lon):
    with pytest.raises(ValueError):
        fetch_climatology(lat=lat, lon=lon, http_client=_StubClient())


def test_fetch_climatology_wraps_network_errors():
    stub = _StubClient(error=httpx.ConnectError("boom"))

    with pytest.raises(NasaPowerError):
        fetch_climatology(lat=0, lon=0, http_client=stub)


def test_fetch_climatology_raises_on_missing_parameter():
    block = _full_parameter_block()
    del block["WS10M"]
    stub = _StubClient(response=_fake_response(block))

    with pytest.raises(NasaPowerError):
        fetch_climatology(lat=0, lon=0, http_client=stub)


def test_fetch_climatology_raises_on_malformed_response_shape():
    bad_response = httpx.Response(
        200, json={"unexpected": "shape"}, request=httpx.Request("GET", "https://example.test")
    )
    stub = _StubClient(response=bad_response)

    with pytest.raises(NasaPowerError):
        fetch_climatology(lat=0, lon=0, http_client=stub)

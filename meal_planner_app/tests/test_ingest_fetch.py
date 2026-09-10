"""URL fetch for recipe ingest: allow http(s) public hosts only (no live net)."""

import io
import urllib.error
from email.message import EmailMessage

import pytest

from meal_planner_app.ingest.fetch import (
    FetchDeniedError,
    FetchTimeoutError,
    FetchUpstreamError,
    FetchValidationError,
    fetch_url,
)


class _FakeResponse:
    def __init__(self, body, headers, url):
        self._body = body if isinstance(body, bytes) else body.encode("utf-8")
        self.headers = headers
        self.url = url

    def read(self, size=-1):
        if size is None or size < 0:
            data = self._body
            self._body = b""
            return data
        data = self._body[:size]
        self._body = self._body[size:]
        return data

    def geturl(self):
        return self.url

    def info(self):
        return self.headers

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def _headers(content_type="text/html; charset=utf-8"):
    msg = EmailMessage()
    msg["Content-Type"] = content_type
    return msg


def test_rejects_non_http_schemes():
    with pytest.raises(FetchValidationError):
        fetch_url("file:///etc/passwd")
    with pytest.raises(FetchValidationError):
        fetch_url("javascript:alert(1)")
    with pytest.raises(FetchValidationError):
        fetch_url("ftp://example.com/recipe")
    with pytest.raises(FetchValidationError):
        fetch_url("not-a-url")


def test_blocks_loopback_and_localhost():
    with pytest.raises(FetchDeniedError):
        fetch_url("http://127.0.0.1/secret")
    with pytest.raises(FetchDeniedError):
        fetch_url("http://localhost/recipe")
    with pytest.raises(FetchDeniedError):
        fetch_url("http://[::1]/recipe")


def test_blocks_private_and_link_local_literals():
    with pytest.raises(FetchDeniedError):
        fetch_url("http://10.0.0.5/recipe")
    with pytest.raises(FetchDeniedError):
        fetch_url("http://192.168.1.1/recipe")
    with pytest.raises(FetchDeniedError):
        fetch_url("http://169.254.169.254/latest/meta-data")


def test_blocks_hostname_that_resolves_private():
    with pytest.raises(FetchDeniedError):
        fetch_url(
            "http://evil.example/przepis",
            resolver=lambda _host: ["10.1.2.3"],
        )


def test_fetch_returns_html_text(monkeypatch):
    html = "<html><body><h1>Zupa</h1></body></html>"

    def fake_urlopen(request, timeout=None):
        assert request.get_full_url() == "https://aniagotuje.pl/przepis/zupa"
        assert timeout == 15
        return _FakeResponse(html, _headers(), request.get_full_url())

    monkeypatch.setattr(
        "meal_planner_app.ingest.fetch.urllib.request.urlopen", fake_urlopen
    )
    result = fetch_url(
        "https://aniagotuje.pl/przepis/zupa",
        resolver=lambda _host: ["93.184.216.34"],
    )
    assert result.text == html
    assert result.source_url == "https://aniagotuje.pl/przepis/zupa"
    assert "text/html" in result.content_type


def test_rejects_non_text_content_type(monkeypatch):
    def fake_urlopen(request, timeout=None):  # pylint: disable=unused-argument
        return _FakeResponse(b"\x89PNG", _headers("image/png"), request.get_full_url())

    monkeypatch.setattr(
        "meal_planner_app.ingest.fetch.urllib.request.urlopen", fake_urlopen
    )
    with pytest.raises(FetchValidationError):
        fetch_url(
            "https://example.com/pic.png",
            resolver=lambda _host: ["93.184.216.34"],
        )


def test_oversize_body_is_validation_error(monkeypatch):
    def fake_urlopen(request, timeout=None):  # pylint: disable=unused-argument
        return _FakeResponse(
            b"x" * (200 * 1024 + 8),
            _headers("text/html"),
            request.get_full_url(),
        )

    monkeypatch.setattr(
        "meal_planner_app.ingest.fetch.urllib.request.urlopen", fake_urlopen
    )
    with pytest.raises(FetchValidationError):
        fetch_url(
            "https://example.com/huge",
            resolver=lambda _host: ["93.184.216.34"],
        )


def test_timeout_maps_to_fetch_timeout(monkeypatch):
    def fake_urlopen(request, timeout=None):  # pylint: disable=unused-argument
        raise TimeoutError("timed out")

    monkeypatch.setattr(
        "meal_planner_app.ingest.fetch.urllib.request.urlopen", fake_urlopen
    )
    with pytest.raises(FetchTimeoutError):
        fetch_url(
            "https://example.com/slow",
            resolver=lambda _host: ["93.184.216.34"],
        )


def test_blocks_redirect_target_that_is_private(monkeypatch):
    def fake_urlopen(request, timeout=None):  # pylint: disable=unused-argument
        return _FakeResponse(
            "<html>stolen</html>",
            _headers(),
            "http://127.0.0.1/stolen",
        )

    monkeypatch.setattr(
        "meal_planner_app.ingest.fetch.urllib.request.urlopen", fake_urlopen
    )
    with pytest.raises(FetchDeniedError):
        fetch_url(
            "https://example.com/przepis",
            resolver=lambda _host: ["93.184.216.34"],
        )


def test_http_error_maps_to_upstream(monkeypatch):
    def fake_urlopen(request, timeout=None):
        raise urllib_error_404()

    monkeypatch.setattr(
        "meal_planner_app.ingest.fetch.urllib.request.urlopen", fake_urlopen
    )
    with pytest.raises(FetchUpstreamError):
        fetch_url(
            "https://example.com/missing",
            resolver=lambda _host: ["93.184.216.34"],
        )


def urllib_error_404():
    return urllib.error.HTTPError(
        "https://example.com/missing",
        404,
        "not found",
        hdrs=None,
        fp=io.BytesIO(b""),
    )

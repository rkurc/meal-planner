"""Fetch recipe page text from a user URL. Blocks private hosts (SSRF)."""

import ipaddress
import socket
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Callable, List, Optional
from urllib.parse import urlparse

MAX_FETCH_BYTES = 200 * 1024
FETCH_TIMEOUT = 15
USER_AGENT = "MealPlanner/0.1 (+recipe-import)"
ALLOWED_SCHEMES = ("http", "https")
ALLOWED_CONTENT_TYPES = frozenset(
    {
        "text/html",
        "text/plain",
        "text/xml",
        "application/xml",
        "application/xhtml+xml",
        "application/ld+json",
    }
)

Resolver = Callable[[str], List[str]]


@dataclass
class FetchResult:
    """Scraped page body. source_url is the final URL after redirects."""

    text: str
    source_url: str
    content_type: str


class FetchError(Exception):
    """Base fetch failure with an HTTP status for the API layer."""

    status_code = 400


class FetchValidationError(FetchError):
    """Bad URL, oversize body, or disallowed content type."""

    status_code = 400


class FetchDeniedError(FetchError):
    """Private / loopback / link-local / metadata host (SSRF)."""

    status_code = 400


class FetchTimeoutError(FetchError):
    """Upstream timed out."""

    status_code = 504


class FetchUpstreamError(FetchError):
    """DNS or HTTP failure talking to the page."""

    status_code = 502


_FETCH_OVERRIDE = None


def set_fetch_impl(func: Optional[Callable]) -> None:
    """Install (or clear) a process-wide fetch function. Tests pass a fake."""
    # pylint: disable=global-statement
    global _FETCH_OVERRIDE
    _FETCH_OVERRIDE = func


def fetch_page(url: str) -> FetchResult:
    """Entry point used by parse/API. Tests replace this via set_fetch_impl."""
    if _FETCH_OVERRIDE is not None:
        return _FETCH_OVERRIDE(url)
    return fetch_url(url)


def _ip_blocked(ip: str) -> bool:
    addr = ipaddress.ip_address(ip)
    return bool(
        addr.is_private
        or addr.is_loopback
        or addr.is_link_local
        or addr.is_reserved
        or addr.is_multicast
        or addr.is_unspecified
    )


def default_resolver(host: str) -> List[str]:
    infos = socket.getaddrinfo(host, None)
    return list({info[4][0] for info in infos})


def assert_host_allowed(host: str, resolver: Resolver) -> None:
    """Raise if host is localhost, a blocked IP, or resolves only/also private."""
    cleaned = (host or "").strip().lower().rstrip(".")
    if not cleaned:
        raise FetchValidationError("url must be an http(s) URL")
    if cleaned == "localhost" or cleaned.endswith(".localhost"):
        raise FetchDeniedError("URL host is not allowed")
    try:
        if _ip_blocked(cleaned):
            raise FetchDeniedError("URL host is not allowed")
        ipaddress.ip_address(cleaned)
        return
    except ValueError:
        pass
    try:
        ips = resolver(cleaned)
    except OSError as exc:
        raise FetchUpstreamError(f"could not resolve host: {exc}") from exc
    if not ips:
        raise FetchDeniedError("URL host is not allowed")
    for ip in ips:
        if _ip_blocked(ip):
            raise FetchDeniedError("URL host is not allowed")


def assert_url_allowed(url: str, resolver: Resolver) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in ALLOWED_SCHEMES or not parsed.netloc:
        raise FetchValidationError("url must be an http(s) URL")
    if parsed.username or parsed.password:
        raise FetchDeniedError("URL host is not allowed")
    host = parsed.hostname
    if host is None:
        raise FetchValidationError("url must be an http(s) URL")
    assert_host_allowed(host, resolver)


def _content_type_allowed(content_type: str) -> bool:
    if not content_type:
        return True
    main = content_type.split(";", 1)[0].strip().lower()
    return main in ALLOWED_CONTENT_TYPES


def _decode_body(raw: bytes, headers) -> str:
    charset = "utf-8"
    if headers is not None and hasattr(headers, "get_content_charset"):
        charset = headers.get_content_charset() or "utf-8"
    try:
        return raw.decode(charset)
    except (LookupError, UnicodeDecodeError):
        return raw.decode("utf-8", errors="replace")


def _read_capped(response) -> bytes:
    chunks = []
    total = 0
    while True:
        chunk = response.read(8192)
        if not chunk:
            break
        total += len(chunk)
        if total > MAX_FETCH_BYTES:
            raise FetchValidationError("page is too large")
        chunks.append(chunk)
    return b"".join(chunks)


def fetch_url(  # pylint: disable=too-many-arguments
    url: Optional[str],
    *,
    resolver: Optional[Resolver] = None,
) -> FetchResult:
    """GET a public http(s) URL and return the body as text."""
    if url is None or not str(url).strip():
        raise FetchValidationError("url is required")
    target = str(url).strip()
    resolve = resolver or default_resolver
    assert_url_allowed(target, resolve)

    request = urllib.request.Request(
        target,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": (
                "text/html,application/xhtml+xml,text/plain,"
                "application/xml;q=0.9,*/*;q=0.1"
            ),
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=FETCH_TIMEOUT) as response:
            final_url = response.geturl() or target
            if final_url != target:
                assert_url_allowed(final_url, resolve)
            headers = response.info()
            content_type = ""
            if headers is not None:
                if hasattr(headers, "get_content_type"):
                    content_type = headers.get_content_type() or ""
                if not content_type:
                    content_type = str(headers.get("Content-Type") or "")
            if not _content_type_allowed(content_type):
                raise FetchValidationError("URL did not return a text page")
            raw = _read_capped(response)
    except (TimeoutError, socket.timeout) as exc:
        raise FetchTimeoutError("timed out fetching URL") from exc
    except urllib.error.HTTPError as exc:
        raise FetchUpstreamError(f"HTTP {exc.code}") from exc
    except urllib.error.URLError as exc:
        reason = exc.reason
        if isinstance(reason, (TimeoutError, socket.timeout)):
            raise FetchTimeoutError("timed out fetching URL") from exc
        if "timed out" in str(exc).lower():
            raise FetchTimeoutError("timed out fetching URL") from exc
        raise FetchUpstreamError(f"could not fetch URL: {exc}") from exc

    return FetchResult(
        text=_decode_body(raw, headers),
        source_url=final_url,
        content_type=content_type,
    )

"""HMAC-SHA256 request signer for GMO Coin private API."""

from __future__ import annotations

import hashlib
import hmac
import time


def build_timestamp() -> str:
    """Return current Unix time in milliseconds as a string."""
    return str(int(time.time() * 1000))


def build_signature(
    api_secret: str,
    timestamp: str,
    method: str,
    path: str,
    body: str = "",
) -> str:
    """Compute HMAC-SHA256 signature for a GMO Coin API request.

    Signature = HMAC-SHA256(secret, timestamp + METHOD + path + body)

    Args:
        api_secret: GMO Coin API secret key.
        timestamp: Unix millisecond timestamp string (from ``build_timestamp``).
        method: HTTP method in uppercase (e.g. "GET", "POST").
        path: Request path including query string (e.g. "/private/v1/order").
        body: Raw request body string; empty string for GET requests.

    Returns:
        Hex-encoded HMAC-SHA256 signature string.
    """
    message = timestamp + method.upper() + path + body
    signature = hmac.new(
        api_secret.encode(),
        msg=message.encode(),
        digestmod=hashlib.sha256,
    ).hexdigest()
    return signature


def build_auth_headers(
    api_key: str,
    api_secret: str,
    method: str,
    path: str,
    body: str = "",
) -> dict[str, str]:
    """Build authentication headers required by GMO Coin private endpoints.

    Args:
        api_key: GMO Coin API key.
        api_secret: GMO Coin API secret.
        method: HTTP method in uppercase.
        path: Request path (and query string) without the base URL.
        body: Raw JSON body string for POST requests; empty for GET.

    Returns:
        Dict containing ``API-KEY``, ``API-TIMESTAMP``, and ``API-SIGN`` headers.
    """
    timestamp = build_timestamp()
    signature = build_signature(api_secret, timestamp, method, path, body)
    return {
        "API-KEY": api_key,
        "API-TIMESTAMP": timestamp,
        "API-SIGN": signature,
    }

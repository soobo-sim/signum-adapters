"""Unit tests for signum_adapters.gmo_coin.signer."""

from __future__ import annotations

import hashlib
import hmac
import time
from unittest.mock import patch

from signum_adapters.gmo_coin.signer import (
    build_auth_headers,
    build_signature,
    build_timestamp,
)


class TestBuildTimestamp:
    def test_returns_string(self):
        ts = build_timestamp()
        assert isinstance(ts, str)

    def test_is_numeric(self):
        ts = build_timestamp()
        assert ts.isdigit()

    def test_is_milliseconds(self):
        before = int(time.time() * 1000)
        ts = int(build_timestamp())
        after = int(time.time() * 1000)
        assert before <= ts <= after

    def test_length_is_13_digits(self):
        # Unix ms timestamps are 13 decimal digits until year 2286
        ts = build_timestamp()
        assert len(ts) == 13


class TestBuildSignature:
    _SECRET = "test-secret-key"
    _TS = "1234567890000"

    def _expected(self, method: str, path: str, body: str = "") -> str:
        message = self._TS + method + path + body
        return hmac.new(
            self._SECRET.encode(),
            msg=message.encode(),
            digestmod=hashlib.sha256,
        ).hexdigest()

    def test_get_no_body(self):
        sig = build_signature(self._SECRET, self._TS, "GET", "/public/v1/ticker")
        assert sig == self._expected("GET", "/public/v1/ticker")

    def test_post_with_body(self):
        body = '{"symbol":"BTC_JPY","side":"BUY"}'
        sig = build_signature(self._SECRET, self._TS, "POST", "/private/v1/order", body)
        assert sig == self._expected("POST", "/private/v1/order", body)

    def test_method_normalised_to_uppercase(self):
        sig_lower = build_signature(self._SECRET, self._TS, "get", "/public/v1/ticker")
        sig_upper = build_signature(self._SECRET, self._TS, "GET", "/public/v1/ticker")
        assert sig_lower == sig_upper

    def test_different_timestamps_produce_different_signatures(self):
        sig1 = build_signature(self._SECRET, "1000000000000", "GET", "/public/v1/ticker")
        sig2 = build_signature(self._SECRET, "1000000000001", "GET", "/public/v1/ticker")
        assert sig1 != sig2

    def test_different_bodies_produce_different_signatures(self):
        sig1 = build_signature(self._SECRET, self._TS, "POST", "/private/v1/order", '{"size":"0.1"}')
        sig2 = build_signature(self._SECRET, self._TS, "POST", "/private/v1/order", '{"size":"0.2"}')
        assert sig1 != sig2

    def test_returns_hex_string(self):
        sig = build_signature(self._SECRET, self._TS, "GET", "/public/v1/ticker")
        # SHA-256 produces 32 bytes → 64 hex chars
        assert len(sig) == 64
        int(sig, 16)  # must be valid hex


class TestBuildAuthHeaders:
    def test_required_header_keys_present(self):
        headers = build_auth_headers(
            api_key="my-key",
            api_secret="my-secret",
            method="GET",
            path="/private/v1/account/assets",
        )
        assert "API-KEY" in headers
        assert "API-TIMESTAMP" in headers
        assert "API-SIGN" in headers

    def test_api_key_value(self):
        headers = build_auth_headers("my-key", "my-secret", "GET", "/private/v1/account/assets")
        assert headers["API-KEY"] == "my-key"

    def test_signature_matches_manual_computation(self):
        fixed_ts = "9999999999999"
        with patch("signum_adapters.gmo_coin.signer.build_timestamp", return_value=fixed_ts):
            headers = build_auth_headers(
                api_key="k",
                api_secret="s",
                method="POST",
                path="/private/v1/order",
                body='{"symbol":"BTC_JPY"}',
            )
        expected_sig = build_signature("s", fixed_ts, "POST", "/private/v1/order", '{"symbol":"BTC_JPY"}')
        assert headers["API-SIGN"] == expected_sig
        assert headers["API-TIMESTAMP"] == fixed_ts

    def test_no_secrets_in_sign_field(self):
        headers = build_auth_headers("api-key-value", "api-secret-value", "GET", "/private/v1/account/assets")
        assert "api-secret-value" not in headers["API-SIGN"]

"""Tests for signum_adapters.errors, signum_adapters.types, and signum_adapters.protocol."""

from __future__ import annotations

import pytest

from signum_adapters.errors import (
    AuthenticationError,
    ConnectionError,
    ExchangeApiError,
    ExchangeError,
    ExchangeServerError,
    InsufficientBalanceError,
    OrderError,
    RateLimitError,
)
from signum_adapters.gmo_coin.client import GmoCoinAdapter
from signum_adapters.protocol import ExchangeAdapter
from signum_adapters.types import (
    Balance,
    Collateral,
    ExchangeConstraints,
    FxPosition,
    Order,
    OrderSide,
    OrderStatus,
    OrderType,
    PositionSide,
    Ticker,
)

# ── Error hierarchy ───────────────────────────────────────────────────────────


class TestErrorHierarchy:
    def test_exchange_error_is_exception(self):
        assert issubclass(ExchangeError, Exception)

    def test_order_error_is_exchange_error(self):
        assert issubclass(OrderError, ExchangeError)

    def test_insufficient_balance_is_order_error(self):
        assert issubclass(InsufficientBalanceError, OrderError)

    def test_insufficient_balance_is_exchange_error(self):
        assert issubclass(InsufficientBalanceError, ExchangeError)

    def test_authentication_error_is_exchange_error(self):
        assert issubclass(AuthenticationError, ExchangeError)

    def test_rate_limit_error_is_exchange_error(self):
        assert issubclass(RateLimitError, ExchangeError)

    def test_connection_error_is_exchange_error(self):
        assert issubclass(ConnectionError, ExchangeError)

    def test_exchange_api_error_is_exchange_error(self):
        assert issubclass(ExchangeApiError, ExchangeError)

    def test_exchange_server_error_is_exchange_api_error(self):
        assert issubclass(ExchangeServerError, ExchangeApiError)

    def test_exchange_server_error_is_exchange_error(self):
        assert issubclass(ExchangeServerError, ExchangeError)

    def test_can_raise_and_catch_insufficient_balance_as_exchange_error(self):
        with pytest.raises(ExchangeError):
            raise InsufficientBalanceError("not enough funds")

    def test_can_raise_and_catch_server_error_as_api_error(self):
        with pytest.raises(ExchangeApiError):
            raise ExchangeServerError("5xx error")

    def test_exchange_error_message_preserved(self):
        err = ExchangeApiError("ERR-422 details")
        assert "ERR-422 details" in str(err)


# ── Types ─────────────────────────────────────────────────────────────────────


class TestTicker:
    def test_fields(self):
        t = Ticker(symbol="BTC_JPY", ask=6_000_000.0, bid=5_999_000.0, last=5_999_500.0, volume=10.5)
        assert t.symbol == "BTC_JPY"
        assert t.ask == 6_000_000.0
        assert t.bid == 5_999_000.0
        assert t.last == 5_999_500.0
        assert t.volume == 10.5

    def test_is_frozen(self):
        t = Ticker(symbol="BTC_JPY", ask=1.0, bid=1.0, last=1.0, volume=1.0)
        with pytest.raises(Exception):
            t.ask = 2.0  # type: ignore[misc]


class TestBalance:
    def test_default_symbol_is_jpy(self):
        b = Balance(amount=100.0, available=80.0)
        assert b.symbol == "JPY"

    def test_custom_symbol(self):
        b = Balance(amount=1.0, available=1.0, symbol="BTC")
        assert b.symbol == "BTC"


class TestFxPosition:
    def test_fields(self):
        p = FxPosition(
            position_id="111",
            symbol="BTC_JPY",
            side=PositionSide.LONG,
            size=0.1,
            average_price=5_000_000.0,
            unrealized_pnl=50_000.0,
        )
        assert p.position_id == "111"
        assert p.side == PositionSide.LONG


class TestOrder:
    def test_fields(self):
        o = Order(
            order_id="123",
            symbol="BTC_JPY",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            price=None,
            size=0.01,
            status="ORDERED",
        )
        assert o.order_id == "123"
        assert o.price is None


class TestOrderStatus:
    def test_values(self):
        assert OrderStatus.ORDERED == "ORDERED"
        assert OrderStatus.EXECUTED == "EXECUTED"
        assert OrderStatus.CANCELED == "CANCELED"


class TestCollateral:
    def test_fields(self):
        c = Collateral(equity=1_000_000.0, available_amount=800_000.0, margin=200_000.0, margin_ratio=0.2)
        assert c.symbol == "JPY"


class TestExchangeConstraints:
    def test_fields(self):
        ec = ExchangeConstraints(
            symbol="BTC_JPY",
            min_order_size=0.01,
            max_order_size=100.0,
            size_step=0.01,
            price_step=1.0,
        )
        assert ec.symbol == "BTC_JPY"


# ── Protocol ──────────────────────────────────────────────────────────────────


class TestExchangeAdapterProtocol:
    def test_gmo_coin_adapter_is_instance(self):
        """GmoCoinAdapter must satisfy ExchangeAdapter structurally."""
        assert isinstance(GmoCoinAdapter(), ExchangeAdapter)

    def test_protocol_is_runtime_checkable(self):
        """ExchangeAdapter must be decorated with @runtime_checkable."""
        # If not runtime_checkable, isinstance raises TypeError.
        result = isinstance(GmoCoinAdapter(), ExchangeAdapter)
        assert result is True

    def test_non_adapter_fails_isinstance(self):
        class NotAnAdapter:
            pass

        assert not isinstance(NotAnAdapter(), ExchangeAdapter)


# ── Public exports from signum_adapters ───────────────────────────────────────


class TestPublicExports:
    def test_all_types_importable_from_top_level(self):
        import signum_adapters

        for name in [
            "ExchangeAdapter",
            "Ticker", "Balance", "Order", "FxPosition", "Candle",
            "Collateral", "ExchangeConstraints",
            "OrderSide", "OrderType", "OrderStatus", "PositionSide",
            "ExchangeError", "OrderError", "InsufficientBalanceError",
            "AuthenticationError", "RateLimitError", "ConnectionError",
            "ExchangeApiError", "ExchangeServerError",
        ]:
            assert hasattr(signum_adapters, name), f"signum_adapters.{name} is missing"

"""Unit tests for signum_adapters.gmo_coin.parsers."""

from __future__ import annotations

import pytest

from signum_adapters.gmo_coin.models import (
    OrderSide,
    OrderType,
    PositionSide,
)
from signum_adapters.gmo_coin.parsers import (
    parse_api_error,
    parse_balance,
    parse_order,
    parse_position,
    parse_ticker,
)

# ── parse_ticker ──────────────────────────────────────────────────────────────


class TestParseTicker:
    def _sample(self) -> dict:
        return {
            "symbol": "BTC_JPY",
            "ask": "6000000",
            "bid": "5999000",
            "last": "5999500",
            "volume": "10.5",
        }

    def test_symbol(self):
        ticker = parse_ticker(self._sample())
        assert ticker.symbol == "BTC_JPY"

    def test_ask(self):
        ticker = parse_ticker(self._sample())
        assert ticker.ask == 6_000_000.0

    def test_bid(self):
        ticker = parse_ticker(self._sample())
        assert ticker.bid == 5_999_000.0

    def test_last(self):
        ticker = parse_ticker(self._sample())
        assert ticker.last == 5_999_500.0

    def test_volume(self):
        ticker = parse_ticker(self._sample())
        assert ticker.volume == 10.5

    def test_missing_optional_fields_default_to_zero(self):
        ticker = parse_ticker({"symbol": "ETH_JPY"})
        assert ticker.ask == 0.0
        assert ticker.bid == 0.0
        assert ticker.last == 0.0
        assert ticker.volume == 0.0

    def test_raises_on_missing_symbol(self):
        with pytest.raises(KeyError):
            parse_ticker({"ask": "100"})


# ── parse_balance ─────────────────────────────────────────────────────────────


class TestParseBalance:
    def _sample(self) -> dict:
        return {
            "symbol": "JPY",
            "amount": "1000000",
            "available": "800000",
        }

    def test_symbol(self):
        balance = parse_balance(self._sample())
        assert balance.symbol == "JPY"

    def test_amount(self):
        balance = parse_balance(self._sample())
        assert balance.amount == 1_000_000.0

    def test_available(self):
        balance = parse_balance(self._sample())
        assert balance.available == 800_000.0

    def test_defaults(self):
        balance = parse_balance({})
        assert balance.amount == 0.0
        assert balance.available == 0.0
        assert balance.symbol == "JPY"


# ── parse_order ───────────────────────────────────────────────────────────────


class TestParseOrder:
    def _market_buy(self) -> dict:
        return {
            "orderId": 123456,
            "symbol": "BTC_JPY",
            "side": "BUY",
            "executionType": "MARKET",
            "price": "0",
            "size": "0.01",
            "status": "ORDERED",
        }

    def _limit_sell(self) -> dict:
        return {
            "orderId": "789",
            "symbol": "ETH_JPY",
            "side": "SELL",
            "executionType": "LIMIT",
            "price": "300000",
            "size": "0.5",
            "status": "ORDERED",
        }

    def test_order_id_is_string(self):
        order = parse_order(self._market_buy())
        assert order.order_id == "123456"
        assert isinstance(order.order_id, str)

    def test_market_order_price_is_none(self):
        order = parse_order(self._market_buy())
        assert order.price is None

    def test_limit_order_price(self):
        order = parse_order(self._limit_sell())
        assert order.price == 300_000.0

    def test_side_buy(self):
        order = parse_order(self._market_buy())
        assert order.side == OrderSide.BUY

    def test_side_sell(self):
        order = parse_order(self._limit_sell())
        assert order.side == OrderSide.SELL

    def test_execution_type_market(self):
        order = parse_order(self._market_buy())
        assert order.order_type == OrderType.MARKET

    def test_execution_type_limit(self):
        order = parse_order(self._limit_sell())
        assert order.order_type == OrderType.LIMIT

    def test_size(self):
        order = parse_order(self._market_buy())
        assert order.size == 0.01

    def test_status(self):
        order = parse_order(self._market_buy())
        assert order.status == "ORDERED"

    def test_none_price_treated_as_none(self):
        data = self._market_buy()
        data["price"] = None
        order = parse_order(data)
        assert order.price is None


# ── parse_position ────────────────────────────────────────────────────────────


class TestParsePosition:
    def _long(self) -> dict:
        return {
            "positionId": 111,
            "symbol": "BTC_JPY",
            "side": "BUY",
            "size": "0.1",
            "price": "5000000",
            "lossGain": "50000",
        }

    def _short(self) -> dict:
        return {
            "positionId": "222",
            "symbol": "ETH_JPY",
            "side": "SELL",
            "size": "1.0",
            "price": "280000",
            "lossGain": "-3000",
        }

    def test_long_side(self):
        pos = parse_position(self._long())
        assert pos.side == PositionSide.LONG

    def test_short_side(self):
        pos = parse_position(self._short())
        assert pos.side == PositionSide.SHORT

    def test_position_id_is_string(self):
        pos = parse_position(self._long())
        assert pos.position_id == "111"

    def test_size(self):
        pos = parse_position(self._long())
        assert pos.size == 0.1

    def test_average_price(self):
        pos = parse_position(self._long())
        assert pos.average_price == 5_000_000.0

    def test_unrealized_pnl_positive(self):
        pos = parse_position(self._long())
        assert pos.unrealized_pnl == 50_000.0

    def test_unrealized_pnl_negative(self):
        pos = parse_position(self._short())
        assert pos.unrealized_pnl == -3_000.0

    def test_defaults_on_empty(self):
        pos = parse_position({})
        assert pos.position_id == ""
        assert pos.symbol == ""
        assert pos.size == 0.0
        assert pos.average_price == 0.0
        assert pos.unrealized_pnl == 0.0


# ── parse_api_error ───────────────────────────────────────────────────────────


class TestParseApiError:
    def test_returns_none_when_no_messages(self):
        assert parse_api_error({"status": 0}) is None

    def test_returns_none_when_messages_empty(self):
        assert parse_api_error({"status": 1, "messages": []}) is None

    def test_extracts_message_string(self):
        data = {
            "status": 1,
            "messages": [{"message_string": "ERR-422"}],
        }
        assert parse_api_error(data) == "ERR-422"

    def test_handles_missing_message_string_key(self):
        data = {
            "status": 1,
            "messages": [{"code": "ERR-101"}],
        }
        result = parse_api_error(data)
        assert result is not None
        assert isinstance(result, str)

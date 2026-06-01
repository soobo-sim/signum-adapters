"""Response parsers for GMO Coin API JSON payloads."""

from __future__ import annotations

import logging
from typing import Any

from signum_adapters.gmo_coin.models import (
    Balance,
    Collateral,
    ExchangeConstraints,
    Order,
    OrderSide,
    OrderType,
    Position,
    PositionSide,
    Ticker,
)

logger = logging.getLogger(__name__)


def parse_ticker(data: dict[str, Any]) -> Ticker:
    """Parse a single ticker entry from ``/public/v1/ticker`` response data.

    Args:
        data: One element from the ``data`` list in the API response.

    Returns:
        ``Ticker`` domain model.

    Raises:
        KeyError: If required fields are missing from ``data``.
        ValueError: If numeric fields cannot be converted.
    """
    return Ticker(
        symbol=data["symbol"],
        ask=float(data.get("ask", 0)),
        bid=float(data.get("bid", 0)),
        last=float(data.get("last", 0)),
        volume=float(data.get("volume", 0)),
    )


def parse_balance(data: dict[str, Any]) -> Balance:
    """Parse a single balance entry from ``/private/v1/account/assets`` response.

    Args:
        data: One element from the ``data`` list in the API response.

    Returns:
        ``Balance`` domain model.
    """
    return Balance(
        amount=float(data.get("amount", 0)),
        available=float(data.get("available", 0)),
        symbol=data.get("symbol", "JPY"),
    )


def parse_order(data: dict[str, Any]) -> Order:
    """Parse a single order entry from the GMO Coin order API response.

    Args:
        data: One order object from the API response ``data`` field.

    Returns:
        ``Order`` domain model.
    """
    price_raw = data.get("price")
    price = float(price_raw) if price_raw not in (None, "", "0", 0) else None
    return Order(
        order_id=str(data.get("orderId", "")),
        symbol=data.get("symbol", ""),
        side=OrderSide(data.get("side", "BUY")),
        order_type=OrderType(data.get("executionType", "MARKET")),
        price=price,
        size=float(data.get("size", 0)),
        status=data.get("status", ""),
    )


def parse_position(data: dict[str, Any]) -> Position:
    """Parse a single position entry from ``/private/v1/openPositions`` response.

    Args:
        data: One position object from the API response ``data`` list.

    Returns:
        ``Position`` domain model.
    """
    side_raw = data.get("side", "BUY")
    position_side = PositionSide.LONG if side_raw == "BUY" else PositionSide.SHORT
    return Position(
        position_id=str(data.get("positionId", "")),
        symbol=data.get("symbol", ""),
        side=position_side,
        size=float(data.get("size", 0)),
        average_price=float(data.get("price", 0)),
        unrealized_pnl=float(data.get("lossGain", 0)),
    )


def parse_api_error(response_data: dict[str, Any]) -> str | None:
    """Extract the first error message from a GMO Coin API error response.

    Args:
        response_data: Parsed JSON response body.

    Returns:
        Error message string, or ``None`` if no error messages are present.
    """
    messages = response_data.get("messages", [])
    if not messages:
        return None
    first = messages[0] if isinstance(messages, list) else {}
    return first.get("message_string", str(first))


def parse_collateral(data: dict[str, Any]) -> Collateral:
    """Parse the margin account entry from ``/private/v1/account/margin`` response.

    Args:
        data: The ``data`` object from the API response.

    Returns:
        ``Collateral`` domain model.
    """
    return Collateral(
        equity=float(data.get("actualProfitLoss", 0)),
        available_amount=float(data.get("availableAmount", 0)),
        margin=float(data.get("margin", 0)),
        margin_ratio=float(data.get("marginRatio", 0)),
        symbol="JPY",
    )


def parse_constraints(data: dict[str, Any]) -> ExchangeConstraints:
    """Parse a single symbol entry from ``/public/v1/symbols`` response.

    Args:
        data: One element from the ``data`` list in the API response.

    Returns:
        ``ExchangeConstraints`` domain model.

    Raises:
        KeyError: If the ``symbol`` field is missing.
    """
    return ExchangeConstraints(
        symbol=data["symbol"],
        min_order_size=float(data.get("minOrderSize", 0)),
        max_order_size=float(data.get("maxOrderSize", 0)),
        size_step=float(data.get("sizeStep", 0)),
        price_step=float(data.get("tickSize", 0)),
    )


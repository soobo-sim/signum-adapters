"""Common data transfer objects (DTOs) for exchange adapter interfaces.

These types are the canonical definitions used by ExchangeAdapter implementations
and by signum-engine consumers.  GMO Coin-specific code re-exports these types
from ``signum_adapters.gmo_coin.models`` for backward compatibility.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

# ── Enumerations ──────────────────────────────────────────────────────────────


class OrderSide(StrEnum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(StrEnum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"


class OrderStatus(StrEnum):
    ORDERED = "ORDERED"
    EXECUTED = "EXECUTED"
    EXPIRED = "EXPIRED"
    CANCELED = "CANCELED"
    MODIFYING = "MODIFYING"
    CANCELING = "CANCELING"


class PositionSide(StrEnum):
    LONG = "LONG"
    SHORT = "SHORT"


# ── Market data ───────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class Ticker:
    """Best bid/ask snapshot for a trading pair."""

    symbol: str
    ask: float
    bid: float
    last: float
    volume: float


@dataclass(frozen=True)
class Candle:
    """OHLCV candlestick data for a single interval."""

    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    timestamp: datetime


# ── Account data ──────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class Balance:
    """Spot asset balance for a single currency."""

    amount: float
    available: float
    symbol: str = "JPY"


@dataclass(frozen=True)
class Collateral:
    """Margin/collateral account summary."""

    equity: float
    available_amount: float
    margin: float
    margin_ratio: float
    symbol: str = "JPY"


# ── Positions and orders ──────────────────────────────────────────────────────


@dataclass(frozen=True)
class FxPosition:
    """An open leveraged (FX/CFD) position."""

    position_id: str
    symbol: str
    side: PositionSide
    size: float
    average_price: float
    unrealized_pnl: float


@dataclass(frozen=True)
class Order:
    """A submitted or completed order."""

    order_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    price: float | None
    size: float
    status: str


# ── Exchange metadata ─────────────────────────────────────────────────────────


@dataclass(frozen=True)
class ExchangeConstraints:
    """Trading constraints for a symbol on a specific exchange."""

    symbol: str
    min_order_size: float
    max_order_size: float
    size_step: float
    price_step: float

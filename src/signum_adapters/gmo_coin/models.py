"""Data models for GMO Coin API responses and domain objects."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class OrderSide(StrEnum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(StrEnum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"


class PositionSide(StrEnum):
    LONG = "LONG"
    SHORT = "SHORT"


@dataclass(frozen=True)
class Ticker:
    symbol: str
    ask: float
    bid: float
    last: float
    volume: float


@dataclass(frozen=True)
class Balance:
    amount: float
    available: float
    symbol: str = "JPY"


@dataclass(frozen=True)
class Order:
    order_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    price: float | None
    size: float
    status: str


@dataclass(frozen=True)
class Position:
    position_id: str
    symbol: str
    side: PositionSide
    size: float
    average_price: float
    unrealized_pnl: float

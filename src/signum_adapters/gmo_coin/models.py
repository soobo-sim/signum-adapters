"""Data models for GMO Coin API responses and domain objects.

All canonical types are defined in ``signum_adapters.types``.
This module re-exports them for backward compatibility and adds the
GMO-Coin-specific ``Position`` alias for ``FxPosition``.
"""

from __future__ import annotations

from signum_adapters.types import (
    Balance,
    FxPosition,
    Order,
    OrderSide,
    OrderStatus,
    OrderType,
    PositionSide,
    Ticker,
)

# GMO Coin uses the term "Position" rather than "FxPosition" in its API.
# ``Position`` is kept as a backward-compatible alias.
Position = FxPosition

__all__ = [
    "Balance",
    "FxPosition",
    "Order",
    "OrderSide",
    "OrderStatus",
    "OrderType",
    "Position",
    "PositionSide",
    "Ticker",
]

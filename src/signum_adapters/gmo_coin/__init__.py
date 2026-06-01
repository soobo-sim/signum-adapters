"""GMO Coin adapter package.

Public re-exports for convenient import::

    from signum_adapters.gmo_coin import GmoCoinAdapter
"""

from signum_adapters.gmo_coin.client import (
    ExchangeApiError,
    ExchangeServerError,
    GmoCoinAdapter,
    InsufficientBalanceError,
)
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
from signum_adapters.gmo_coin.utils import _floor_to_step, is_maintenance_window

__all__ = [
    "GmoCoinAdapter",
    "ExchangeApiError",
    "ExchangeServerError",
    "InsufficientBalanceError",
    "Balance",
    "Collateral",
    "ExchangeConstraints",
    "Order",
    "OrderSide",
    "OrderType",
    "Position",
    "PositionSide",
    "Ticker",
    "_floor_to_step",
    "is_maintenance_window",
]

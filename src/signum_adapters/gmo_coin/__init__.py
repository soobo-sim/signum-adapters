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
    Order,
    OrderSide,
    OrderType,
    Position,
    PositionSide,
    Ticker,
)

__all__ = [
    "GmoCoinAdapter",
    "ExchangeApiError",
    "ExchangeServerError",
    "InsufficientBalanceError",
    "Balance",
    "Order",
    "OrderSide",
    "OrderType",
    "Position",
    "PositionSide",
    "Ticker",
]

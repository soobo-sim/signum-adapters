"""signum-adapters: Exchange adapter implementations for signum-engine."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("signum-adapters")
except PackageNotFoundError:
    __version__ = "0.0.0-dev"

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
from signum_adapters.protocol import ExchangeAdapter
from signum_adapters.types import (
    Balance,
    Candle,
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

__all__ = [
    "__version__",
    # Protocol
    "ExchangeAdapter",
    # Types
    "Balance",
    "Candle",
    "Collateral",
    "ExchangeConstraints",
    "FxPosition",
    "Order",
    "OrderSide",
    "OrderStatus",
    "OrderType",
    "PositionSide",
    "Ticker",
    # Errors
    "AuthenticationError",
    "ConnectionError",
    "ExchangeApiError",
    "ExchangeError",
    "ExchangeServerError",
    "InsufficientBalanceError",
    "OrderError",
    "RateLimitError",
]

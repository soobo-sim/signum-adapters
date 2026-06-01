"""ExchangeAdapter Protocol — the contract that every exchange adapter must satisfy.

All exchange adapter implementations (e.g. ``GmoCoinAdapter``) must structurally
conform to this Protocol so that signum-engine can use them interchangeably.

Usage::

    from signum_adapters.protocol import ExchangeAdapter

    def accepts_any_adapter(adapter: ExchangeAdapter) -> None:
        ...

    assert isinstance(my_adapter, ExchangeAdapter)  # runtime check
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol, runtime_checkable

from signum_adapters.types import (
    Balance,
    Collateral,
    ExchangeConstraints,
    FxPosition,
    Order,
    Ticker,
)


@runtime_checkable
class ExchangeAdapter(Protocol):
    """Structural protocol for exchange adapter implementations.

    Every method is ``async``; implementations must use an async HTTP client
    internally.  The adapter is expected to be used as an async context manager
    to manage the lifecycle of its HTTP session::

        async with MyAdapter() as adapter:
            ticker = await adapter.get_ticker("BTC_JPY")
    """

    async def __aenter__(self) -> ExchangeAdapter:
        ...

    async def __aexit__(self, *args: Any) -> None:
        ...

    async def connect(self) -> None:
        """Open the underlying HTTP (and WebSocket) session."""
        ...

    async def disconnect(self) -> None:
        """Close the underlying HTTP (and WebSocket) session."""
        ...

    async def get_ticker(self, symbol: str) -> Ticker:
        """Return the current best bid/ask snapshot for *symbol*."""
        ...

    async def get_balance(self) -> list[Balance]:
        """Return a list of asset balances for the authenticated account."""
        ...

    async def get_positions(self, symbol: str) -> list[FxPosition]:
        """Return a list of open leveraged positions for *symbol*."""
        ...

    async def get_collateral(self) -> Collateral:
        """Return the margin/collateral account summary."""
        ...

    async def get_exchange_constraints(self, symbol: str) -> ExchangeConstraints:
        """Return trading constraints (lot size, tick size, etc.) for *symbol*."""
        ...

    async def create_order(
        self,
        symbol: str,
        side: str,
        size: str,
        *,
        execution_type: str = "MARKET",
        price: str | None = None,
        time_in_force: str | None = None,
    ) -> Order:
        """Submit a new order and return the resulting ``Order`` object."""
        ...

    async def close_position(self, position_id: str, symbol: str, size: float) -> Order:
        """Close (or partially close) an open position and return the resulting ``Order``."""
        ...

    async def subscribe_trades(self, symbol: str, callback: Callable[[Any], Any]) -> None:
        """Subscribe to the public real-time trade stream for *symbol*.

        *callback* is invoked for every incoming trade message.
        """
        ...

    async def subscribe_executions(self, callback: Callable[[Any], Any]) -> None:
        """Subscribe to the private real-time execution event stream.

        *callback* is invoked for every incoming execution event.
        """
        ...

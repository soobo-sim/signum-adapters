"""GmoCoinAdapter — ExchangeAdapter Protocol implementation for GMO Coin.

Uses httpx.AsyncClient for all HTTP communication.  The adapter is stateless
with respect to orders/positions: it delegates persistence entirely to the
calling layer (signum-engine).

Error handling contract:
  - ERR-422  → raises ``InsufficientBalanceError``
  - ERR-5xx  → raises ``ExchangeServerError``
  - Other non-zero status codes → raises ``ExchangeApiError``
"""

from __future__ import annotations

import json
import logging
from collections.abc import Callable
from typing import Any

import httpx
import websockets

from signum_adapters.errors import (
    ExchangeApiError,
    ExchangeServerError,
    InsufficientBalanceError,
)
from signum_adapters.gmo_coin.models import (
    Balance,
    Collateral,
    ExchangeConstraints,
    Order,
    Position,
    Ticker,
)
from signum_adapters.gmo_coin.parsers import (
    parse_balance,
    parse_collateral,
    parse_constraints,
    parse_order,
    parse_position,
    parse_ticker,
)
from signum_adapters.gmo_coin.signer import build_auth_headers
from signum_adapters.settings import gmo_coin_settings

logger = logging.getLogger(__name__)


# ── GmoCoinAdapter ────────────────────────────────────────────────────────────


class GmoCoinAdapter:
    """Async HTTP adapter for the GMO Coin exchange private/public REST API.

    Usage::

        async with GmoCoinAdapter() as adapter:
            ticker = await adapter.get_ticker("BTC_JPY")

    The adapter is safe to reuse across requests because it maintains a single
    ``httpx.AsyncClient`` for the lifetime of the context manager.
    """

    def __init__(self) -> None:
        self._settings = gmo_coin_settings
        self._client: httpx.AsyncClient | None = None

    # ── Context manager ───────────────────────────────────────────────────────

    async def __aenter__(self) -> GmoCoinAdapter:
        await self.connect()
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.disconnect()

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    async def connect(self) -> None:
        """Open the underlying HTTP session.

        Idempotent: calling ``connect`` on an already-connected adapter is safe.
        """
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self._settings.GMO_COIN_BASE_URL,
                timeout=self._settings.REQUEST_TIMEOUT,
            )

    async def disconnect(self) -> None:
        """Close the underlying HTTP session.

        Idempotent: calling ``disconnect`` on an already-disconnected adapter is safe.
        """
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    # ── Internal helpers ──────────────────────────────────────────────────────

    @property
    def _http(self) -> httpx.AsyncClient:
        if self._client is None:
            raise RuntimeError("GmoCoinAdapter must be used as an async context manager.")
        return self._client

    async def _get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Send a GET request and return the parsed JSON response."""
        response = await self._http.get(path, params=params)
        response.raise_for_status()
        return response.json()

    async def _post_private(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        """Send an authenticated POST request and return the parsed response."""
        body_str = json.dumps(body, separators=(",", ":"))
        headers = build_auth_headers(
            api_key=self._settings.GMO_COIN_API_KEY,
            api_secret=self._settings.GMO_COIN_API_SECRET,
            method="POST",
            path=path,
            body=body_str,
        )
        response = await self._http.post(
            path,
            content=body_str,
            headers={**headers, "Content-Type": "application/json"},
        )
        response.raise_for_status()
        return response.json()

    async def _get_private(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Send an authenticated GET request and return the parsed response."""
        query = ""
        if params:
            query = "?" + "&".join(f"{k}={v}" for k, v in params.items())
        headers = build_auth_headers(
            api_key=self._settings.GMO_COIN_API_KEY,
            api_secret=self._settings.GMO_COIN_API_SECRET,
            method="GET",
            path=path + query,
        )
        response = await self._http.get(path, params=params, headers=headers)
        response.raise_for_status()
        return response.json()

    def _check_api_status(self, data: dict[str, Any], path: str) -> None:
        """Raise a typed exception if the GMO Coin API status code is non-zero.

        Args:
            data: Parsed API JSON response.
            path: Request path used for log context.

        Raises:
            InsufficientBalanceError: When ``status`` is ``"ERR-422"``.
            ExchangeServerError: When ``status`` starts with ``"ERR-5"``.
            ExchangeApiError: For any other non-zero ``status``.
        """
        status = data.get("status", 0)
        if status == 0:
            return
        messages = data.get("messages", [])
        logger.warning("GMO Coin API error on %s: status=%s messages=%s", path, status, messages)
        status_str = str(status)
        if status_str == "ERR-422":
            raise InsufficientBalanceError(f"Insufficient balance [{path}]: {messages}")
        if status_str.startswith("ERR-5"):
            raise ExchangeServerError(f"Exchange server error [{path}]: status={status} {messages}")
        raise ExchangeApiError(f"API error [{path}]: status={status} {messages}")

    # ── Public API ────────────────────────────────────────────────────────────

    async def get_ticker(self, symbol: str) -> Ticker:
        """Fetch the best bid/ask ticker for *symbol*.

        Args:
            symbol: Trading pair symbol (e.g. ``"BTC_JPY"``).

        Returns:
            ``Ticker`` with ask, bid, last, and volume fields populated.

        Raises:
            ExchangeApiError: On non-zero API status.
            httpx.HTTPStatusError: On HTTP-level errors.
        """
        path = "/public/v1/ticker"
        raw = await self._get(path, params={"symbol": symbol})
        self._check_api_status(raw, path)
        data_list = raw.get("data", [])
        if not data_list:
            raise ExchangeApiError(f"No ticker data returned for symbol={symbol}")
        return parse_ticker(data_list[0])

    # ── Private API ───────────────────────────────────────────────────────────

    async def get_balance(self) -> list[Balance]:
        """Fetch account asset balances.

        Returns:
            List of ``Balance`` objects for each held asset.

        Raises:
            ExchangeApiError: On non-zero API status.
        """
        path = "/private/v1/account/assets"
        raw = await self._get_private(path)
        self._check_api_status(raw, path)
        return [parse_balance(item) for item in raw.get("data", [])]

    async def get_positions(self, symbol: str) -> list[Position]:
        """Fetch open positions for *symbol*.

        Args:
            symbol: Trading pair symbol (e.g. ``"BTC_JPY"``).

        Returns:
            List of open ``Position`` objects.

        Raises:
            ExchangeApiError: On non-zero API status.
        """
        path = "/private/v1/openPositions"
        raw = await self._get_private(path, params={"symbol": symbol})
        self._check_api_status(raw, path)
        items = raw.get("data", {})
        if isinstance(items, dict):
            items = items.get("list", [])
        return [parse_position(item) for item in items]

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
        """Place a new order on GMO Coin.

        Use ``side="BUY"`` / ``execution_type="MARKET"`` to open a long position
        (``MARKET_BUY``), and ``side="BUY_CLOSE"`` to close a short position
        (``MARKET_BUY_CLOSE``).  The adapter does NOT merge these into a single
        ``side`` field — the caller must supply the correct GMO Coin side string.

        Args:
            symbol: Trading pair (e.g. ``"BTC_JPY"``).
            side: GMO Coin side string: ``"BUY"``, ``"SELL"``,
                ``"BUY_CLOSE"``, or ``"SELL_CLOSE"``.
            size: Order quantity as a string (GMO Coin requires string).
            execution_type: ``"MARKET"`` (default) or ``"LIMIT"``.
            price: Limit price string; required when *execution_type* is ``"LIMIT"``.
            time_in_force: Optional time-in-force (e.g. ``"FAK"``).

        Returns:
            ``Order`` with the assigned order ID from GMO Coin.

        Raises:
            InsufficientBalanceError: When GMO Coin returns ERR-422.
            ExchangeServerError: When GMO Coin returns a 5xx status.
            ExchangeApiError: On any other non-zero API status.
        """
        path = "/private/v1/order"
        body: dict[str, Any] = {
            "symbol": symbol,
            "side": side,
            "executionType": execution_type,
            "size": size,
        }
        if price is not None:
            body["price"] = price
        if time_in_force is not None:
            body["timeInForce"] = time_in_force

        raw = await self._post_private(path, body)
        self._check_api_status(raw, path)
        order_data = raw.get("data", {})
        if isinstance(order_data, (int, str)):
            order_data = {"orderId": str(order_data)}
        order_data.setdefault("symbol", symbol)
        order_data.setdefault("side", side)
        order_data.setdefault("executionType", execution_type)
        order_data.setdefault("size", size)
        order_data.setdefault("status", "ORDERED")
        return parse_order(order_data)

    async def get_open_positions(self, symbol: str) -> list[Position]:
        """Fetch open FX positions for *symbol*.

        This is an alias for :meth:`get_positions` provided for compatibility
        with the signum-engine naming convention.

        Args:
            symbol: Trading pair symbol (e.g. ``"BTC_JPY"``).

        Returns:
            List of open ``Position`` (``FxPosition``) objects.

        Raises:
            ExchangeApiError: On non-zero API status.
        """
        return await self.get_positions(symbol)

    async def close_position(self, position_id: str, symbol: str, size: float) -> Order:
        """Close (or partially close) an open position.

        Sends a ``closeOrder`` request to GMO Coin using ``executionType="MARKET"``.

        Args:
            position_id: The ID of the position to close.
            symbol: Trading pair symbol (e.g. ``"BTC_JPY"``).
            size: The quantity to close.

        Returns:
            ``Order`` with the assigned order ID from GMO Coin.

        Raises:
            InsufficientBalanceError: When GMO Coin returns ERR-422.
            ExchangeServerError: When GMO Coin returns a 5xx status.
            ExchangeApiError: On any other non-zero API status.
        """
        path = "/private/v1/closeOrder"
        body: dict[str, Any] = {
            "symbol": symbol,
            "executionType": "MARKET",
            "settlePosition": [
                {"positionId": position_id, "size": str(size)},
            ],
        }
        raw = await self._post_private(path, body)
        self._check_api_status(raw, path)
        order_data = raw.get("data", {})
        if isinstance(order_data, (int, str)):
            order_data = {"orderId": str(order_data)}
        order_data.setdefault("symbol", symbol)
        order_data.setdefault("side", "SELL")
        order_data.setdefault("executionType", "MARKET")
        order_data.setdefault("size", str(size))
        order_data.setdefault("status", "ORDERED")
        return parse_order(order_data)

    async def get_collateral(self) -> Collateral:
        """Fetch the margin/collateral account summary.

        Returns:
            ``Collateral`` with equity, available amount, margin, and ratio.

        Raises:
            ExchangeApiError: On non-zero API status.
        """
        path = "/private/v1/account/margin"
        raw = await self._get_private(path)
        self._check_api_status(raw, path)
        return parse_collateral(raw.get("data", {}))

    async def get_exchange_constraints(self, symbol: str) -> ExchangeConstraints:
        """Fetch trading constraints for *symbol*.

        Args:
            symbol: Trading pair symbol (e.g. ``"BTC_JPY"``).

        Returns:
            ``ExchangeConstraints`` with lot size, tick size, etc.

        Raises:
            ExchangeApiError: If *symbol* is not found or on non-zero API status.
        """
        path = "/public/v1/symbols"
        raw = await self._get(path)
        self._check_api_status(raw, path)
        items = raw.get("data", [])
        for item in items:
            if item.get("symbol") == symbol:
                return parse_constraints(item)
        raise ExchangeApiError(f"Symbol not found in exchange constraints: {symbol!r}")

    # ── WebSocket ─────────────────────────────────────────────────────────────

    async def subscribe_trades(self, symbol: str, callback: Callable[[Any], Any]) -> None:
        """Subscribe to the public real-time trade stream for *symbol*.

        Opens a WebSocket connection to the GMO Coin public endpoint and invokes
        *callback* for each incoming trade message.  The method returns only when
        the WebSocket connection is closed.

        Args:
            symbol: Trading pair symbol (e.g. ``"BTC_JPY"``).
            callback: Async or sync callable invoked with each parsed message dict.

        Raises:
            websockets.exceptions.WebSocketException: On connection errors.
        """
        import asyncio
        import inspect

        url = self._settings.GMO_COIN_WS_PUBLIC_URL
        subscribe_msg = json.dumps({"command": "subscribe", "channel": "trades", "symbol": symbol})
        async with websockets.connect(url) as ws:
            await ws.send(subscribe_msg)
            async for raw_msg in ws:
                data = json.loads(raw_msg)
                if inspect.iscoroutinefunction(callback):
                    await callback(data)
                else:
                    asyncio.get_event_loop().call_soon(callback, data)

    async def subscribe_executions(self, callback: Callable[[Any], Any]) -> None:
        """Subscribe to the private real-time execution event stream.

        Opens an authenticated WebSocket connection to the GMO Coin private
        endpoint and invokes *callback* for each incoming execution event.
        The method returns only when the WebSocket connection is closed.

        Args:
            callback: Async or sync callable invoked with each parsed message dict.

        Raises:
            websockets.exceptions.WebSocketException: On connection errors.
        """
        import asyncio
        import inspect

        url = self._settings.GMO_COIN_WS_PRIVATE_URL
        subscribe_msg = json.dumps({"command": "subscribe", "channel": "executionEvents"})
        async with websockets.connect(url) as ws:
            await ws.send(subscribe_msg)
            async for raw_msg in ws:
                data = json.loads(raw_msg)
                if inspect.iscoroutinefunction(callback):
                    await callback(data)
                else:
                    asyncio.get_event_loop().call_soon(callback, data)

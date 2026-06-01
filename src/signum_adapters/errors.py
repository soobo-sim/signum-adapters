"""Unified error hierarchy for signum-adapters exchange integrations.

Hierarchy
---------
ExchangeError
├── OrderError
│   └── InsufficientBalanceError   (GMO ERR-422)
├── AuthenticationError
├── RateLimitError
├── ConnectionError
├── ExchangeApiError               (non-zero GMO API status code)
│   └── ExchangeServerError        (GMO ERR-5xx)
"""

from __future__ import annotations


class ExchangeError(Exception):
    """Base class for all exchange-related errors."""


class OrderError(ExchangeError):
    """Raised when an order operation fails."""


class InsufficientBalanceError(OrderError):
    """Raised when the exchange reports insufficient balance (GMO ERR-422)."""


class AuthenticationError(ExchangeError):
    """Raised when API credentials are rejected by the exchange."""


class RateLimitError(ExchangeError):
    """Raised when the exchange rate limit is exceeded."""


class ConnectionError(ExchangeError):
    """Raised when a network-level connection to the exchange fails."""


class ExchangeApiError(ExchangeError):
    """Raised when the exchange API returns a non-zero application status code."""


class ExchangeServerError(ExchangeApiError):
    """Raised when the exchange returns a 5xx server error (GMO ERR-5xx)."""

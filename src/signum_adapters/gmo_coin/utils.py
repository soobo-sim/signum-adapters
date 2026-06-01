"""Utility helpers for the GMO Coin adapter."""

from __future__ import annotations

import math
from datetime import datetime, timedelta, timezone

# GMO Coin maintenance window: every Saturday 16:00–17:00 JST
_JST = timezone(timedelta(hours=9))
_MAINTENANCE_WEEKDAY = 5   # Saturday
_MAINTENANCE_HOUR_START = 16
_MAINTENANCE_HOUR_END = 17


def _floor_to_step(value: float, step: float) -> float:
    """Return *value* rounded **down** to the nearest multiple of *step*.

    Args:
        value: The raw numeric value to quantise.
        step:  The minimum increment (e.g. ``0.01`` for 2-decimal-place sizes).

    Returns:
        The largest multiple of *step* that is ≤ *value*.

    Examples::

        >>> _floor_to_step(0.123, 0.01)
        0.12
        >>> _floor_to_step(1.999, 0.5)
        1.5
    """
    if step <= 0:
        raise ValueError(f"step must be positive, got {step!r}")
    return math.floor(value / step) * step


def is_maintenance_window() -> bool:
    """Return ``True`` if the current time falls inside GMO Coin's weekly maintenance window.

    GMO Coin performs scheduled maintenance every **Saturday 16:00–17:00 JST**.
    The check is based on the current wall-clock time converted to JST.

    Returns:
        ``True`` during the maintenance window, ``False`` otherwise.
    """
    now = datetime.now(_JST)
    return now.weekday() == _MAINTENANCE_WEEKDAY and _MAINTENANCE_HOUR_START <= now.hour < _MAINTENANCE_HOUR_END

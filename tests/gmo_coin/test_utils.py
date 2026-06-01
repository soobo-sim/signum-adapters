"""Unit tests for signum_adapters.gmo_coin.utils."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest

from signum_adapters.gmo_coin.utils import _floor_to_step, is_maintenance_window

# ── _floor_to_step ────────────────────────────────────────────────────────────

_JST = timezone(timedelta(hours=9))


class TestFloorToStep:
    def test_exact_multiple(self):
        assert _floor_to_step(0.10, 0.01) == pytest.approx(0.10)

    def test_rounds_down(self):
        assert _floor_to_step(0.123, 0.01) == pytest.approx(0.12)

    def test_large_step(self):
        assert _floor_to_step(1.999, 0.5) == pytest.approx(1.5)

    def test_integer_step(self):
        assert _floor_to_step(10.9, 1.0) == pytest.approx(10.0)

    def test_value_smaller_than_step(self):
        assert _floor_to_step(0.005, 0.01) == pytest.approx(0.0)

    def test_zero_value(self):
        assert _floor_to_step(0.0, 0.01) == pytest.approx(0.0)

    def test_raises_on_non_positive_step(self):
        with pytest.raises(ValueError):
            _floor_to_step(1.0, 0.0)

    def test_raises_on_negative_step(self):
        with pytest.raises(ValueError):
            _floor_to_step(1.0, -0.01)


# ── is_maintenance_window ─────────────────────────────────────────────────────


class TestIsMaintenanceWindow:
    def test_during_maintenance_returns_true(self):
        # Saturday 16:30 JST
        target = datetime(2024, 1, 6, 16, 30, 0, tzinfo=_JST)
        with patch("signum_adapters.gmo_coin.utils.datetime") as mock_dt:
            mock_dt.now.return_value = target
            assert is_maintenance_window() is True

    def test_at_maintenance_start_returns_true(self):
        # Saturday 16:00 JST
        target = datetime(2024, 1, 6, 16, 0, 0, tzinfo=_JST)
        with patch("signum_adapters.gmo_coin.utils.datetime") as mock_dt:
            mock_dt.now.return_value = target
            assert is_maintenance_window() is True

    def test_at_maintenance_end_returns_false(self):
        # Saturday 17:00 JST — window is [16, 17) so 17:00 is outside
        target = datetime(2024, 1, 6, 17, 0, 0, tzinfo=_JST)
        with patch("signum_adapters.gmo_coin.utils.datetime") as mock_dt:
            mock_dt.now.return_value = target
            assert is_maintenance_window() is False

    def test_saturday_outside_window_returns_false(self):
        # Saturday 15:59 JST
        target = datetime(2024, 1, 6, 15, 59, 0, tzinfo=_JST)
        with patch("signum_adapters.gmo_coin.utils.datetime") as mock_dt:
            mock_dt.now.return_value = target
            assert is_maintenance_window() is False

    def test_weekday_during_maintenance_hours_returns_false(self):
        # Monday 16:30 JST — not Saturday
        target = datetime(2024, 1, 8, 16, 30, 0, tzinfo=_JST)
        with patch("signum_adapters.gmo_coin.utils.datetime") as mock_dt:
            mock_dt.now.return_value = target
            assert is_maintenance_window() is False

    def test_sunday_during_maintenance_hours_returns_false(self):
        # Sunday 16:30 JST — not Saturday
        target = datetime(2024, 1, 7, 16, 30, 0, tzinfo=_JST)
        with patch("signum_adapters.gmo_coin.utils.datetime") as mock_dt:
            mock_dt.now.return_value = target
            assert is_maintenance_window() is False

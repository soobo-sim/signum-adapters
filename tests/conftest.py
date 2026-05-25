"""Test configuration: inject dummy credentials before settings module loads.

Uses os.environ.setdefault so real values from .env are NOT overwritten.
This allows tests to run without a real .env file (CI and local dev).
"""
import os

os.environ.setdefault("GMO_COIN_API_KEY", "dummy-key-for-test")
os.environ.setdefault("GMO_COIN_API_SECRET", "dummy-secret-for-test")

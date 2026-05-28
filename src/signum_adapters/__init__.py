"""signum-adapters: Exchange adapter implementations for signum-engine."""
from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("signum-adapters")
except PackageNotFoundError:
    __version__ = "0.0.0-dev"

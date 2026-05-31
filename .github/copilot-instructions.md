# GitHub Copilot Instructions — signum-adapters

## Repository Purpose

`signum-adapters` provides `ExchangeAdapter` Protocol implementations consumed by
[signum-engine](https://github.com/soobo-sim/trading-engine).

```
signum-engine  ←  ExchangeAdapter Protocol  ←  signum-adapters
                                                  └── GmoCoinAdapter
```

## Stack

| Layer | Technology |
|-------|-----------|
| Language | Python ≥ 3.11 |
| HTTP client | `httpx` (async) |
| Settings / validation | `pydantic-settings` v2 |
| Test framework | `pytest` + `pytest-asyncio` |
| Linter | `ruff` |
| Build backend | `hatchling` |

## Directory Structure

```
signum-adapters/
├── src/
│   └── signum_adapters/        ← all production code lives here
│       ├── __init__.py
│       └── settings.py         ← GmoCoinSettings (pydantic-settings)
├── tests/                      ← pytest test suite
├── .github/
│   ├── agents/
│   │   ├── implementor.agent.md
│   │   └── validator.agent.md
│   ├── copilot-instructions.md  ← this file
│   ├── workflows/
│   └── PULL_REQUEST_TEMPLATE.md
├── pyproject.toml
└── README.md
```

## Dependency Repositories

| Repository | Relationship | Usage |
|------------|-------------|-------|
| [signum-engine](https://github.com/soobo-sim/trading-engine) | Upstream — defines `ExchangeAdapter` Protocol | Import Protocol/ABC definitions only; never import internals |
| [signum-strategy](https://github.com/soobo-sim/signum-strategy) | Sibling | No direct dependency |
| [signum-backtest](https://github.com/soobo-sim/signum-backtest) | Sibling | No direct dependency |

> **Rule**: Only `Protocol` / `ABC` contracts may be imported from `signum_engine`.
> Never import `signum_engine.core`, `signum_engine.adapters`, or `signum_engine.app`.

## ExchangeAdapter Protocol Contract

All adapter classes must implement the following four async methods:

```python
from typing import Protocol

class ExchangeAdapter(Protocol):
    async def create_order(
        self,
        symbol: str,
        side: str,           # "BUY" or "SELL"
        order_type: str,     # e.g. "MARKET_BUY", "MARKET_BUY_CLOSE"
        size: float,
    ) -> dict:
        """Place an order. Returns the raw exchange response dict."""
        ...

    async def get_positions(self, symbol: str) -> list[dict]:
        """Return open positions for the given symbol."""
        ...

    async def get_balance(self) -> dict:
        """Return current account balance information."""
        ...

    async def get_ticker(self, symbol: str) -> dict:
        """Return the latest ticker (bid/ask/last) for the given symbol."""
        ...
```

### GMO Coin — Order Type Mapping

| Intent | GMO Coin `executionType` |
|--------|--------------------------|
| Open long position | `MARKET_BUY` |
| Close short position | `MARKET_BUY_CLOSE` |

## Settings Reference

All configuration is loaded from `src/signum_adapters/settings.py` via
`pydantic-settings`. Never call `os.getenv()` directly.

| Setting | Source | Description |
|---------|--------|-------------|
| `GMO_COIN_BASE_URL` | `.env` / env var | Exchange REST API base URL |
| `REQUEST_TIMEOUT` | `.env` / env var | HTTP request timeout in seconds |
| `POST_RATE_LIMIT` | `.env` / env var | Max POST requests per second (GMO Coin spec: 20) |
| `LOG_LEVEL` | `.env` / env var | Python logging level |
| `GMO_COIN_API_KEY` | CI Secret / `.env` | Exchange API key — **never commit** |
| `GMO_COIN_API_SECRET` | CI Secret / `.env` | Exchange API secret — **never commit** |

## No-Hardcode Principle

| Forbidden ❌ | Correct ✅ |
|-------------|------------|
| `"https://api.coin.z.com"` | `gmo_coin_settings.GMO_COIN_BASE_URL` |
| `timeout = 30` | `gmo_coin_settings.REQUEST_TIMEOUT` |
| `rate_limit = 20` | `gmo_coin_settings.POST_RATE_LIMIT` |
| `os.getenv("GMO_COIN_API_KEY")` | `gmo_coin_settings.GMO_COIN_API_KEY` |

Use `# HARDCODE_OK: <reason>` only for truly immutable values defined by an
external specification (e.g., a fixed algorithm constant).

## Security Rules

- **Never log** API keys, secrets, or raw request headers containing auth tokens.
- Validate external inputs: `order_id` must pass `str.isdigit()` before use.
- Use `response.get("data", {})` pattern — never assume response keys exist.
- Reuse `httpx.AsyncClient` within a request context; do not create a new client per call.

## Common Commands

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests (no live API credentials needed)
python -m pytest tests/ -m "not requires_api_key" --tb=short -q

# Lint
ruff check src/ tests/

# Detect hardcoded secrets / URLs
grep -rn "https://" src/ --include="*.py" | grep -v "HARDCODE_OK\|#\|\"\"\""
grep -rn "os\.getenv" src/ --include="*.py"
```

## Agent Roles

| Agent | File | Responsibility |
|-------|------|---------------|
| implementor | `.github/agents/implementor.agent.md` | Receives Issues, writes adapter code, opens PRs |
| validator | `.github/agents/validator.agent.md` | Reviews PRs for Protocol compliance, security, and test coverage |

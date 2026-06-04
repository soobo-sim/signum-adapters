# signum-adapters

Exchange adapter implementations for [signum-engine](https://github.com/soobo-sim/trading-engine).

## Overview

`signum-adapters` provides `ExchangeAdapter` Protocol implementations for signum-engine.

```
signum-engine  ←  ExchangeAdapter Protocol  ←  signum-adapters
                                                  └── GmoCoinAdapter
```

## Language Policy

> **All code in this repository is written in English.**
> This includes source code, comments, docstrings, commit messages, PR titles, issue titles, and documentation.
>
> User-facing messages (errors, logs displayed to end users) must support multiple languages via a message bundle pattern — no hardcoded locale-specific strings in logic code.
>
> Contributor communication (issues, PR reviews, chat) may be in any language.

## Installation

```bash
pip install -e ".[dev]"
```

## Supported Exchanges

| Exchange | Class | Status |
|----------|-------|--------|
| GMO Coin | `GmoCoinAdapter` | 🚧 In development (v0.0) |

## Development

```bash
# Run tests (no API key required)
pytest -m "not requires_api_key"

# Lint
ruff check src/ tests/
```

## Release Note

- Release publishing is executed manually from `release/vX.Y` branch via GitHub Actions.

## Related Repositories

- [signum-engine](https://github.com/soobo-sim/trading-engine) — Platform core + Protocol definitions
- [signum-strategy](https://github.com/soobo-sim/signum-strategy) — Strategy implementations
- [signum-backtest](https://github.com/soobo-sim/signum-backtest) — Backtesting framework

## License

MIT
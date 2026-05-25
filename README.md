# signum-adapters

Exchange adapter implementations for [signum-engine](https://github.com/soobo-sim/trading-engine).

## 개요

`signum-adapters`는 signum-engine의 `ExchangeAdapter` Protocol을 구현하는 거래소 어댑터 패키지입니다.

```
signum-engine  ←  ExchangeAdapter Protocol  ←  signum-adapters
                                                  └── GmoCoinAdapter
```

## 설치

```bash
pip install -e ".[dev]"
```

## 지원 거래소

| 거래소 | 클래스 | 상태 |
|--------|--------|------|
| GMO Coin | `GmoCoinAdapter` | 🚧 개발 중 (v0.0 예정) |

## 개발

```bash
# 테스트 (API 키 불필요)
pytest -m "not requires_api_key"

# lint
ruff check src/ tests/
```

## 관련 레포
- [signum-engine](https://github.com/soobo-sim/trading-engine) — 플랫폼 코어 + Protocol 정의
- [signum-strategy](https://github.com/soobo-sim/signum-strategy) — 전략 구현
- [signum-backtest](https://github.com/soobo-sim/signum-backtest) — 백테스트 프레임워크

## 라이선스

MIT
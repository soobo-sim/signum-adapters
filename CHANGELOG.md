# Changelog

모든 주목할 만한 변경 사항은 이 파일에 기록됩니다.
형식은 [Keep a Changelog](https://keepachangelog.com/ko/1.0.0/)를 따릅니다.

## [Unreleased]

### Added
- Smoke tests for settings schema and public defaults (`tests/test_smoke.py`)
- `tests/conftest.py`: dummy credential injection for CI/local-dev without `.env`

### Added
- 프로젝트 초기 구조 설정 (pyproject.toml, src layout)
- CI/CD 워크플로우 (ci.yml, cd.yml)
- GitHub 에이전트 정의 (implementor.agent.md, validator.agent.md)
- PR 템플릿 및 validator 자동 트리거 워크플로우

---

## [v0.0] — 예정

### Added
- `GmoCoinAdapter` — ExchangeAdapter Protocol 구현체 이식 (signum-adapters#3)

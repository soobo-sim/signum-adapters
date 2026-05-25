"""signum-adapters 설정.

레포 IN (버전 관리 대상):
  - GMO_COIN_BASE_URL, REQUEST_TIMEOUT, POST_RATE_LIMIT, LOG_LEVEL
  - 기본값이 코드에 정의되어 있으며, 환경변수로 override 가능

레포 OUT (gitignore / CI Secrets):
  - GMO_COIN_API_KEY, GMO_COIN_API_SECRET
  - 기본값 없음 — 미설정 시 ValidationError 발생 (의도적)
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class GmoCoinSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ── 레포 IN: 공개 설정 (기본값 있음) ──────────────────────────────────
    GMO_COIN_BASE_URL: str = "https://api.coin.z.com"
    REQUEST_TIMEOUT: int = 30       # HTTP 요청 타임아웃 (초)
    POST_RATE_LIMIT: int = 20       # GMO Coin POST 레이트 상한 (회/초, API 스펙 고정)  # HARDCODE_OK: GMO Coin API 스펙 불변값
    LOG_LEVEL: str = "INFO"

    # ── 레포 OUT: 시크릿 (기본값 없음 — 미설정 시 즉시 에러) ─────────────
    GMO_COIN_API_KEY: str
    GMO_COIN_API_SECRET: str


# 모듈 로드 시 즉시 검증 — 시크릿 누락을 조기에 감지
gmo_coin_settings = GmoCoinSettings()

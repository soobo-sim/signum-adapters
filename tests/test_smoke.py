"""Smoke tests: verify package imports, settings schema, and defaults."""
from signum_adapters import __version__
from signum_adapters.settings import GmoCoinSettings, gmo_coin_settings


def test_version_is_string():
    assert isinstance(__version__, str)
    assert len(__version__) > 0


def test_settings_required_fields_exist():
    fields = GmoCoinSettings.model_fields
    assert "GMO_COIN_BASE_URL" in fields
    assert "GMO_COIN_API_KEY" in fields
    assert "GMO_COIN_API_SECRET" in fields
    assert "REQUEST_TIMEOUT" in fields
    assert "POST_RATE_LIMIT" in fields
    assert "LOG_LEVEL" in fields


def test_settings_public_defaults():
    """Public config values (repo-IN) must match documented defaults."""
    assert gmo_coin_settings.GMO_COIN_BASE_URL == "https://api.coin.z.com"
    assert gmo_coin_settings.REQUEST_TIMEOUT == 30
    assert gmo_coin_settings.POST_RATE_LIMIT == 20
    assert gmo_coin_settings.LOG_LEVEL == "INFO"


def test_settings_secrets_are_populated():
    """In CI dummy values are injected; in production real keys must be set."""
    assert len(gmo_coin_settings.GMO_COIN_API_KEY) > 0
    assert len(gmo_coin_settings.GMO_COIN_API_SECRET) > 0

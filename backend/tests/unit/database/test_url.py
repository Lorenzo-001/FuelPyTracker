"""tests/unit/database/test_url.py — LOCAL_SQLITE URL resolution (no secrets)."""
import os
from pathlib import Path
from unittest.mock import patch

from src.database.url import is_local_sqlite, resolve_database_url, engine_kwargs_for_url


class TestIsLocalSqlite:
    def test_true_when_env_true(self):
        with patch.dict(os.environ, {"LOCAL_SQLITE": "True"}):
            assert is_local_sqlite() is True

    def test_false_when_absent_or_false(self):
        with patch.dict(os.environ, {"LOCAL_SQLITE": "False"}):
            assert is_local_sqlite() is False


class TestResolveDatabaseUrl:
    def test_local_sqlite_returns_sqlite_file_url(self):
        with patch.dict(os.environ, {"LOCAL_SQLITE": "True"}):
            url = resolve_database_url(secrets_url=None)
        assert url.startswith("sqlite:///")
        assert url.endswith("/data/local.db") or url.endswith("\\data\\local.db") or "data/local.db" in url
        # Directory must exist after resolve
        root = Path(__file__).resolve().parents[3]
        assert (root / "data").is_dir()

    def test_secrets_url_when_not_local(self):
        with patch.dict(os.environ, {"LOCAL_SQLITE": "False"}):
            url = resolve_database_url(secrets_url="postgresql://u:p@h/db")
        assert url == "postgresql://u:p@h/db"

    def test_raises_when_neither(self):
        with patch.dict(os.environ, {"LOCAL_SQLITE": "False"}):
            try:
                resolve_database_url(secrets_url=None)
                assert False, "expected ValueError"
            except ValueError as e:
                assert "LOCAL_SQLITE" in str(e)


class TestEngineKwargs:
    def test_sqlite_gets_check_same_thread(self):
        kw = engine_kwargs_for_url("sqlite:///tmp/x.db")
        assert kw["connect_args"]["check_same_thread"] is False

    def test_postgres_empty(self):
        assert engine_kwargs_for_url("postgresql://x") == {}

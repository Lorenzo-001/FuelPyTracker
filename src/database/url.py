import os
from pathlib import Path

_TRUTHY = ("1", "true", "yes")


def is_local_sqlite() -> bool:
    """True when LOCAL_SQLITE env opts into the zero-cloud SQLite bootstrap."""
    return os.environ.get("LOCAL_SQLITE", "").strip().lower() in _TRUTHY


def resolve_database_url(secrets_url: str | None = None) -> str:
    """
    Resolve SQLAlchemy URL.

    1. LOCAL_SQLITE=True → sqlite file under data/ (creates directory).
    2. Else secrets_url if provided.
    3. Else raises ValueError.
    """
    if is_local_sqlite():
        root = Path(__file__).resolve().parents[2]
        data_dir = root / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        # Absolute path so CWD does not matter under Streamlit/Docker.
        db_path = (data_dir / "local.db").resolve()
        return f"sqlite:///{db_path.as_posix()}"

    if secrets_url:
        return secrets_url

    raise ValueError(
        "Database URL missing. Set LOCAL_SQLITE=True for local SQLite, "
        "or configure database.url in .streamlit/secrets.toml."
    )


def engine_kwargs_for_url(url: str) -> dict:
    """Extra create_engine kwargs (SQLite needs check_same_thread for Streamlit)."""
    if url.startswith("sqlite"):
        return {"connect_args": {"check_same_thread": False}}
    return {}

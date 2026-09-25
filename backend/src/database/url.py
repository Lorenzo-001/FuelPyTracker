import os
from pathlib import Path

_TRUTHY = ("1", "true", "yes")


def is_local_sqlite() -> bool:
    """True when LOCAL_SQLITE env opts into SQLite or when running locally without cloud DB."""
    if os.environ.get("LOCAL_SQLITE", "").strip().lower() in _TRUTHY:
        return True
    db_url = os.environ.get("DATABASE_URL", "").strip().lower()
    if db_url.startswith("sqlite"):
        return True
    # Se non c'è DATABASE_URL impostato, il backend fa fallback automatico su SQLite locale
    if not db_url and not os.environ.get("SUPABASE_URL"):
        return True
    return False



def resolve_database_url(secrets_url: str | None = None) -> str:
    """
    Risolve l'URL per SQLAlchemy con la seguente priorità:
    1. Variabile d'ambiente DATABASE_URL (con normalizzazione postgres:// -> postgresql://)
    2. Flag LOCAL_SQLITE=True (database SQLite sotto data/local.db)
    3. secrets_url fornito esplicitamente (da Streamlit o da file di configurazione)
    4. Solleva ValueError se nessuna sorgente è configurata.
    """
    # 1. Variabile d'ambiente OS (Docker, Render, Cloud Run, .env)
    env_url = os.environ.get("DATABASE_URL", "").strip()
    if env_url:
        if env_url.startswith("postgres://"):
            env_url = env_url.replace("postgres://", "postgresql://", 1)
        return env_url

    # 2. Modalità SQLite locale isolata
    if is_local_sqlite():
        root = Path(__file__).resolve().parents[2]
        data_dir = root / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        db_path = (data_dir / "local.db").resolve()
        return f"sqlite:///{db_path.as_posix()}"

    # 3. Parametro fornito esplicitamente
    if secrets_url:
        return secrets_url

    raise ValueError(
        "Database URL missing. Set DATABASE_URL env var, LOCAL_SQLITE=True, "
        "or configure database.url in .streamlit/secrets.toml."
    )




def engine_kwargs_for_url(url: str) -> dict:
    """Extra create_engine kwargs (SQLite needs check_same_thread for Streamlit)."""
    if url.startswith("sqlite"):
        return {"connect_args": {"check_same_thread": False}}
    return {}

import logging
from pathlib import Path
import toml
# pyrefly: ignore [missing-import]
from sqlalchemy import create_engine, text
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import sessionmaker
# pyrefly: ignore [missing-import]
from sqlalchemy.pool import NullPool
# pyrefly: ignore [missing-import]
from sqlalchemy.exc import OperationalError
from src.database.models import Base, Refueling, Maintenance, AppSettings, Reminder, ReminderHistory
from src.database.url import resolve_database_url, engine_kwargs_for_url, is_local_sqlite

# Supporto opzionale per runtime Streamlit (legacy V1)
try:
    from streamlit.runtime.scriptrunner import get_script_run_ctx
except Exception:
    get_script_run_ctx = None  # type: ignore

try:
    import streamlit as st
except Exception:
    st = None  # type: ignore

logger = logging.getLogger(__name__)

# =============================================================================
# CONFIGURAZIONE & CONNESSIONE DATABASE
# =============================================================================

def _is_streamlit_running() -> bool:
    """Rileva se il codice è in esecuzione all'interno del runtime Streamlit."""
    if get_script_run_ctx is not None:
        try:
            return get_script_run_ctx() is not None
        except Exception:
            return False
    return False


def _secrets_database_url() -> str | None:
    """Estrae l'URL da st.secrets se disponibile, oppure direttamente dal file secrets.toml."""
    if st is not None:
        try:
            url = st.secrets["database"]["url"]
            if url:
                return str(url)
        except Exception:
            pass

    try:
        candidates = [
            Path(__file__).resolve().parents[2] / ".streamlit" / "secrets.toml",
            Path.cwd() / "backend" / ".streamlit" / "secrets.toml",
            Path.cwd() / ".streamlit" / "secrets.toml",
        ]
        for candidate in candidates:
            if candidate.is_file():
                data = toml.load(candidate)
                url = data.get("database", {}).get("url")
                if url:
                    return str(url)
    except Exception:
        pass
    return None



try:
    DATABASE_URL = resolve_database_url(_secrets_database_url())
except ValueError as exc:
    if _is_streamlit_running() and st is not None:
        st.error(
            """
            ❌ **Errore Critico: Configurazione Database Mancante**

            Imposta `DATABASE_URL` nel file `.env` o `LOCAL_SQLITE=True` per un bootstrap locale,
            oppure configura `database.url` in `.streamlit/secrets.toml`.
            """
        )
        st.stop()
    else:
        # In contesto headless/FastAPI senza configurazione, usa fallback SQLite sicuro
        logger.warning("Nessuna configurazione DB trovata: fallback automatico su SQLite locale.")
        root = Path(__file__).resolve().parents[2]
        data_dir = root / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        DATABASE_URL = f"sqlite:///{(data_dir / 'local.db').resolve().as_posix()}"

_engine_kwargs = {
    "pool_pre_ping": True,
    "poolclass": NullPool,
    **engine_kwargs_for_url(DATABASE_URL),
}
engine = create_engine(DATABASE_URL, **_engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# =============================================================================
# FUNZIONI DI UTILITÀ
# =============================================================================

def init_db():
    """
    Inizializza lo schema del database creando le tabelle definite nei modelli.

    Operazioni:
        - Verifica l'esistenza delle tabelle tramite i metadati di SQLAlchemy.
        - Crea le tabelle mancanti (operazione idempotente).

    Raises:
        Mostra un messaggio di errore e blocca l'app se il database non è raggiungibile.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        Base.metadata.create_all(bind=engine)
    except OperationalError as exc:
        if _is_streamlit_running() and st is not None:
            hint = (
                "Verifica i permessi sulla cartella `data/`."
                if is_local_sqlite()
                else (
                    "Le cause più comuni sono: PostgreSQL spento/in pausa, "
                    "stringa in `secrets.toml` errata, o firewall."
                )
            )
            st.error(
                f"""
                🔴 **Database non raggiungibile**

                {hint}

                ⚙️ Controlla la configurazione e ricarica la pagina.
                """
            )
            st.stop()
        else:
            logger.error("Database non raggiungibile durante init_db: %s", exc)
            raise


def get_db():
    """
    Generatore per la Dependency Injection della sessione database.
    Garantisce la chiusura della connessione anche in caso di eccezioni.
    In Streamlit mostra errore UI, altrove solleva l'eccezione.
    """
    db = SessionLocal()
    try:
        yield db
    except OperationalError as exc:
        if _is_streamlit_running() and st is not None:
            st.error(
                """
                🔴 **Connessione al database persa**

                La connessione al database è caduta durante l'operazione.
                Questo può accadere se il server è andato in timeout o è stato riavviato.

                ⚙️ Ricarica la pagina per ristabilire la connessione.
                """
            )
            st.stop()
        else:
            logger.error("Errore di connessione database durante get_db: %s", exc)
            raise
    finally:
        db.close()

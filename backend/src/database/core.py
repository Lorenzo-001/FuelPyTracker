import streamlit as st

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.exc import OperationalError
from src.database.models import Base, Refueling, Maintenance, AppSettings, Reminder, ReminderHistory
from src.database.url import resolve_database_url, engine_kwargs_for_url, is_local_sqlite

# =============================================================================
# CONFIGURAZIONE & CONNESSIONE DATABASE
# =============================================================================

def _secrets_database_url() -> str | None:
    try:
        return st.secrets["database"]["url"]
    except Exception:
        return None


try:
    DATABASE_URL = resolve_database_url(_secrets_database_url())
except ValueError:
    st.error(
        """
        ❌ **Errore Critico: Configurazione Database Mancante**

        Imposta `LOCAL_SQLITE=True` nel file `.env` per un bootstrap locale senza Supabase,
        oppure configura `database.url` in `.streamlit/secrets.toml`.

        Verifica anche che, se usi Docker, il volume dei secrets sia montato correttamente.
        """
    )
    st.stop()

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
    except OperationalError:
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


def get_db():
    """
    Generatore per la Dependency Injection della sessione database.
    Garantisce la chiusura della connessione anche in caso di eccezioni.
    In caso di DB irraggiungibile, mostra un messaggio di errore e blocca l'app.
    """
    db = SessionLocal()
    try:
        yield db
    except OperationalError:
        st.error(
            """
            🔴 **Connessione al database persa**

            La connessione al database è caduta durante l'operazione.
            Questo può accadere se il server è andato in timeout o è stato riavviato.

            ⚙️ Ricarica la pagina per ristabilire la connessione.
            """
        )
        st.stop()
    finally:
        db.close()

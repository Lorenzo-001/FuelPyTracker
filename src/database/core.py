import streamlit as st

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy.exc import OperationalError
from src.database.models import Base, Refueling, Maintenance, AppSettings, Reminder, ReminderHistory

# =============================================================================
# CONFIGURAZIONE & CONNESSIONE DATABASE
# =============================================================================

# URL di connessione dai secrets di Streamlit — credenziali separate dal codice.
try:
    DATABASE_URL = st.secrets["database"]["url"]
except Exception:
    # Gestione fallback per evitare crash immediati in fase di sviluppo/debug locale
    st.error(
        """
        ❌ **Errore Critico: Configurazione Database Mancante**
        
        Impossibile recuperare `database.url`. Verifica che:
        1. Il file `.streamlit/secrets.toml` esista nella root del progetto.
        2. Contenga la sezione `[database]` con la proprietà `url`.
        3. Se stai usando Docker, assicurati di aver montato correttamente il file.
        """
    )
    st.stop()

# Engine SQLAlchemy — pool_pre_ping per rilevare connessioni stantie.
engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True,
    poolclass=NullPool
)

# Configurazione transazioni esplicite (no autocommit, no autoflush prematuro)
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
        # Verifica prima che la connessione sia effettivamente viva
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        Base.metadata.create_all(bind=engine)
    except OperationalError as e:
        st.error(
            """
            🔴 **Database non raggiungibile**

            Impossibile connettersi al database. Le cause più comuni sono:
            - Il server PostgreSQL è spento o in pausa (es. piano gratuito di Neon/Supabase).
            - La stringa di connessione in `secrets.toml` non è corretta.
            - Un firewall o un problema di rete blocca la connessione.

            ⚙️ Verifica lo stato del tuo database e ricarica la pagina.
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
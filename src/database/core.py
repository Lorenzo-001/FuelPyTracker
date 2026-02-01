import streamlit as st

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from src.database.models import Base

# =============================================================================
# CONFIGURAZIONE & CONNESSIONE DATABASE
# =============================================================================

# 1. Recupero URL di Connessione
# Tentativo di recupero dai secrets di Streamlit.
# Questo approccio garantisce sicurezza separando le credenziali dal codice.
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

# 2. Inizializzazione Engine SQLAlchemy
# Configurazione specifica per PostgreSQL.
engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True,
    poolclass=NullPool
)

# 3. Session Factory
# Configurazione della fabbrica di sessioni:
# - autocommit=False: Per gestire esplicitamente le transazioni.
# - autoflush=False: Per evitare scritture parziali prima del commit esplicito.
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
    """
    Base.metadata.create_all(bind=engine)


def get_db():
    """
    Generatore per la Dependency Injection della sessione database.
    
    Gestisce il ciclo di vita della connessione (apertura e chiusura sicura)
    utilizzando il pattern 'yield' per l'uso nei contesti 'with' o nelle dipendenze.
    
    Yields:
        Session: Un'istanza attiva di SessionLocal.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        # Garantisce la chiusura della connessione anche in caso di eccezioni
        db.close()
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Base

# 1. Recupero URL Database
# Proviamo a prenderlo dai secrets di Streamlit (funziona sia in locale che in cloud)
try:
    DATABASE_URL = st.secrets["database"]["url"]
except Exception:
    # Fallback per evitare crash se non configurato (opzionale, utile per debug)
    st.error("❌ Errore: 'database.url' non trovato nei secrets (.streamlit/secrets.toml).")
    st.stop()

# 2. Configurazione Engine
# Nota: PostgreSQL NON supporta 'check_same_thread', quindi lo togliamo.
# Se usi Supabase Transaction Pooler (porta 6543), aggiungiamo 'pool_pre_ping' per stabilità.
engine = create_engine(
    DATABASE_URL
)

# 3. Session Factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Crea le tabelle nel database remoto se non esistono."""
    # SQLAlchemy controlla automaticamente se le tabelle esistono prima di crearle
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables checked/created on Cloud!")

def get_db():
    """
    Dependency injection per gestire la sessione del database.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
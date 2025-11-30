import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Base

# 1. Setup dei percorsi (Paths)
# Risaliamo la directory: src/database/core.py -> src/database -> src -> root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DB_DIR, "tracker.db")

# Creiamo la cartella 'data' se non esiste
os.makedirs(DB_DIR, exist_ok=True)

# 2. Configurazione URL Database (SQLite)
DATABASE_URL = f"sqlite:///{DB_PATH}"

# 3. Creazione Engine
# check_same_thread=False è necessario per SQLite quando usato con Streamlit
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

# 4. Session Factory
# Questa classe serve a creare nuove connessioni al DB quando servono
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """
    Crea le tabelle nel database basandosi sui modelli definiti in models.py.
    """
    print(f"🔄 Initializing database at: {DB_PATH}")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")

def get_db():
    """
    Dependency injection per gestire la sessione del database.
    Apre la sessione e garantisce che venga chiusa anche in caso di errori.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
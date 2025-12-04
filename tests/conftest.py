import sys
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 1. Setup Path: Aggiunge la cartella 'src' al path di Python
# Permette ai test di importare i moduli come 'database' invece di 'src.database'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from database.models import Base

# DB in memoria per isolamento totale e velocità
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def db_session():
    """
    Fixture che fornisce una sessione DB pulita per ogni singolo test.
    Ciclo di vita: Setup -> Test -> Teardown (Rollback/Drop).
    """
    # 1. Creazione Engine e Tabelle
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    
    # 2. Creazione Sessione
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    yield db  # Esecuzione del test qui
    
    # 3. Pulizia risorse
    db.close()
    Base.metadata.drop_all(bind=engine)
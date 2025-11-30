import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Base

# Usiamo un DB in memoria per velocità e isolamento
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def db_session():
    """
    Crea un database SQLite in memoria pulito per ogni test.
    Restituisce una sessione SQLAlchemy pronta all'uso.
    """
    # 1. Setup Engine
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    
    # 2. Setup Tabelle
    Base.metadata.create_all(bind=engine)
    
    # 3. Setup Sessione
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    yield db  # Qui il test viene eseguito
    
    # 4. Teardown (Pulizia post-test)
    db.close()
    Base.metadata.drop_all(bind=engine)
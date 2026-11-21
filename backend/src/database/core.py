import logging
from pathlib import Path
# pyrefly: ignore [missing-import]
from sqlalchemy import create_engine, text, inspect
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import sessionmaker
# pyrefly: ignore [missing-import]
from sqlalchemy.pool import NullPool
# pyrefly: ignore [missing-import]
from sqlalchemy.exc import OperationalError
from src.database.models import Base
from src.database.url import resolve_database_url, engine_kwargs_for_url

logger = logging.getLogger(__name__)

# =============================================================================
# CONFIGURAZIONE & CONNESSIONE DATABASE
# =============================================================================

try:
    DATABASE_URL = resolve_database_url()
except ValueError:
    # In contesto headless/FastAPI senza configurazione esplicita, usa fallback SQLite locale
    logger.warning("Nessuna configurazione DB esplicita trovata: fallback automatico su SQLite locale.")
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
        - Verifica e applica migrazioni automatiche per colonne mancanti.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        Base.metadata.create_all(bind=engine)

        # Migrazione automatica colonne veicolo se mancanti (per SQLite locale e ambienti non migrati)
        try:
            inspector = inspect(engine)
            if "settings" in inspector.get_table_names():
                cols = {c["name"] for c in inspector.get_columns("settings")}
                with engine.begin() as conn:
                    if "vehicle_name" not in cols:
                        logger.info("Aggiunta colonna settings.vehicle_name...")
                        conn.execute(text("ALTER TABLE settings ADD COLUMN vehicle_name VARCHAR(100) DEFAULT 'Il mio Veicolo'"))
                    if "vehicle_plate" not in cols:
                        logger.info("Aggiunta colonna settings.vehicle_plate...")
                        conn.execute(text("ALTER TABLE settings ADD COLUMN vehicle_plate VARCHAR(20) DEFAULT ''"))
                    if "vehicle_fuel_type" not in cols:
                        logger.info("Aggiunta colonna settings.vehicle_fuel_type...")
                        conn.execute(text("ALTER TABLE settings ADD COLUMN vehicle_fuel_type VARCHAR(50) DEFAULT 'Benzina'"))
        except Exception as mig_err:
            logger.warning("Verifica/migrazione colonne settings non riuscita (non bloccante): %s", mig_err)
    except OperationalError as exc:
        logger.error("Database non raggiungibile durante init_db: %s", exc)
        raise


def get_db():
    """
    Generatore per la Dependency Injection della sessione database FastAPI.
    Garantisce la chiusura della connessione anche in caso di eccezioni.
    """
    db = SessionLocal()
    try:
        yield db
    except OperationalError as exc:
        logger.error("Errore di connessione database durante get_db: %s", exc)
        raise
    finally:
        db.close()

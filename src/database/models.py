from sqlalchemy import Column, Integer, String, Float, Boolean, Date, Text
from sqlalchemy.orm import declarative_base

# Base class per i modelli SQLAlchemy
Base = declarative_base()

# Entità Rifornimento: mappa la tabella 'refuelings'.
class Refueling(Base):
    __tablename__ = 'refuelings'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False) 
    date = Column(Date, nullable=False)
    total_km = Column(Integer, nullable=False)
    price_per_liter = Column(Float, nullable=False)
    total_cost = Column(Float, nullable=False)
    liters = Column(Float, nullable=False)
    is_full_tank = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)

    def __repr__(self):
        return f"<Refueling(id={self.id}, user={self.user_id}, date={self.date})>"

# Entità Manutenzione: mappa la tabella 'maintenances'.
class Maintenance(Base):
    __tablename__ = 'maintenances'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    date = Column(Date, nullable=False)
    total_km = Column(Integer, nullable=False)
    expense_type = Column(String, nullable=False)
    cost = Column(Float, nullable=False)
    description = Column(Text, nullable=True)

    def __repr__(self):
        return f"<Maintenance(id={self.id}, user={self.user_id}, type={self.expense_type})>"
    
# Entità Configurazione Applicazione.
# Ora non è più un Singleton globale, ma "Una riga per ogni utente".
class AppSettings(Base):
    __tablename__ = 'settings'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False, unique=True)
    price_fluctuation_cents = Column(Float, default=0.15)
    max_total_cost = Column(Float, default=120.0)
    max_accumulated_partial_cost = Column(Float, default=80.0)

    def __repr__(self):
        return f"<AppSettings(user={self.user_id})>"
from sqlalchemy import Column, Integer, String, Float, Boolean, Date, Text
from sqlalchemy.orm import declarative_base

# Base class per i modelli SQLAlchemy
Base = declarative_base()

class Refueling(Base):
    """
    Modello per la tabella dei rifornimenti (Fuel records).
    """
    __tablename__ = 'refuelings'

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    total_km = Column(Integer, nullable=False)        # Chilometraggio totale (Odometer)
    price_per_liter = Column(Float, nullable=False)   # Prezzo al litro
    total_cost = Column(Float, nullable=False)        # Costo totale del pieno
    liters = Column(Float, nullable=False)            # Litri immessi
    is_full_tank = Column(Boolean, default=True)      # True se è stato fatto il pieno (fondamentale per i calcoli)
    notes = Column(Text, nullable=True)

    def __repr__(self):
        return f"<Refueling(date={self.date}, km={self.total_km}, cost={self.total_cost})>"


class Maintenance(Base):
    """
    Modello per la tabella delle manutenzioni e spese extra (Service records).
    """
    __tablename__ = 'maintenances'

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    total_km = Column(Integer, nullable=False)
    expense_type = Column(String, nullable=False)     # Es: "Service", "Tires", "Tax"
    cost = Column(Float, nullable=False)
    description = Column(Text, nullable=True)         # Dettagli dell'intervento

    def __repr__(self):
        return f"<Maintenance(date={self.date}, type={self.expense_type}, cost={self.cost})>"
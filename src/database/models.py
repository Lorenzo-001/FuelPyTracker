from sqlalchemy import Column, Integer, String, Float, Boolean, Date, Text, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, relationship

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
    expiry_km = Column(Integer, nullable=True)
    expiry_date = Column(Date, nullable=True)

    def __repr__(self):
        return f"<Maintenance(id={self.id}, user={self.user_id}, type={self.expense_type})>"
    
# Entità Azioni ripetitive da ricordare.
class Reminder(Base):
    __tablename__ = 'reminders'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    title = Column(String, nullable=False)
    frequency_km = Column(Integer, nullable=True)
    frequency_days = Column(Integer, nullable=True)
    last_km_check = Column(Integer, nullable=True)
    last_date_check = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)

    history = relationship("ReminderHistory", back_populates="reminder", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Reminder(user={self.user_id}, title={self.title})>"
    
# Entità Log Esecuzioni Promemoria
class ReminderHistory(Base):
    __tablename__ = 'reminder_history'

    id = Column(Integer, primary_key=True, index=True)
    reminder_id = Column(Integer, ForeignKey('reminders.id'), nullable=False)
    user_id = Column(String, index=True, nullable=False)
    date_checked = Column(Date, nullable=False)
    km_checked = Column(Integer, nullable=False)
    notes = Column(Text, nullable=True)

    reminder = relationship("Reminder", back_populates="history")

    def __repr__(self):
        return f"<ReminderLog(id={self.id}, rem={self.reminder_id})>"
    
# Entità Configurazione Applicazione.
# Ora non è più un Singleton globale, ma "Una riga per ogni utente".
class AppSettings(Base):
    __tablename__ = 'settings'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False, unique=True)
    price_fluctuation_cents = Column(Float, default=0.15)
    max_total_cost = Column(Float, default=120.0)
    max_accumulated_partial_cost = Column(Float, default=80.0)
    reminder_types = Column(JSON, nullable=True)

    def __repr__(self):
        return f"<AppSettings(user={self.user_id})>"
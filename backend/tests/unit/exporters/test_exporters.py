import io
from datetime import date
import pandas as pd
import pytest
# pyrefly: ignore [missing-import]
from pypdf import PdfReader

from src.database import crud
from src.services.data.exporters.reports import generate_excel_report
from src.services.data.exporters.pdf_generator import generate_maintenance_report

USER_ID = "test-export-user"

def test_generate_excel_report_with_data(db_session):
    """Testa la corretta generazione del file Excel con dati presenti."""
    # 1. Popolamento dati mock
    crud.create_refueling(
        db=db_session, user_id=USER_ID,
        date_obj=date(2025, 1, 15), total_km=10000,
        price_per_liter=1.80, total_cost=90.0,
        liters=50.0, is_full_tank=True, notes="Pieno test"
    )
    crud.create_maintenance(
        db=db_session, user_id=USER_ID,
        date_obj=date(2025, 2, 1), total_km=11000,
        expense_type="Tagliando", cost=250.0,
        description="Filtri e olio"
    )
    
    # 2. Esecuzione export
    excel_bytes = generate_excel_report(db_session, USER_ID)
    
    # 3. Asserzioni
    assert len(excel_bytes) > 0
    
    # Usiamo pandas per rileggere il file binario generato
    df_dict = pd.read_excel(io.BytesIO(excel_bytes), sheet_name=None)
    
    # Verifichiamo che i due fogli esistano
    assert "Rifornimenti" in df_dict
    assert "Manutenzione" in df_dict
    
    df_fuel = df_dict["Rifornimenti"]
    df_maint = df_dict["Manutenzione"]
    
    # Verifichiamo il contenuto (Rifornimenti)
    assert len(df_fuel) == 1
    assert df_fuel.iloc[0]["Costo"] == 90.0
    assert df_fuel.iloc[0]["Pieno"] == "Sì"
    assert df_fuel.iloc[0]["Note"] == "Pieno test"
    
    # Verifichiamo il contenuto (Manutenzione)
    assert len(df_maint) == 1
    assert df_maint.iloc[0]["Costo"] == 250.0
    assert df_maint.iloc[0]["Tipo"] == "Tagliando"

def test_generate_excel_report_empty(db_session):
    """Testa la generazione excel quando non ci sono dati."""
    # Nessun dato inserito per OTHER_USER
    excel_bytes = generate_excel_report(db_session, "empty_user")
    assert len(excel_bytes) > 0
    
    df_dict = pd.read_excel(io.BytesIO(excel_bytes), sheet_name=None)
    assert len(df_dict["Rifornimenti"]) == 0
    assert len(df_dict["Manutenzione"]) == 0
    # Le colonne dovrebbero comunque esserci ma senza righe
    assert "Data" in df_dict["Rifornimenti"].columns

def test_generate_maintenance_report_pdf(db_session):
    """Testa la generazione del libretto PDF verificandone l'output text."""
    crud.create_maintenance(
        db=db_session, user_id=USER_ID,
        date_obj=date(2025, 5, 20), total_km=25000,
        expense_type="Gomme", cost=500.0,
        description="Cambio treno gomme invernali"
    )
    
    # Creazione del PDF
    pdf_bytes = generate_maintenance_report(
        db=db_session,
        user_id=USER_ID,
        owner_name="Mario Rossi",
        plate="AB123CD",
        car_model="Fiat Panda"
    )
    
    assert len(pdf_bytes) > 0
    # Verifica intestazione raw PDF (firma magica)
    assert pdf_bytes.startswith(b"%PDF-")
    
    # Lettura del PDF con pypdf
    reader = PdfReader(io.BytesIO(pdf_bytes))
    assert len(reader.pages) > 0
    
    text = reader.pages[0].extract_text()
    
    # Verifichiamo che il testo estratto contenga le parole chiave attese
    assert "STORICO MANUTENZIONE" in text
    assert "Mario Rossi" in text
    assert "AB123CD" in text
    assert "Fiat Panda" in text
    assert "Gomme" in text
    assert "Cambio treno gomme invernali" in text
    
def test_generate_maintenance_report_pdf_with_year(db_session):
    """Verifica il filtro sull'anno per il report PDF."""
    crud.create_maintenance(
        db=db_session, user_id=USER_ID,
        date_obj=date(2023, 1, 1), total_km=10000,
        expense_type="Tagliando 2023", cost=100.0
    )
    crud.create_maintenance(
        db=db_session, user_id=USER_ID,
        date_obj=date(2024, 1, 1), total_km=20000,
        expense_type="Tagliando 2024", cost=150.0
    )
    
    pdf_bytes = generate_maintenance_report(
        db=db_session,
        user_id=USER_ID,
        owner_name="Luigi Verdi",
        plate="XY987ZZ",
        car_model="Alfa Romeo",
        year=2024
    )
    
    reader = PdfReader(io.BytesIO(pdf_bytes))
    text = reader.pages[0].extract_text()
    
    # Dovrebbe esserci solo il tagliando 2024
    assert "REGISTRO MANUTENZIONE 2024" in text
    assert "Tagliando 2024" in text
    assert "Tagliando 2023" not in text

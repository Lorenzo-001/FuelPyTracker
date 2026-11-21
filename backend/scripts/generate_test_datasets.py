"""
Generatore di dataset Excel di prova per il collaudo UAT di FuelPyTracker V2.
Crea due file nella cartella _cantiere/test_datasets/:
1. 01_dataset_baseline_valido.xlsx (Rifornimenti e Manutenzioni coerenti per popolamento iniziale)
2. 02_dataset_stress_e_anomalie.xlsx (Casi limite, refusi, km invertiti, date future e modifiche)
"""
from pathlib import Path
import sys
import pandas as pd

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

def generate_datasets():
    output_dir = Path(__file__).resolve().parents[2] / "_cantiere" / "test_datasets"
    output_dir.mkdir(parents=True, exist_ok=True)

    # =========================================================================
    # DATASET 1: BASELINE VALIDO
    # =========================================================================
    file_1 = output_dir / "01_dataset_baseline_valido.xlsx"
    print(f"📦 Generazione Dataset 1: {file_1.name}...")

    fuel_baseline = [
        {"Data": "2024-01-10", "Km": 114500, "Prezzo": 1.829, "Costo": 85.00, "Litri": 46.47, "Pieno": "Sì", "Note": "Pieno iniziale di riferimento"},
        {"Data": "2024-01-25", "Km": 114950, "Prezzo": 1.819, "Costo": 30.00, "Litri": 16.49, "Pieno": "No", "Note": "Rabbocco parziale per viaggio"},
        {"Data": "2024-02-12", "Km": 115650, "Prezzo": 1.839, "Costo": 82.50, "Litri": 44.86, "Pieno": "Sì", "Note": "Pieno completo chiusura tratta"},
        {"Data": "2024-03-05", "Km": 116400, "Prezzo": 1.809, "Costo": 78.00, "Litri": 43.12, "Pieno": "Sì", "Note": "Distributore tangenziale"},
        {"Data": "2024-03-28", "Km": 117250, "Prezzo": 1.849, "Costo": 88.00, "Litri": 47.59, "Pieno": "Sì", "Note": "Pieno autostradale"},
        {"Data": "2024-04-18", "Km": 118100, "Prezzo": 1.869, "Costo": 90.00, "Litri": 48.15, "Pieno": "Sì", "Note": "Pieno completo di routine"},
    ]

    maint_baseline = [
        {"Data": "2024-01-15", "Km": 114600, "Tipo": "Tagliando", "Costo": 320.00, "Note": "Tagliando completo (olio, filtri, livelli)", "Scadenza_Km": 130000, "Scadenza_Data": "2025-01-15"},
        {"Data": "2024-02-20", "Km": 115800, "Tipo": "Freni", "Costo": 180.00, "Note": "Sostituzione pastiglie anteriori Brembo", "Scadenza_Km": 145000, "Scadenza_Data": ""},
        {"Data": "2024-03-10", "Km": 116600, "Tipo": "Gomme", "Costo": 450.00, "Note": "4x pneumatici Michelin Primacy 4 + convergenza", "Scadenza_Km": 160000, "Scadenza_Data": "2026-03-10"},
    ]

    with pd.ExcelWriter(file_1, engine="openpyxl") as writer:
        pd.DataFrame(fuel_baseline).to_excel(writer, sheet_name="Rifornimenti", index=False)
        pd.DataFrame(maint_baseline).to_excel(writer, sheet_name="Manutenzioni", index=False)
    print(f"   ✓ Creato con successo: 6 rifornimenti, 3 manutenzioni.\n")

    # =========================================================================
    # DATASET 2: STRESS TEST & ANOMALIE
    # =========================================================================
    file_2 = output_dir / "02_dataset_stress_e_anomalie.xlsx"
    print(f"🧪 Generazione Dataset 2: {file_2.name}...")

    fuel_stress = [
        # Caso 1: Record valido nuovo (Verde)
        {"Data": "2024-05-02", "Km": 118900, "Prezzo": 1.859, "Costo": 80.00, "Litri": 43.03, "Pieno": "Sì", "Note": "Record nuovo valido"},
        # Caso 2: Refuso di battitura estremo (500€ invece di 50€ -> Rosso per Litri > 120L e Spesa > 2.5x)
        {"Data": "2024-05-15", "Km": 119600, "Prezzo": 1.859, "Costo": 500.00, "Litri": 268.96, "Pieno": "Sì", "Note": "Refuso spesa da correggere a 50 euro"},
        # Caso 3: Chilometraggio invertito rispetto al precedente (119400 < 119600 -> Rosso Sandwich check)
        {"Data": "2024-05-28", "Km": 119400, "Prezzo": 1.849, "Costo": 75.00, "Litri": 40.56, "Pieno": "Sì", "Note": "Km invertiti da correggere a 120400"},
        # Caso 4: Data nel futuro (Rosso Data futura)
        {"Data": "2027-01-01", "Km": 121000, "Prezzo": 1.839, "Costo": 70.00, "Litri": 38.06, "Pieno": "Sì", "Note": "Data nel futuro da correggere ad oggi"},
        # Caso 5: Record già esistente con prezzo modificato (Blu Modifica)
        {"Data": "2024-01-10", "Km": 114500, "Prezzo": 1.950, "Costo": 85.00, "Litri": 43.59, "Pieno": "Sì", "Note": "Variazione prezzo sul record iniziale"},
        # Caso 6: Record identico a quello a DB (Grigio Invariato)
        {"Data": "2024-03-05", "Km": 116400, "Prezzo": 1.809, "Costo": 78.00, "Litri": 43.12, "Pieno": "Sì", "Note": "Distributore tangenziale"},
    ]

    maint_stress = [
        # Caso 1: Nuovo valido (Verde)
        {"Data": "2024-05-10", "Km": 119500, "Tipo": "Batteria", "Costo": 140.00, "Note": "Sostituzione batteria Bosch 12V 70Ah", "Scadenza_Km": 170000, "Scadenza_Data": "2028-05-10"},
        # Caso 2: Modifica costo su record esistente (Blu)
        {"Data": "2024-02-20", "Km": 115800, "Tipo": "Freni", "Costo": 195.00, "Note": "Rettifica costo con manodopera aggiunta", "Scadenza_Km": 145000, "Scadenza_Data": ""},
        # Caso 3: Record identico (Grigio)
        {"Data": "2024-01-15", "Km": 114600, "Tipo": "Tagliando", "Costo": 320.00, "Note": "Tagliando completo (olio, filtri, livelli)", "Scadenza_Km": 130000, "Scadenza_Data": "2025-01-15"},
        # Caso 4: Errore Km Zero (Rosso)
        {"Data": "2024-05-12", "Km": 0, "Tipo": "Revisione", "Costo": 79.00, "Note": "Revisione ministeriale con km mancanti", "Scadenza_Km": "", "Scadenza_Data": "2026-05-12"},
    ]

    with pd.ExcelWriter(file_2, engine="openpyxl") as writer:
        pd.DataFrame(fuel_stress).to_excel(writer, sheet_name="Rifornimenti", index=False)
        pd.DataFrame(maint_stress).to_excel(writer, sheet_name="Manutenzioni", index=False)
    print(f"   ✓ Creato con successo: scenari verde, blu, grigio e rosso.\n")

if __name__ == "__main__":
    generate_datasets()

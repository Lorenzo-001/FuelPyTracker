import pandas as pd
from sqlalchemy.orm import Session

from . import fuel, maintenance

# =============================================================================
# FILE UPLOAD ORCHESTRATOR
# =============================================================================

def parse_upload_file(db: Session, user_id: str, uploaded_file) -> dict:
    """
    Gestisce il parsing di file caricati dall'utente (CSV o Excel).
    Rileva automaticamente il formato e smista ai moduli competenti (fuel/maintenance).
    
    Args:
        uploaded_file: Oggetto file-like fornito da Streamlit uploader.
        
    Returns:
        dict: Dizionario contenente i DataFrame processati o messaggi di errore globali.
    """
    results = {}
    
    # 1. Handling CSV (Legacy Support)
    if uploaded_file.name.endswith('.csv'):
        try:
            df = pd.read_csv(uploaded_file)
            results['fuel'] = fuel.process_fuel_data(db, user_id, df)
        except Exception as e:
            results['global_error'] = f"Errore CSV: {e}"
        return results

    # 2. Handling Excel (Multi-sheet)
    try:
        xls = pd.ExcelFile(uploaded_file)
        
        # Mappa nomi fogli in minuscolo per ricerca case-insensitive
        sheet_map = {s.lower().strip(): s for s in xls.sheet_names}
        
        # Euristica di rilevamento fogli (Sheet Sniffing)
        fuel_sheet = next((s for k, s in sheet_map.items() if 'riforniment' in k or 'fuel' in k), None)
        maint_sheet = next((s for k, s in sheet_map.items() if 'manutenzion' in k or 'maint' in k), None)
        
        # Fallback: Se c'è un solo foglio e non ho riconosciuto nomi, assumo siano Rifornimenti
        if not fuel_sheet and not maint_sheet and len(xls.sheet_names) == 1:
            fuel_sheet = xls.sheet_names[0]

        # 3. Processing
        if fuel_sheet:
            df = pd.read_excel(uploaded_file, sheet_name=fuel_sheet)
            results['fuel'] = fuel.process_fuel_data(db, user_id, df)
            
        if maint_sheet:
            df = pd.read_excel(uploaded_file, sheet_name=maint_sheet)
            results['maintenance'] = maintenance.process_maintenance_data(db, user_id, df)

        if not results:
            results['global_error'] = "Nessun foglio valido trovato (cerca 'Rifornimenti' o 'Manutenzione')."

    except Exception as e:
        results['global_error'] = f"Errore file: {e}"

    return results
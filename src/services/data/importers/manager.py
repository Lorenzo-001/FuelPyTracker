import pandas as pd
from sqlalchemy.orm import Session
from . import fuel, maintenance

def parse_upload_file(db: Session, user_id: str, uploaded_file) -> dict:
    results = {}
    
    # 1. Handling CSV (Legacy)
    if uploaded_file.name.endswith('.csv'):
        try:
            df = pd.read_csv(uploaded_file)
            results['fuel'] = fuel.process_fuel_data(db, user_id, df)
        except Exception as e:
            results['global_error'] = f"Errore CSV: {e}"
        return results

    # 2. Handling Excel
    try:
        xls = pd.ExcelFile(uploaded_file)
        sheet_map = {s.lower().strip(): s for s in xls.sheet_names}
        
        # Sniffing
        fuel_sheet = next((s for k, s in sheet_map.items() if 'riforniment' in k or 'fuel' in k), None)
        maint_sheet = next((s for k, s in sheet_map.items() if 'manutenzion' in k or 'maint' in k), None)
        
        # Fallback single sheet
        if not fuel_sheet and not maint_sheet and len(xls.sheet_names) == 1:
            fuel_sheet = xls.sheet_names[0]

        if fuel_sheet:
            df = pd.read_excel(uploaded_file, sheet_name=fuel_sheet)
            results['fuel'] = fuel.process_fuel_data(db, user_id, df)
            
        if maint_sheet:
            df = pd.read_excel(uploaded_file, sheet_name=maint_sheet)
            results['maintenance'] = maintenance.process_maintenance_data(db, user_id, df) # (Da implementare in maintenance.py simile a fuel)

        if not results:
            results['global_error'] = "Nessun foglio valido trovato."

    except Exception as e:
        results['global_error'] = f"Errore file: {e}"

    return results
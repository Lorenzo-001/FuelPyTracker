import pandas as pd
from sqlalchemy.orm import Session
from src.database import crud
from .utils import clean_column_names, parse_date, parse_float, parse_int

# --- Configurazione ---
REQUIRED_COLS = {'data', 'km', 'tipo', 'costo'}

ALIAS_MAP = {
    'data': 'data', 
    'km': 'km', 'chilometri': 'km', 'kilometri': 'km',
    'tipo': 'tipo', 'type': 'tipo', 'intervento': 'tipo',
    'costo': 'costo', 'spesa': 'costo',
    'descrizione': 'descrizione', 'note': 'descrizione', 'dettagli': 'descrizione'
}

UI_REVERSE_MAP = {
    'data': 'data',
    'km': 'km',
    'tipo': 'tipo',
    'costo': 'costo',
    'descrizione': 'descrizione'
}

def process_maintenance_data(db: Session, user_id: str, df: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    if df.empty: return pd.DataFrame(), "Il foglio Manutenzioni è vuoto."
    
    df = clean_column_names(df)
    df = df.rename(columns=ALIAS_MAP)
    df = df.loc[:, ~df.columns.duplicated()]
    
    if 'id' not in df.columns: df['id'] = None

    if not REQUIRED_COLS.issubset(set(df.columns)):
        missing = ", ".join(REQUIRED_COLS - set(df.columns))
        return pd.DataFrame(), f"Colonne mancanti: {missing}"
    
    if 'descrizione' not in df.columns: df['descrizione'] = ""
    else: df['descrizione'] = df['descrizione'].fillna("").astype(str)

    return validate_maintenance_logic(db, user_id, df), None

def validate_maintenance_logic(db: Session, user_id: str, df: pd.DataFrame) -> pd.DataFrame:
    # 1. Normalizzazione e Pulizia
    df = clean_column_names(df)
    if 'note' in df.columns and 'descrizione' in df.columns:
        df = df.drop(columns=['note'])
    df = df.rename(columns=UI_REVERSE_MAP) 
    df = df.loc[:, ~df.columns.duplicated()]

    # 2. Recupero Dati e Ordinamento per Controlli Temporali
    db_recs = crud.get_all_maintenances(db, user_id)
    # Ordinamento fondamentale per il Sandwich Check
    sorted_history = sorted(db_recs, key=lambda x: (x.date, x.total_km))
    
    ref_map = {(m.date, m.total_km, m.expense_type): m for m in db_recs}
    id_map = {m.id: m for m in db_recs}
    
    processed_rows = []
    file_keys = set() 

    for _, row in df.iterrows():
        # Passiamo sorted_history alla funzione di parsing
        res = _parse_single_row(row, ref_map, id_map, file_keys, sorted_history)
        
        if res:
            key = (res['Data'], res['Km'], res['Tipo'])
            if key not in file_keys:
                file_keys.add(key)
                processed_rows.append(res)
            else:
                res['Stato'] = 'Errore'
                res['Note'] = 'Record duplicato nel file'
                processed_rows.append(res)

    res_df = pd.DataFrame(processed_rows)
    if not res_df.empty:
        res_df['Data'] = pd.to_datetime(res_df['Data'])
        res_df = res_df.sort_values(by='Data', ascending=True)
        
    return res_df

def _parse_single_row(row, ref_map, id_map, file_keys, sorted_history):
    status, notes = "Nuovo", []
    db_id = None
    
    # --- Parsing Base ---
    d_date = parse_date(row.get('data'))
    d_km = parse_int(row.get('km'))
    if not d_date and d_km == 0: return None
    if not d_date: status, notes = "Errore", ["Data invalida"]

    d_cost = parse_float(row.get('costo'))
    d_type = str(row.get('tipo', 'Altro')).strip()
    d_desc = str(row.get('descrizione', '')).strip()
    
    raw_id = row.get('db_id')
    raw_id = int(float(raw_id)) if pd.notna(raw_id) else None

    if status != "Errore":
        
        # --- A. Identification Logic (ID vs Key) ---
        found_match = False
        db_rec = None

        # 1. Match per ID (Prioritario)
        if raw_id and raw_id in id_map:
            db_rec = id_map[raw_id]
            db_id = raw_id
            found_match = True
            
            # Diff Check Completo
            diffs = []
            if db_rec.date != d_date: diffs.append(f"Data: {db_rec.date} -> {d_date}")
            if db_rec.total_km != d_km: diffs.append(f"Km: {db_rec.total_km} -> {d_km}")
            if db_rec.expense_type != d_type: diffs.append(f"Tipo: {db_rec.expense_type} -> {d_type}")
            if abs(db_rec.cost - d_cost) > 0.01: diffs.append(f"Costo")
            if (db_rec.description or "").strip() != d_desc: diffs.append("Descrizione")
            
            if diffs:
                status = "Modifica"
                notes = [f"Cambia: {', '.join(diffs)}"]
            else:
                status = "Invariato"

        # 2. Match per Super Key (Fallback)
        elif not found_match:
            super_key = (d_date, d_km, d_type)
            if super_key in ref_map:
                db_rec = ref_map[super_key]
                db_id = db_rec.id
                found_match = True
                
                diffs = []
                if abs(db_rec.cost - d_cost) > 0.01: diffs.append("Costo")
                if (db_rec.description or "").strip() != d_desc: diffs.append("Descrizione")
                
                if diffs:
                    status = "Modifica"
                    notes = [f"Aggiornamenti: {', '.join(diffs)}"]
                else:
                    status = "Invariato"

    # --- B. Controlli di Congruità (SANDWICH CHECK) ---
    # Eseguiamo questo controllo se è Nuovo o Modifica (perché se modifico i KM devo riverificare la coerenza)
    if status in ["Nuovo", "Modifica"]:
        
        # 1. Valori base
        if d_cost < 0: status, notes = "Errore", ["Costo negativo"]
        if d_km <= 0: status, notes = "Errore", ["Km <= 0"]

        # 2. Sandwich Check (Coerenza Temporale)
        # Cerchiamo record precedenti e successivi nella storia ESISTENTE
        prev_rec = None
        next_rec = None
        
        for r in sorted_history:
            # Saltiamo il record stesso se stiamo facendo un update (controllo tramite ID)
            if db_id and r.id == db_id:
                continue

            if r.date < d_date:
                prev_rec = r
            elif r.date > d_date:
                next_rec = r
                break # Trovato il primo successivo, fermiamoci
        
        # Check Km incoerenti col passato
        if prev_rec and d_km < prev_rec.total_km:
            status = "Errore"
            # Formattazione user-friendly dell'errore
            notes.append(f"Km ({d_km}) inferiori al {prev_rec.date.strftime('%d/%m')} - ({prev_rec.total_km})")

        # Check Km incoerenti col futuro
        if next_rec and d_km > next_rec.total_km:
            status = "Errore"
            notes.append(f"Km ({d_km}) superiori al {next_rec.date.strftime('%d/%m')} ({next_rec.total_km})")

    return {
        "db_id": db_id,
        "Stato": status,
        "Note": " | ".join(notes),
        "Data": d_date, "Km": d_km, "Tipo": d_type, 
        "Costo": d_cost, "Descrizione": d_desc
    }

def save_row(db: Session, user_id: str, row):
    if row['Stato'] in ["Errore", "Invariato"]: return

    try:
        # LOGICA UPDATE
        if row['Stato'] == "Modifica" and pd.notna(row['db_id']):
            crud.update_maintenance(db, user_id, int(row['db_id']), {
                "date": row['Data'],
                "total_km": int(row['Km']),
                "expense_type": row['Tipo'],
                "cost": float(row['Costo']),
                "description": row['Descrizione']
            })
            
        # LOGICA INSERT
        elif row['Stato'] in ["Nuovo", "OK"]:
            crud.create_maintenance(
                db, user_id, 
                row['Data'], int(row['Km']), row['Tipo'], 
                float(row['Costo']), row['Descrizione']
            )
    except Exception as e:
        print(f"[Maintenance Import Error] Riga fallita: {e}")
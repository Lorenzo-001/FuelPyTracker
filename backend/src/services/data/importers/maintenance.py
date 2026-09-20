import pandas as pd
from sqlalchemy.orm import Session

from src.database import crud
from .utils import clean_column_names, parse_date, parse_float, parse_int

# =============================================================================
# CONFIGURAZIONE & MAPPING
# =============================================================================

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

# =============================================================================
# LOGICA DI PROCESSING
# =============================================================================

def process_maintenance_data(db: Session, user_id: str, df: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    """Valida la struttura del file manutenzioni e normalizza i nomi colonne."""
    if df.empty: return pd.DataFrame(), "Il foglio Manutenzioni è vuoto."
    
    # 1. Normalizzazione Header
    df = clean_column_names(df)
    df = df.rename(columns=ALIAS_MAP)
    df = df.loc[:, ~df.columns.duplicated()]
    
    # Setup ID colonna se mancante
    if 'id' not in df.columns: df['id'] = None

    # 2. Controllo Colonne Obbligatorie
    if not REQUIRED_COLS.issubset(set(df.columns)):
        missing = ", ".join(REQUIRED_COLS - set(df.columns))
        return pd.DataFrame(), f"Colonne mancanti: {missing}"
    
    # Handling Null description
    if 'descrizione' not in df.columns: df['descrizione'] = ""
    else: df['descrizione'] = df['descrizione'].fillna("").astype(str)

    return validate_maintenance_logic(db, user_id, df), None


def validate_maintenance_logic(db: Session, user_id: str, df: pd.DataFrame) -> pd.DataFrame:
    """Valida logicamente le righe confrontandole con lo storico manutenzioni."""
    # 1. Pulizia e Preparazione
    df = clean_column_names(df)
    # Risolve conflitti nomi colonne (priorità alla descrizione standard)
    if 'note' in df.columns and 'descrizione' in df.columns:
        df = df.drop(columns=['note'])
    df = df.rename(columns=UI_REVERSE_MAP) 
    df = df.loc[:, ~df.columns.duplicated()]

    # 2. Recupero Storico e Mappe Lookup
    db_recs = crud.get_all_maintenances(db, user_id)
    # L'ordinamento è cruciale per i check di coerenza chilometrica
    sorted_history = sorted(db_recs, key=lambda x: (x.date, x.total_km))
    
    ref_map = {(m.date, m.total_km, m.expense_type): m for m in db_recs}
    id_map = {m.id: m for m in db_recs}
    
    processed_rows = []
    file_keys = set() 

    # 3. Iterazione Rows
    for _, row in df.iterrows():
        res = _parse_single_row(row, ref_map, id_map, file_keys, sorted_history)
        
        if res:
            # Controllo Duplicati nel file di input
            key = (res['Data'], res['Km'], res['Tipo'])
            if key not in file_keys:
                file_keys.add(key)
                processed_rows.append(res)
            else:
                res['Stato'] = 'Errore'
                res['Note'] = 'Record duplicato nel file'
                processed_rows.append(res)

    # 4. Formattazione Finale Output
    res_df = pd.DataFrame(processed_rows)
    if not res_df.empty:
        res_df['Data'] = pd.to_datetime(res_df['Data'])
        res_df = res_df.sort_values(by='Data', ascending=True)
        
    return res_df


def _parse_single_row(row, ref_map, id_map, file_keys, sorted_history):
    """
    Core parsing: Identifica se la riga è un nuovo inserimento o un update.
    Implementa controlli di coerenza temporale (Sandwich Check).
    """
    status, notes = "Nuovo", []
    db_id = None
    
    # 1. Parsing Base
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
        
        # 2. Identification Logic (Matching)
        found_match = False
        db_rec = None

        # Strategia A: Match per ID Univoco (Priorità alta)
        if raw_id and raw_id in id_map:
            db_rec = id_map[raw_id]
            db_id = raw_id
            found_match = True
            
            # Diff Check
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

        # Strategia B: Match per Chiave Logica (Data + Km + Tipo)
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

    # 3. Controlli di Congruità (SANDWICH CHECK)
    # Applicabile solo se stiamo inserendo o modificando (potenziale alterazione sequenza km)
    if status in ["Nuovo", "Modifica"]:
        
        # Check Valori Negativi
        if d_cost < 0: status, notes = "Errore", ["Costo negativo"]
        if d_km <= 0: status, notes = "Errore", ["Km <= 0"]

        # Sandwich Logic
        prev_rec = None
        next_rec = None
        
        for r in sorted_history:
            # Esclusione record corrente in caso di update (per evitare self-comparison)
            if db_id and r.id == db_id:
                continue

            if r.date < d_date:
                prev_rec = r
            elif r.date > d_date:
                next_rec = r
                break 
        
        # Validazione coerenza con il passato
        if prev_rec and d_km < prev_rec.total_km:
            status = "Errore"
            notes.append(f"Km ({d_km}) inferiori al {prev_rec.date.strftime('%d/%m')} - ({prev_rec.total_km})")

        # Validazione coerenza con il futuro
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
    """Routing del salvataggio: Update o Insert."""
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
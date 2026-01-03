import pandas as pd
from sqlalchemy.orm import Session

from src.database import crud
from .utils import clean_column_names, parse_date, parse_float, parse_int

# =============================================================================
# COSTANTI DI MAPPING
# =============================================================================

# Alias per normalizzare input eterogenei da Excel grezzi
ALIAS_MAP = {
    'notes': 'note', 'descrizione': 'note',
    'chilometri': 'km', 'kilometri': 'km',
    'costo totale': 'costo', 'prezzo litro': 'prezzo',
    'full': 'pieno'
}

# Alias per ri-mappare i dati processati dalla UI (Data Editor di Streamlit)
# La UI tende a rinominare le colonne o aggiungere suffix (es. note_user)
UI_REVERSE_MAP = {
    'data': 'data',
    'km': 'km',
    'prezzo': 'prezzo',
    'costo': 'costo',
    'litri': 'litri',
    'pieno': 'pieno',
    'note_user': 'note' # Normalizzazione fondamentale per il parser interno
}

# =============================================================================
# LOGICA DI PROCESSING
# =============================================================================

def process_fuel_data(db: Session, user_id: str, df: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    """
    Entry point per l'elaborazione del foglio Rifornimenti.
    Pulisce i nomi delle colonne e delega la validazione business.
    """
    if df.empty: return pd.DataFrame(), "Il foglio è vuoto."
    
    # 1. Pulizia preliminare Header
    df = clean_column_names(df)
    df = df.rename(columns=ALIAS_MAP)

    # Rimozione colonne duplicate per evitare ambiguità
    df = df.loc[:, ~df.columns.duplicated()]
    
    # 2. Impostazione Default
    if 'litri' not in df.columns: df['litri'] = 0.0
    if 'pieno' not in df.columns: df['pieno'] = True
    if 'note' not in df.columns: df['note'] = ""
    
    return validate_fuel_logic(db, user_id, df), None


def validate_fuel_logic(db: Session, user_id: str, df: pd.DataFrame) -> pd.DataFrame:
    """
    Core business logic: confronta i dati in input con il DB esistente.
    Funzione idempotente: gestisce sia upload Excel grezzi che modifiche da UI.
    """
    # 1. Normalizzazione Input
    df = clean_column_names(df)

    # Gestione conflitto: se la UI invia sia 'note' che 'note_user', privilegia 'note_user'
    if 'note' in df.columns and 'note_user' in df.columns:
        df = df.drop(columns=['note'])
    
    # Standardizzazione nomi colonne post-edit UI
    df = df.rename(columns=UI_REVERSE_MAP)

    # 2. Pre-fetching Dati Database (Ottimizzazione N+1)
    settings = crud.get_settings(db, user_id)
    db_refuelings = crud.get_all_refuelings(db, user_id)
    
    # Strutture dati per lookup rapido O(1)
    ref_map = {(r.date, r.total_km): r for r in db_refuelings} 
    date_map = {r.date: r for r in db_refuelings}
    # Ordinamento necessario per controlli sequenziali (Sandwich Check)
    sorted_history = sorted(db_refuelings, key=lambda x: (x.date, x.total_km))
    
    processed_rows = []
    file_keys = set() 

    # 3. Iterazione e Validazione Righe
    for _, row in df.iterrows():
        res = _parse_single_row(row, settings, ref_map, date_map, sorted_history, file_keys)
        
        if res:
            # Controllo Duplicati INTRA-FILE (stesso file, due righe uguali)
            key = (res['Data'], res['Km'])
            if key not in file_keys:
                file_keys.add(key)
                processed_rows.append(res)
            else:
                res['Stato'] = 'Errore'
                res['Note'] = 'Record duplicato nel file'
                processed_rows.append(res)

    # 4. Preparazione Output
    res_df = pd.DataFrame(processed_rows)
    if not res_df.empty:
        res_df['Data'] = pd.to_datetime(res_df['Data'])
        res_df = res_df.sort_values(by='Data')
        
    return res_df


def _parse_single_row(row, settings, ref_map, date_map, sorted_history, file_keys):
    """Analizza una singola riga determinando lo stato (Nuovo, Modifica, Errore)."""
    status, notes, db_id = "Nuovo", [], None
    
    # 1. Parsing Tipo Dati
    d_date = parse_date(row.get('data'))
    d_km = parse_int(row.get('km'))
    
    # Fast-fail su dati mancanti
    if not d_date and d_km == 0: return None 
    if not d_date: status, notes = "Errore", ["Data invalida"]
    
    d_price = parse_float(row.get('prezzo'))
    d_cost = parse_float(row.get('costo'))
    d_liters = parse_float(row.get('litri'))
    
    # Inferenza litri se mancanti
    if d_price > 0 and d_cost > 0: 
        d_liters = d_cost / d_price
    
    d_notes_user = str(row.get('note', '')).strip()
    
    # Normalizzazione booleano 'Pieno'
    raw_pieno = row.get('pieno')
    if isinstance(raw_pieno, str):
        d_full = raw_pieno.lower() not in ['no', 'false', '0', 'n']
    else:
        d_full = bool(raw_pieno)

    # 2. Validazione Logica vs Database
    if status != "Errore":
        super_key = (d_date, d_km)
        
        # A. Riconciliazione (Match Esatto Data+Km)
        if super_key in ref_map:
            db_rec = ref_map[super_key]
            db_id = db_rec.id
            diffs = []
            
            # Change Detection con tolleranza float
            if abs(db_rec.total_cost - d_cost) > 0.01: diffs.append(f"Costo")
            if abs(db_rec.price_per_liter - d_price) > 0.001: diffs.append(f"Prezzo")
            if bool(db_rec.is_full_tank) is not d_full: diffs.append(f"Pieno")
            if (db_rec.notes or "").strip() != d_notes_user: diffs.append("Note")
            
            if diffs: 
                status = "Modifica"
                notes = [f"Cambia: {', '.join(diffs)}"]
            else: 
                status = "Invariato" # Record identico già presente
        else:
            # B. Controllo Nuovi Inserimenti
            if d_date in date_map:
                # Blocca più rifornimenti nello stesso giorno (vincolo di business semplificato)
                status, notes = "Errore", [f"Data già presente (ID: {date_map[d_date].id})"]
            else:
                # Verifica coerenza chilometrica temporale
                status = _sandwich_check(d_date, d_km, sorted_history, notes, status)

    # 3. Check Valori Assoluti
    if status in ["Nuovo", "Modifica"]:
        if d_km <= 0: status, notes = "Errore", ["Km zero o negativi"]
        if d_cost > settings.max_total_cost: status, notes = "Warning", [f"Spesa > {settings.max_total_cost}"]

    # Risoluzione ID finale (priorità al DB ID recuperato, fallback su quello in input)
    existing_id = row.get('db_id')
    final_id = db_id if db_id else (existing_id if pd.notna(existing_id) else None)

    return {
        "db_id": final_id, 
        "Stato": status, 
        "Note": " | ".join(notes),
        "Data": d_date, 
        "Km": d_km, 
        "Prezzo": d_price, 
        "Costo": d_cost,
        "Litri": round(d_liters, 2), 
        "Pieno": d_full, 
        "Note_User": d_notes_user
    }


def _sandwich_check(d_date, d_km, sorted_history, notes, current_status):
    """
    Verifica la coerenza cronologica dei chilometri (Sandwich Logic).
    Il nuovo record deve avere Km > del precedente e Km < del successivo.
    """
    prev_rec = None
    next_rec = None
    
    # Scansione sequenziale (ottimizzabile con bisect per grandi volumi)
    for r in sorted_history:
        if r.date < d_date: prev_rec = r
        elif r.date > d_date: 
            next_rec = r
            break # Trovato il primo record futuro, stop
            
    if prev_rec and d_km <= prev_rec.total_km:
        notes.append(f"Km < del {prev_rec.date} ({prev_rec.total_km})")
        return "Errore"
        
    if next_rec and d_km >= next_rec.total_km:
        notes.append(f"Km > del {next_rec.date} ({next_rec.total_km})")
        return "Errore"
        
    return current_status


def save_row(db: Session, user_id: str, row):
    """Persiste le modifiche sul DB (Create o Update) in base allo stato."""
    if row['Stato'] in ["Errore", "Invariato"]: return
    
    try:
        # Case 1: Update Record Esistente
        if row['Stato'] == "Modifica" and pd.notna(row['db_id']):
            crud.update_refueling(db, user_id, int(row['db_id']), {
                "price_per_liter": float(row['Prezzo']), 
                "total_cost": float(row['Costo']),
                "liters": float(row['Litri']), 
                "is_full_tank": bool(row['Pieno']),
                "notes": row['Note_User']
            })
        # Case 2: Create Nuovo Record
        elif row['Stato'] in ["Nuovo", "OK", "Warning"]:
            crud.create_refueling(
                db, user_id, 
                row['Data'], int(row['Km']), 
                float(row['Prezzo']), float(row['Costo']), 
                float(row['Litri']), bool(row['Pieno']), 
                row['Note_User']
            )
    except Exception as e: 
        print(f"Save error: {e}")
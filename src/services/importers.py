import pandas as pd
from datetime import datetime, date
from sqlalchemy.orm import Session
from database import crud

def parse_upload_file(db: Session, uploaded_file) -> tuple[pd.DataFrame, str]:
    """
    Legge il file raw (CSV/Excel) e lo converte in DataFrame iniziale.
    """
    # 1. Lettura Fisica del File
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        return pd.DataFrame(), f"Errore lettura file: {e}"

    if df.empty:
        return pd.DataFrame(), "Il file caricato è vuoto."

    # 2. Normalizzazione Colonne
    df.columns = [str(c).lower().strip() for c in df.columns]
    required_cols = {'data', 'km', 'prezzo', 'costo'}
    
    if not required_cols.issubset(set(df.columns)):
        missing = required_cols - set(df.columns)
        return pd.DataFrame(), f"Colonne mancanti: {', '.join(missing)}"

    # 3. Aggiunta colonne di servizio se mancano
    if 'litri' not in df.columns: df['litri'] = 0.0
    if 'pieno' not in df.columns: df['pieno'] = True

    # 4. Standardizzazione nomi colonne per l'uso interno
    df = df.rename(columns={
        'data': 'data', 'km': 'km', 'prezzo': 'prezzo', 'costo': 'costo', 
        'litri': 'litri', 'pieno': 'pieno'
    })

    # 5. Prima validazione massiva
    return revalidate_dataframe(db, df), None

def revalidate_dataframe(db: Session, df: pd.DataFrame) -> pd.DataFrame:
    """
    Prende un DataFrame (anche sporco o modificato dall'utente) e ricalcola Stato e Note.
    Ricalcola SEMPRE i Litri per mantenere coerenza matematica (L = C / P).
    Rimuove le righe 'Fantasma' (aggiunte per sbaglio con valori nulli).
    """
    # Recupero contesto dal DB
    last_record = crud.get_last_refueling(db)
    settings = crud.get_settings(db)
    
    # Valori di riferimento
    last_db_km = last_record.total_km if last_record else 0
    last_db_date = last_record.date if last_record else date(2000, 1, 1)
    last_db_price = last_record.price_per_liter if last_record else 0.0
    
    existing_dates = set(r.date for r in crud.get_all_refuelings(db))
    
    processed_rows = []
    file_dates = set()

    for _, row in df.iterrows():
        status = "OK"
        notes = []
        
        # --- A. PARSING & CHECK GHOST ---
        # Cerchiamo la chiave sia minuscola (dal file) che Maiuscola (dal data_editor)
        raw_date = row.get('data') if 'data' in row else row.get('Data')
        
        # Recupero valori numerici grezzi per capire se la riga è vuota
        raw_km = row.get('km') if 'km' in row else row.get('Km')
        
        # FIX GHOST RECORD: Se data è vuota E km è 0/Nan, è una riga creata per sbaglio dalla UI
        is_date_empty = pd.isna(raw_date)
        is_km_empty = pd.isna(raw_km) or raw_km == 0
        
        if is_date_empty and is_km_empty:
            continue # Saltiamo questa riga -> Verrà cancellata dal DataFrame finale

        # --- B. PARSING EFFETTIVO ---
        d_date = None
        d_km = 0
        d_price = 0.0
        d_cost = 0.0
        d_liters = 0.0
        d_full = True

        try:
            # DATA
            if is_date_empty:
                status = "Errore"
                notes.append("Data mancante")
            else:
                if isinstance(raw_date, (datetime, date)):
                    d_date = raw_date.date() if isinstance(raw_date, datetime) else raw_date
                else:
                    # Parsing stringa flessibile
                    found = False
                    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
                        try:
                            d_date = datetime.strptime(str(raw_date), fmt).date()
                            found = True
                            break
                        except: pass
                    if not found:
                        status = "Errore"
                        notes.append("Formato data invalido")
            
            # NUMERI (Helper per parsing sicuro)
            def parse_float(val):
                if pd.isna(val): return 0.0
                try:
                    return float(str(val).replace(',', '.'))
                except: return 0.0

            def parse_int(val):
                if pd.isna(val): return 0
                try: return int(float(str(val).replace(',', '.')))
                except: return 0

            d_km = parse_int(raw_km)
            d_price = parse_float(row.get('prezzo') if 'prezzo' in row else row.get('Prezzo'))
            d_cost = parse_float(row.get('costo') if 'costo' in row else row.get('Costo'))
            d_liters = parse_float(row.get('litri') if 'litri' in row else row.get('Litri'))

            # PIENO
            raw_full = row.get('pieno') if 'pieno' in row else row.get('Pieno')
            if str(raw_full).lower() in ['false', 'no', '0', 'falso', 'n']:
                d_full = False
            else:
                d_full = True

        except Exception as e:
            status = "Errore"
            notes.append(f"Errore tecnico: {str(e)}")

        # --- C. LOGICA RICALCOLO (Coerenza Dati) ---
        if d_price > 0 and d_cost > 0:
            d_liters = d_cost / d_price
        
        # --- D. VALIDAZIONI LOGICHE ---
        if status != "Errore":
            # Date Logic
            if d_date:
                if d_date > date.today():
                    status = "Errore"
                    notes.append("Data futura")
                if d_date in existing_dates:
                    status = "Errore" 
                    notes.append("Data già presente nel DB")
                if d_date in file_dates:
                    status = "Errore"
                    notes.append("Duplicato nel file")
                file_dates.add(d_date)

            # Km Logic
            if d_km <= 0:
                status = "Errore"
                notes.append("Km <= 0")
            elif d_date and d_date > last_db_date and d_km < last_db_km:
                status = "Errore"
                notes.append(f"Km incoerenti (Ultimo DB: {last_db_km})")

            # Prezzi Logic
            if d_price <= 0 or d_cost <= 0:
                status = "Errore"
                notes.append("Prezzo/Costo <= 0")
            else:
                # C1. Check Massimale Spesa
                if d_cost > settings.max_total_cost:
                    status = "Warning"
                    notes.append(f"Spesa > Max Config ({settings.max_total_cost}€)")
                
                # C2. Check Range Prezzo (vs Ultimo Record)
                if last_db_price > 0:
                    min_p = max(0.0, last_db_price - settings.price_fluctuation_cents)
                    max_p = last_db_price + settings.price_fluctuation_cents
                    
                    if not (min_p <= d_price <= max_p):
                        status = "Warning"
                        notes.append(f"Prezzo fuori range ({min_p:.3f}-{max_p:.3f})")

        # --- E. Output Normalizzato ---
        processed_rows.append({
            "Stato": status,
            "Note": " | ".join(notes),
            "Data": d_date,
            "Km": d_km,
            "Prezzo": d_price,
            "Costo": d_cost,
            "Litri": round(d_liters, 2), # Litri ricalcolati e arrotondati
            "Pieno": d_full
        })

    return pd.DataFrame(processed_rows)

def save_single_row(db: Session, row):
    """Salva una riga nel DB. Presuppone che i dati siano già validati."""
    if row['Stato'] == "Errore":
        return

    try:
        crud.create_refueling(
            db, 
            pd.to_datetime(row['Data']).date(), 
            int(row['Km']), 
            float(row['Prezzo']), 
            float(row['Costo']), 
            float(row['Litri']), 
            bool(row['Pieno']),
            f"Import (Note: {row['Note']})" if row['Note'] else "Import Massivo"
        )
    except Exception:
        pass
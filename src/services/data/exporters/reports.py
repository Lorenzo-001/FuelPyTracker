import io

import pandas as pd
from sqlalchemy.orm import Session

from src.database import crud

# =============================================================================
# EXPORT EXCEL LOGIC
# =============================================================================

def generate_excel_report(db: Session, user_id: str) -> bytes:
    """
    Genera un report Excel multi-sheet contenente Rifornimenti e Manutenzioni.
    Include formattazione avanzata (bordi, stili header, larghezza colonne automatica).
    
    Args:
        db (Session): Sessione database attiva.
        user_id (str): ID dell'utente per filtrare i dati.
        
    Returns:
        bytes: Buffer binario del file .xlsx pronto per il download.
    """
    
    # 1. Recupero Dati dal Database
    refuelings = crud.get_all_refuelings(db, user_id)
    maintenances = crud.get_all_maintenances(db, user_id)

    # 2. Mapping Dati: Rifornimenti
    # Trasformazione da oggetti ORM a lista di dizionari per DataFrame
    data_fuel = []
    for r in refuelings:
        data_fuel.append({
            "Data": r.date,
            "Km": r.total_km,
            "Prezzo": r.price_per_liter,
            "Costo": r.total_cost,
            "Litri": r.liters,
            "Pieno": "Sì" if r.is_full_tank else "No",
            "Note": r.notes
        })

    # 3. Mapping Dati: Manutenzioni
    data_maint = []
    for m in maintenances:
        data_maint.append({
            "Data": m.date,
            "Km": m.total_km,
            "Tipo": m.expense_type,
            "Costo": m.cost,
            "Descrizione": m.description
        })

    # 4. Creazione e Ordinamento DataFrame
    df_fuel = pd.DataFrame(data_fuel)
    if not df_fuel.empty:
        df_fuel['Data'] = pd.to_datetime(df_fuel['Data'])
        df_fuel = df_fuel.sort_values(by='Data', ascending=True)

    df_maint = pd.DataFrame(data_maint)
    if not df_maint.empty:
        df_maint['Data'] = pd.to_datetime(df_maint['Data'])
        df_maint = df_maint.sort_values(by='Data', ascending=True)

    # 5. Scrittura Excel con XlsxWriter
    # Utilizziamo un buffer in memoria per evitare salvataggi su disco
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        
        # Dump grezzo dei dati nei rispettivi fogli
        df_fuel.to_excel(writer, sheet_name='Rifornimenti', index=False)
        df_maint.to_excel(writer, sheet_name='Manutenzione', index=False)
        
        workbook = writer.book
        
        # Definizione Stili Custom
        header_fmt = workbook.add_format({
            'bold': True, 'bg_color': '#D9E1F2', 'border': 1, 
            'align': 'center', 'valign': 'vcenter'
        })
        cell_fmt = workbook.add_format({
            'border': 1, 'align': 'center', 'valign': 'vcenter'
        })
        date_fmt = workbook.add_format({
            'num_format': 'dd/mm/yyyy', 'border': 1, 
            'align': 'center', 'valign': 'vcenter'
        })
        
        # Iterazione sui fogli per applicare formattazione
        for sheet_name, df in {'Rifornimenti': df_fuel, 'Manutenzione': df_maint}.items():
            worksheet = writer.sheets[sheet_name]
            
            # A. Sovrascrittura Intestazioni (per applicare stile header)
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_fmt)

            # B. Calcolo e applicazione larghezza colonne (Auto-fit)
            for idx, col in enumerate(df.columns):
                # Larghezza minima 15 char per leggibilità date
                max_len = max(
                    df[col].astype(str).map(len).max() if not df[col].empty else 0,
                    len(str(col))
                ) + 4 
                worksheet.set_column(idx, idx, max(15, max_len)) 

            # C. Applicazione stili alle celle dati
            # XlsxWriter richiede iterazione puntuale per applicare bordi su celle già scritte
            if not df.empty:
                rows = len(df)
                cols = len(df.columns)
                
                for row_idx in range(rows):
                    for col_idx in range(cols):
                        val = df.iloc[row_idx, col_idx]
                        
                        # Selezione formato: Data vs Standard
                        fmt = date_fmt if df.columns[col_idx] == "Data" else cell_fmt
                        
                        # Gestione valori nulli
                        if pd.isna(val): val = ""
                        
                        # Scrittura cella formattata
                        # Nota: +1 sull'indice riga per saltare l'header
                        if df.columns[col_idx] == "Data":
                            worksheet.write_datetime(row_idx + 1, col_idx, val, fmt)
                        else:
                            worksheet.write(row_idx + 1, col_idx, val, fmt)

    return output.getvalue()
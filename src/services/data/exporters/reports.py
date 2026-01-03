import pandas as pd
import io
from sqlalchemy.orm import Session
from src.database import crud

def generate_excel_report(db: Session, user_id: str) -> bytes:
    """
    Genera Excel formattato con bordi, allineamento e larghezza colonne corretta.
    """
    
    # 1. Recupero Dati (Identico a prima)
    refuelings = crud.get_all_refuelings(db, user_id)
    maintenances = crud.get_all_maintenances(db, user_id)

    # 2. Mapping Rifornimenti
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

    # 3. Mapping Manutenzioni
    data_maint = []
    for m in maintenances:
        data_maint.append({
            "Data": m.date,
            "Km": m.total_km,
            "Tipo": m.expense_type,
            "Costo": m.cost,
            "Descrizione": m.description
        })

    # 4. Creazione DF e Sort
    df_fuel = pd.DataFrame(data_fuel)
    if not df_fuel.empty:
        df_fuel['Data'] = pd.to_datetime(df_fuel['Data'])
        df_fuel = df_fuel.sort_values(by='Data', ascending=True)

    df_maint = pd.DataFrame(data_maint)
    if not df_maint.empty:
        df_maint['Data'] = pd.to_datetime(df_maint['Data'])
        df_maint = df_maint.sort_values(by='Data', ascending=True)

    # 5. Scrittura con Formattazione Avanzata
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        
        df_fuel.to_excel(writer, sheet_name='Rifornimenti', index=False)
        df_maint.to_excel(writer, sheet_name='Manutenzione', index=False)
        
        workbook = writer.book
        
        # Stili
        header_fmt = workbook.add_format({
            'bold': True, 'bg_color': '#D9E1F2', 'border': 1, 'align': 'center', 'valign': 'vcenter'
        })
        cell_fmt = workbook.add_format({
            'border': 1, 'align': 'center', 'valign': 'vcenter' # Bordi neri e centrato
        })
        date_fmt = workbook.add_format({
            'num_format': 'dd/mm/yyyy', 'border': 1, 'align': 'center', 'valign': 'vcenter'
        })
        
        for sheet_name, df in {'Rifornimenti': df_fuel, 'Manutenzione': df_maint}.items():
            worksheet = writer.sheets[sheet_name]
            
            # Scrivi Header Formattato
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_fmt)

            # Auto-adjust columns
            for idx, col in enumerate(df.columns):
                # Larghezza minima 15 per evitare ### sulle date
                max_len = max(
                    df[col].astype(str).map(len).max() if not df[col].empty else 0,
                    len(str(col))
                ) + 4 
                worksheet.set_column(idx, idx, max(15, max_len)) 

            # Applica stile celle (Bordi) a tutto il range dati
            if not df.empty:
                rows = len(df)
                cols = len(df.columns)
                # xlsxwriter non supporta styling range diretto facile senza sovrascrivere dati
                # Iteriamo per applicare formati specifici
                for row_idx in range(rows):
                    for col_idx in range(cols):
                        val = df.iloc[row_idx, col_idx]
                        
                        # Formato Data per la prima colonna, Cell standard per le altre
                        fmt = date_fmt if df.columns[col_idx] == "Data" else cell_fmt
                        
                        # Scrittura (gestione NaN)
                        if pd.isna(val): val = ""
                        
                        if df.columns[col_idx] == "Data":
                            worksheet.write_datetime(row_idx + 1, col_idx, val, fmt)
                        else:
                            worksheet.write(row_idx + 1, col_idx, val, fmt)

    return output.getvalue()
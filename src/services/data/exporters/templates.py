import io
import pandas as pd

# =============================================================================
# GENERAZIONE TEMPLATE EXCEL
# =============================================================================

def generate_empty_template() -> bytes:
    """
    Genera un buffer binario contenente un file Excel pre-formattato.
    Crea due fogli di lavoro distinti ('Rifornimenti', 'Manutenzione') 
    con intestazioni stilizzate e larghezza colonne ottimizzata.

    Returns:
        bytes: Il contenuto del file .xlsx pronto per il download/stream.
    """
    output = io.BytesIO()

    # 1. Configurazione Writer e Stili
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        
        # Stile standard per le intestazioni (Grigio-Blu, Grassetto, Bordato)
        header_fmt = workbook.add_format({
            'bold': True, 
            'bg_color': '#D9E1F2', 
            'border': 1, 
            'align': 'center'
        })

        # 2. Configurazione Foglio 'Rifornimenti'
        cols_fuel = ["Data", "Km", "Prezzo", "Costo", "Litri", "Pieno", "Note"]
        
        # Creazione DataFrame vuoto per generare la struttura
        df_fuel = pd.DataFrame(columns=cols_fuel)
        df_fuel.to_excel(writer, sheet_name='Rifornimenti', index=False)
        
        # Applicazione formattazione colonne
        ws_fuel = writer.sheets['Rifornimenti']
        for idx, col in enumerate(cols_fuel):
            ws_fuel.write(0, idx, col, header_fmt)
            ws_fuel.set_column(idx, idx, 15) # Larghezza fissa per leggibilità

        # 3. Configurazione Foglio 'Manutenzione'
        cols_maint = ["Data", "Km", "Tipo", "Costo", "Descrizione"]
        
        df_maint = pd.DataFrame(columns=cols_maint)
        df_maint.to_excel(writer, sheet_name='Manutenzione', index=False)

        # Applicazione formattazione colonne
        ws_maint = writer.sheets['Manutenzione']
        for idx, col in enumerate(cols_maint):
            ws_maint.write(0, idx, col, header_fmt)
            ws_maint.set_column(idx, idx, 20) # Larghezza maggiore per descrizioni

    return output.getvalue()
import pandas as pd
import io

def generate_empty_template() -> bytes:
    """
    Genera un file Excel vuoto con due fogli ('Rifornimenti', 'Manutenzione')
    e le intestazioni corrette per l'importazione.
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        header_fmt = workbook.add_format({
            'bold': True, 'bg_color': '#D9E1F2', 'border': 1, 'align': 'center'
        })

        # --- FOGLIO 1: Rifornimenti ---
        # Colonne attese dall'importer
        cols_fuel = ["Data", "Km", "Prezzo", "Costo", "Litri", "Pieno", "Note"]
        df_fuel = pd.DataFrame(columns=cols_fuel)
        df_fuel.to_excel(writer, sheet_name='Rifornimenti', index=False)
        
        ws_fuel = writer.sheets['Rifornimenti']
        for idx, col in enumerate(cols_fuel):
            ws_fuel.write(0, idx, col, header_fmt)
            ws_fuel.set_column(idx, idx, 15)

        # --- FOGLIO 2: Manutenzione ---
        # Colonne future per l'importer manutenzioni
        cols_maint = ["Data", "Km", "Tipo", "Costo", "Descrizione"]
        df_maint = pd.DataFrame(columns=cols_maint)
        df_maint.to_excel(writer, sheet_name='Manutenzione', index=False)

        ws_maint = writer.sheets['Manutenzione']
        for idx, col in enumerate(cols_maint):
            ws_maint.write(0, idx, col, header_fmt)
            ws_maint.set_column(idx, idx, 20)

    return output.getvalue()
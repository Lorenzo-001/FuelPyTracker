import pandas as pd
from datetime import datetime, date

def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Normalizza i nomi delle colonne: lowercase, strip e converti in stringa."""
    df.columns = [str(c).lower().strip() for c in df.columns]
    return df

def parse_date(raw_date):
    """Tenta di convertire una data da vari formati."""
    if pd.isna(raw_date): return None
    if isinstance(raw_date, (datetime, date)):
        return raw_date.date() if isinstance(raw_date, datetime) else raw_date
    
    raw_str = str(raw_date).split(' ')[0] # Rimuove orari se presenti
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(raw_str, fmt).date()
        except ValueError:
            continue
    return None

def parse_float(value) -> float:
    """Gestisce virgole e NaN."""
    if pd.isna(value): return 0.0
    try:
        return float(str(value).replace(',', '.'))
    except ValueError:
        return 0.0

def parse_int(value) -> int:
    """Gestisce interi da float o stringhe."""
    return int(parse_float(value))
from datetime import datetime, date

import pandas as pd

# =============================================================================
# DATA CLEANING UTILS
# =============================================================================

def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalizza i nomi delle colonne del DataFrame.
    Operazioni: conversione a stringa, lowercase, strip spazi.
    """
    df.columns = [str(c).lower().strip() for c in df.columns]
    return df


def parse_date(raw_date):
    """
    Tenta di convertire un input eterogeneo (str, timestamp, datetime) 
    in un oggetto datetime.date standard.
    """
    if pd.isna(raw_date): return None
    
    # Se è già un oggetto data/datetime
    if isinstance(raw_date, (datetime, date)):
        return raw_date.date() if isinstance(raw_date, datetime) else raw_date
    
    # Parsing stringhe
    raw_str = str(raw_date).split(' ')[0] # Rimuove eventuali componenti orarie
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(raw_str, fmt).date()
        except ValueError:
            continue
            
    return None


def parse_float(value) -> float:
    """Safe parsing per valori float, gestisce virgole decimali e NaN."""
    if pd.isna(value): return 0.0
    try:
        return float(str(value).replace(',', '.'))
    except ValueError:
        return 0.0


def parse_int(value) -> int:
    """Safe parsing per interi (es. chilometri)."""
    return int(parse_float(value))
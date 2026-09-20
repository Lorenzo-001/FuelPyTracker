import pandas as pd
from datetime import datetime, timedelta

def filter_data_by_date(df: pd.DataFrame, range_option: str) -> pd.DataFrame:
    """
    Filtra il DataFrame in base all'intervallo temporale selezionato.
    """
    if df.empty:
        return df
    
    today = datetime.now()
    cutoff_date = None
    
    if range_option == "Ultimo Mese":
        cutoff_date = today - timedelta(days=30)
    elif range_option == "Ultimi 3 Mesi":
        cutoff_date = today - timedelta(days=90)
    elif range_option == "Ultimi 6 Mesi":
        cutoff_date = today - timedelta(days=180)
    elif range_option == "Ultimo Anno":
        cutoff_date = today - timedelta(days=365)
    elif range_option == "Anno Corrente (YTD)":
        cutoff_date = datetime(today.year, 1, 1)
    # "Tutto lo storico" ritorna None
    
    if cutoff_date:
        return df[df["Data"] >= cutoff_date]
    return df
import streamlit as st
import pandas as pd
from database.core import get_db
from database import crud
from services.calculations import calculate_stats

def render():
    """Vista principale: mostra i KPI e i riepiloghi."""
    st.header("📊 Dashboard Riepilogativa")
    
    # 1. Recupero dati DB
    db = next(get_db())
    records = crud.get_all_refuelings(db)
    db.close()

    if not records:
        st.info("Nessun dato disponibile. Inizia aggiungendo un rifornimento!")
        return

    # 2. Calcolo KPI
    metrics = _calculate_global_metrics(records)

    # 3. Visualizzazione
    c1, c2, c3 = st.columns(3)
    c1.metric("Ultimo Prezzo", f"{metrics['last_price']:.3f} €/L")
    c2.metric("Consumo Medio", f"{metrics['avg_kml']:.2f} km/L" if metrics['avg_kml'] else "N/A")
    c3.metric("Spesa Totale", f"{metrics['total_spent']:.2f} €")
    
    st.divider()
    st.caption("Prossimamente: Grafici di andamento temporale.")

def _calculate_global_metrics(records) -> dict:
    """Helper: estrae le statistiche aggregate dalla lista di record."""
    # Calcoliamo efficienza puntuale per ogni record
    kml_values = []
    for r in records:
        stats = calculate_stats(r, records)
        if stats["km_per_liter"]:
            kml_values.append(stats["km_per_liter"])
    
    avg_kml = sum(kml_values) / len(kml_values) if kml_values else 0
    
    return {
        "last_price": records[0].price_per_liter,
        "avg_kml": avg_kml,
        "total_spent": sum(r.total_cost for r in records)
    }
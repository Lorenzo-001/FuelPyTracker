"""Fuel history tab (year-filtered table)."""
import streamlit as st
import pandas as pd
from src.ui.components.fuel import grids


def render_history_tab(records, year):
    if not records:
        st.info(f"Nessun dato nel {year}.")
        return

    df = grids.build_fuel_dataframe(records)
    # Formattazione per visualizzazione
    df['Data'] = pd.to_datetime(df['Data'])
    df_show = df.copy()
    df_show['Data'] = df_show['Data'].dt.strftime('%Y-%m-%d')
    
    st.dataframe(
        df_show.drop(columns=["_obj"]), 
        width="stretch", hide_index=True,
        column_config={
            "ID": None, 
            "Pieno": st.column_config.TextColumn(width="small"),
            "Km/L": st.column_config.TextColumn(width="small"),
            "Descrizione": st.column_config.TextColumn(width="medium")
        }
    )

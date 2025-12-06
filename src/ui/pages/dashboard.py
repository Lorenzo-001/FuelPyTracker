import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from database.core import get_db
from database import crud
from services.calculations import calculate_stats, check_partial_accumulation

def filter_data_by_date(df, range_option):
    """Filtra il dataframe in base all'opzione temporale selezionata."""
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
    # Se "Tutto lo storico", cutoff_date rimane None
    
    if cutoff_date:
        return df[df["Data"] >= cutoff_date]
    return df

def render():
    """Vista principale: Dashboard Interattiva."""
    
    # 1. Recupero Dati
    db = next(get_db())
    records = crud.get_all_refuelings(db)
    settings = crud.get_settings(db)
    db.close()

    if not records:
        st.info("👋 Benvenuto! Inizia aggiungendo il tuo primo rifornimento dalla barra laterale.")
        return

    # Preparazione DataFrame base
    records_asc = sorted(records, key=lambda x: x.date)
    chart_data = []
    for r in records_asc:
        stats = calculate_stats(r, records)
        chart_data.append({
            "Data": pd.to_datetime(r.date),
            "Prezzo": r.price_per_liter,
            "Costo": r.total_cost,
            "Litri": r.liters,
            "KmTotali": r.total_km,
            "Efficienza": stats["km_per_liter"] if stats["km_per_liter"] else None
        })
    df = pd.DataFrame(chart_data)

    # --- SEZIONE 1: HEADER E GUIDA ---
    st.title("📊 Dashboard")
    
    st.markdown("""
    Benvenuto nella tua area di analisi. Qui puoi monitorare l'andamento dei prezzi e l'efficienza della tua auto.
    Usa i filtri nei grafici sottostanti per analizzare periodi specifici.
    """)

    with st.expander("ℹ️ Guida rapida alla Dashboard"):
        st.markdown("""
        - **Ultimo Rifornimento**: Mostra i dettagli dell'operazione più recente.
        - **Trend Prezzo**: Osserva come cambia il costo del carburante nel tempo.
        - **Efficienza**: Monitora i Km/L. Se vedi dei "buchi", significa che hai fatto rifornimenti parziali.
        - **Spesa**: Somma dei costi raggruppati per mese.
        """)

    st.divider()

    # --- SEZIONE 2: CARD "ULTIMO RIFORNIMENTO" (Snapshot) ---
    last_record = df.iloc[-1]
    
    st.subheader("⛽ Ultimo Rifornimento")
    
    # Creiamo un contenitore visivo (Card)
    with st.container(border=True):
        col_last_1, col_last_2, col_last_3, col_last_4 = st.columns(4)
        
        with col_last_1:
            st.metric("📅 Data", last_record["Data"].strftime("%d/%m/%Y"))
        
        with col_last_2:
            st.metric("💶 Spesa", f"{last_record['Costo']:.2f} €")
            
        with col_last_3:
            st.metric("🏷️ Prezzo/L", f"{last_record['Prezzo']:.3f} €")
            
        with col_last_4:
            st.metric("🛢️ Litri", f"{last_record['Litri']:.2f} L")

    # Avviso accumulo parziali
    partial_status = check_partial_accumulation(records)
    if partial_status["accumulated_cost"] > settings.max_accumulated_partial_cost:
        st.warning(f"⚠️ Attenzione: Hai accumulato {partial_status['accumulated_cost']:.2f} € di parziali. Fai un pieno per resettare le statistiche.")

    st.divider()

    # --- SEZIONE 3: GRAFICI CONFIGURABILI (MACRO CARDS) ---
    
    # Opzioni per i filtri temporali
    time_options = ["Ultimo Mese", "Ultimi 3 Mesi", "Ultimi 6 Mesi", "Anno Corrente (YTD)", "Ultimo Anno", "Tutto lo storico"]

    # --- CARD 1: TREND PREZZO ---
    with st.container(border=True):
        st.subheader("📉 Analisi Prezzo Carburante")
        c_settings, c_chart = st.columns([1, 3])
        
        with c_settings:
            st.markdown("**Configurazione**")
            range_price = st.radio("Periodo di analisi:", time_options, index=1, key="filter_price")
            st.caption("Seleziona l'intervallo temporale per zoomare sul grafico.")
        
        with c_chart:
            df_filtered_price = filter_data_by_date(df, range_price)
            if not df_filtered_price.empty:
                avg_p = df_filtered_price["Prezzo"].mean()
                fig_price = go.Figure()
                fig_price.add_trace(go.Scatter(
                    x=df_filtered_price["Data"], y=df_filtered_price["Prezzo"],
                    mode='lines+markers', name='Prezzo', line=dict(color='#EF553B', width=3)
                ))
                fig_price.add_trace(go.Scatter(
                    x=df_filtered_price["Data"], y=[avg_p]*len(df_filtered_price),
                    mode='lines', name='Media Periodo', line=dict(color='gray', dash='dash')
                ))
                fig_price.update_layout(height=300, margin=dict(l=20, r=20, t=10, b=20), yaxis_title="€ / Litro")
                st.plotly_chart(fig_price, width="stretch")
            else:
                st.warning("Nessun dato nel periodo selezionato.")

    # --- CARD 2: EFFICIENZA MOTORE ---
    with st.container(border=True):
        st.subheader("🚗 Efficienza Consumi (Km/L)")
        c_settings, c_chart = st.columns([1, 3])
        
        with c_settings:
            st.markdown("**Configurazione**")
            range_eff = st.radio("Periodo di analisi:", time_options, index=2, key="filter_eff")
            show_trendline = st.checkbox("Mostra linea di tendenza", value=False)
        
        with c_chart:
            df_eff_base = df.dropna(subset=["Efficienza"])
            df_filtered_eff = filter_data_by_date(df_eff_base, range_eff)
            
            if not df_filtered_eff.empty:
                fig_eff = go.Figure()
                fig_eff.add_trace(go.Scatter(
                    x=df_filtered_eff["Data"], y=df_filtered_eff["Efficienza"],
                    mode='lines+markers', name='Km/L', fill='tozeroy', line=dict(color='#00CC96')
                ))
                fig_eff.update_layout(height=300, margin=dict(l=20, r=20, t=10, b=20), yaxis_title="Km / Litro")
                st.plotly_chart(fig_eff, width="stretch")
            else:
                st.warning("Dati di consumo non sufficienti nel periodo selezionato.")

    # --- CARD 3: SPESA ---
    with st.container(border=True):
        st.subheader("💸 Analisi Spesa")
        c_settings, c_chart = st.columns([1, 3])
        
        with c_settings:
            st.markdown("**Configurazione**")
            range_cost = st.selectbox("Filtra visualizzazione:", time_options, index=4, key="filter_cost")
            st.caption("Il grafico mostra la somma totale spesa raggruppata per mese.")

        with c_chart:
            df_filtered_cost = filter_data_by_date(df, range_cost)
            
            if not df_filtered_cost.empty:
                # Raggruppamento Mensile Dinamico
                monthly_costs = df_filtered_cost.set_index("Data")[["Costo"]].resample("M").sum().reset_index()
                monthly_costs["MeseStr"] = monthly_costs["Data"].dt.strftime('%b %Y')
                
                fig_cost = px.bar(
                    monthly_costs, x="MeseStr", y="Costo",
                    text_auto='.0f',
                    color_discrete_sequence=['#636EFA']
                )
                fig_cost.update_layout(
                    height=300, 
                    margin=dict(l=20, r=20, t=10, b=20), 
                    yaxis_title="Totale €",
                    xaxis_title=""
                )
                fig_cost.update_traces(textfont_size=14, textangle=0, textposition="outside", cliponaxis=False)
                
                # Questa chiamata deve essere indentata DENTRO l'if.
                st.plotly_chart(fig_cost, width="stretch")
            else:
                st.warning("Nessuna spesa registrata nel periodo.")
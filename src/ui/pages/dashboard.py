import streamlit as st
import pandas as pd
from src.database.core import get_db
from src.database import crud
from src.services.business.calculations import calculate_stats, check_partial_accumulation
from src.services.business.analysis import *
from src.ui.components import kpi, charts

def render():
    """Vista Dashboard: Analisi Dati e Trend (Refactored)."""

    # 1. Recupero Dati
    user = st.session_state["user"]
    db = next(get_db())
    records = crud.get_all_refuelings(db, user.id)
    settings = crud.get_settings(db, user.id)
    db.close()

    if not records:
        st.info("👋 Benvenuto! Inizia aggiungendo il tuo primo rifornimento.")
        return

    # 2. Preparazione DataFrame Base
    records_asc = sorted(records, key=lambda x: x.date)
    chart_data = []
    
    # Calcolo medie per il Trip Calculator
    valid_efficiency_values = []
    
    for r in records_asc:
        stats = calculate_stats(r, records)
        eff = stats["km_per_liter"]
        
        if eff:
            valid_efficiency_values.append(eff)
            
        chart_data.append({
            "Data": pd.to_datetime(r.date),
            "Prezzo": r.price_per_liter,
            "Costo": r.total_cost,
            "Litri": r.liters,
            "Efficienza": eff
        })
    df = pd.DataFrame(chart_data)

    # 3. Header e Info
    st.header("📊 Dashboard")
    
    with st.expander("ℹ️ Guida Rapida e Funzionalità", expanded=False):
        st.markdown("""
        **Benvenuto in FuelPyTracker!** Ecco come ottenere il massimo dalla tua app:
        
        * **⛽ Rifornimenti:** Registra ogni sosta alla pompa. Per calcolare i consumi reali (**Km/L**), è fondamentale segnare correttamente quando fai il **Pieno**.
        * **🔧 Manutenzione:** Tieni traccia di Tagliandi, Gomme e Scadenze (Bollo/Revisione).
        * **⚙️ Configurazione:** Dalle Impostazioni puoi importare il tuo storico Excel e tarare gli avvisi di spesa.
        
        *I grafici qui sotto si aggiorneranno automaticamente in base ai tuoi inserimenti.*
        """)

    # 4. KPI Ultimo Rifornimento (Delegato a component)
    last_record = df.iloc[-1]
    st.subheader("⛽ Ultimo Rifornimento")
    
    kpi.render_dashboard_last_record({
        "Data": last_record["Data"].strftime("%d/%m/%y"),
        "Spesa": f"{last_record['Costo']:.2f} €",
        "Prezzo": f"{last_record['Prezzo']:.3f} €",
        "Litri": f"{last_record['Litri']:.2f} L"
    })
    
    # === TRIP CALCULATOR ===
    st.write("")
    # Calcoliamo i dati base per il calcolatore
    avg_kml = sum(valid_efficiency_values) / len(valid_efficiency_values) if valid_efficiency_values else 0
    last_price = last_record['Prezzo']
    
    col_trip, col_alert = st.columns([1, 2], vertical_alignment="center")
    
    with col_trip:
        if st.button("🧮 Calcola Costo Viaggio", use_container_width=True):
             _render_trip_calculator_dialog(avg_kml, last_price)
             
    with col_alert:
        # Alert Parziali (Delegato a service)
        partial_status = check_partial_accumulation(records)
        if partial_status["accumulated_cost"] > settings.max_accumulated_partial_cost:
            st.warning(f"⚠️ Accumulo parziali: {partial_status['accumulated_cost']:.2f} €. Consigliato fare il pieno!")
    
    st.divider()

    # ==========================================
    # SEZIONE: GRAFICI (Delegati a charts.py e analysis.py)
    # ==========================================
    
    time_opts = ["Ultimo Mese", "Ultimi 3 Mesi", "Ultimi 6 Mesi", "Anno Corrente (YTD)", "Ultimo Anno", "Tutto lo storico"]

    # --- GRAFICO 1: TREND PREZZO ---
    with st.container(border=True):
        st.subheader("📉 Prezzo Carburante")
        with st.expander("⚙️ Filtra Periodo", expanded=False):
            range_price = st.selectbox("Periodo:", time_opts, index=1, key="p_filter", label_visibility="collapsed")

        df_p = filter_data_by_date(df, range_price)
        if not df_p.empty:
            st.plotly_chart(charts.build_price_trend_chart(df_p), width="stretch")
        else:
            st.warning("Nessun dato nel periodo.")

    # --- GRAFICO 2: EFFICIENZA ---
    with st.container(border=True):
        st.subheader("🚗 Efficienza (Km/L)")
        with st.expander("⚙️ Opzioni", expanded=False):
            range_eff = st.selectbox("Periodo:", time_opts, index=4, key="e_filter", label_visibility="collapsed")
        
        # Filtriamo prima i nulli, poi le date
        df_e = filter_data_by_date(df.dropna(subset=["Efficienza"]), range_eff)
        if not df_e.empty:
            st.plotly_chart(charts.build_efficiency_chart(df_e), width="stretch")
        else:
            st.warning("Dati insufficienti per calcolare l'efficienza.")

    # --- GRAFICO 3: SPESA MENSILE ---
    with st.container(border=True):
        st.subheader("💸 Analisi Spesa")
        with st.expander("⚙️ Filtra", expanded=False):
            range_cost = st.selectbox("Periodo:", time_opts, index=4, key="c_filter", label_visibility="collapsed")

        df_c = filter_data_by_date(df, range_cost)
        if not df_c.empty:
            st.plotly_chart(charts.build_spending_bar_chart(df_c), width="stretch")
        else:
            st.warning("Nessuna spesa registrata.")


# --- HELPER: Dialog Trip Calculator ---
@st.dialog("🧮 Trip Calculator")
def _render_trip_calculator_dialog(avg_kml, last_price):
    """
    Mostra un modale per calcolare il costo stimato di un viaggio
    basandosi sulla media storica dell'utente.
    """
    st.write("Stima il costo del tuo prossimo viaggio basandoti sui tuoi consumi storici.")
    
    # Input Utente
    trip_km = st.number_input("Quanto è lungo il viaggio? (Km)", min_value=1, value=100, step=10)
    
    # Parametri Modificabili (con default intelligenti)
    with st.expander("🔧 Parametri di Calcolo", expanded=False):
        c1, c2 = st.columns(2)
        calc_kml = c1.number_input("Media Km/L", value=float(f"{avg_kml:.2f}"), min_value=1.0, step=0.5, format="%.2f")
        calc_price = c2.number_input("Prezzo €/L", value=float(f"{last_price:.3f}"), min_value=0.5, step=0.01, format="%.3f")
        st.caption("Default: La tua media storica e l'ultimo prezzo pagato.")

    if st.button("Calcola Costo", type="primary", use_container_width=True):
        # Formula: (Km / (Km/L)) * Prezzo
        liters_needed = trip_km / calc_kml
        estimated_cost = liters_needed * calc_price
        
        st.divider()
        
        # Risultato in evidenza
        st.success(f"💶 Costo Stimato: **{estimated_cost:.2f} €**")
        
        # Dettagli calcolo
        c_res1, c_res2 = st.columns(2)
        c_res1.metric("Carburante Richiesto", f"{liters_needed:.1f} L")
        c_res2.metric("Costo al Km", f"{(estimated_cost/trip_km):.3f} €/km")
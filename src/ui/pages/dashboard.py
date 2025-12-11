import streamlit as st
import pandas as pd
from database.core import get_db
from database import crud
from services.calculations import calculate_stats, check_partial_accumulation
from services import analysis
from ui.components import kpi, charts

def render():
    """Vista Dashboard: Analisi Dati e Trend (Refactored)."""
    
    # 1. Recupero Dati
    db = next(get_db())
    records = crud.get_all_refuelings(db)
    settings = crud.get_settings(db)
    db.close()

    if not records:
        st.info("👋 Benvenuto! Inizia aggiungendo il tuo primo rifornimento.")
        return

    # 2. Preparazione DataFrame Base
    records_asc = sorted(records, key=lambda x: x.date)
    chart_data = []
    
    for r in records_asc:
        stats = calculate_stats(r, records)
        chart_data.append({
            "Data": pd.to_datetime(r.date),
            "Prezzo": r.price_per_liter,
            "Costo": r.total_cost,
            "Litri": r.liters,
            "Efficienza": stats["km_per_liter"] if stats["km_per_liter"] else None
        })
    df = pd.DataFrame(chart_data)

    # 3. Header e Info
    st.title("📊 Dashboard")
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

        df_p = analysis.filter_data_by_date(df, range_price)
        if not df_p.empty:
            st.plotly_chart(charts.build_price_trend_chart(df_p), width="stretch")
        else:
            st.warning("Nessun dato nel periodo.")

    # --- GRAFICO 2: EFFICIENZA ---
    with st.container(border=True):
        st.subheader("🚗 Efficienza (Km/L)")
        with st.expander("⚙️ Opzioni", expanded=False):
            range_eff = st.selectbox("Periodo:", time_opts, index=3, key="e_filter", label_visibility="collapsed")
        
        # Filtriamo prima i nulli, poi le date
        df_e = analysis.filter_data_by_date(df.dropna(subset=["Efficienza"]), range_eff)
        if not df_e.empty:
            st.plotly_chart(charts.build_efficiency_chart(df_e), width="stretch")
        else:
            st.warning("Dati insufficienti per calcolare l'efficienza.")

    # --- GRAFICO 3: SPESA MENSILE ---
    with st.container(border=True):
        st.subheader("💸 Analisi Spesa")
        with st.expander("⚙️ Filtra", expanded=False):
            range_cost = st.selectbox("Periodo:", time_opts, index=4, key="c_filter", label_visibility="collapsed")

        df_c = analysis.filter_data_by_date(df, range_cost)
        if not df_c.empty:
            st.plotly_chart(charts.build_spending_bar_chart(df_c), width="stretch")
        else:
            st.warning("Nessuna spesa registrata.")
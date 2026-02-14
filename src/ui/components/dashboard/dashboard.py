import streamlit as st
import pandas as pd
from src.database.core import get_db
from src.database import crud
from src.services.business.calculations import calculate_stats, check_partial_accumulation
from src.services.business.analysis import filter_data_by_date
from src.services.business import gamification
from src.ui.components.dashboard import kpi, charts
from src.ui.components import startup_alerts

@st.fragment
def render():
    """Vista Dashboard: Analisi Dati, Salute Auto e Trend."""

    # 1. Recupero Dati Essenziali
    user = st.session_state["user"]

    # Init Session State per Calcolatore Viaggio
    if "trip_calc_key" not in st.session_state:
        st.session_state.trip_calc_key = 0
    
    # --- STARTUP CHECK (Pop-up automatico one-shot) ---
    startup_alerts.check_and_show_alerts(user.id)
    
    db = next(get_db())
    records = crud.get_all_refuelings(db, user.id)
    settings = crud.get_settings(db, user.id)
    
    # Recupero ultimo KM noto per calcoli salute
    last_km = max(r.total_km for r in records) if records else 0
    
    # --- CALCOLO HEALTH SCORE ---
    health_score, health_issues = gamification.calculate_car_health_score(db, user.id, last_km)
    
    db.close()

    if not records:
        st.info("👋 Benvenuto! Inizia aggiungendo il tuo primo rifornimento.")
        return

    # 2. Preparazione DataFrame Base (Rifornimenti)
    records_asc = sorted(records, key=lambda x: x.date)
    chart_data = []
    
    # Calcolo medie (necessarie ora per il Tab Funzionalità)
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

    # Dati per Calcolatori e KPI
    last_record = df.iloc[-1]
    avg_kml = sum(valid_efficiency_values) / len(valid_efficiency_values) if valid_efficiency_values else 0
    last_price = last_record['Prezzo']

    # 3. Header e Info (Con TAB)
    st.header("📊 Dashboard")
    
    # Visualizzazione Rapida Salute Auto (Badge)
    health_color = "green" if health_score >= 80 else "orange" if health_score >= 50 else "red"
    st.markdown(f"**Stato Salute Veicolo:** <span style='color:{health_color}; font-weight:bold; font-size:1.2em'>{health_score}%</span>", unsafe_allow_html=True)
    
    with st.expander("ℹ️ Strumenti e Guida", expanded=False):
        tab_guide, tab_tools = st.tabs(["📖 Guida Rapida", "🛠️ Funzionalità"])
        
        with tab_guide:
            st.markdown("""
            **Benvenuto in FuelPyTracker!** Ecco come ottenere il massimo dalla tua app:
            
            * **⛽ Rifornimenti:** Registra ogni sosta alla pompa. Per calcolare i consumi reali (**Km/L**), è fondamentale segnare correttamente quando fai il **Pieno**.
            * **🔧 Manutenzione:** Tieni traccia di Tagliandi, Gomme e Scadenze (Bollo/Revisione).
            * **⚙️ Configurazione:** Dalle Impostazioni puoi importare il tuo storico Excel e tarare gli avvisi di spesa.
            
            *I grafici qui sotto si aggiorneranno automaticamente in base ai tuoi inserimenti.*
            """)
            
        with tab_tools:
            
            # TOOL 1: Trip Calculator
            if st.button("🧮 Calcola Viaggio", width='stretch'):
                st.session_state.trip_calc_key += 1
                _render_trip_calculator_dialog(avg_kml, last_price, st.session_state.trip_calc_key)            
            # TOOL 2: Dettaglio Salute (Nuovo)
            if st.button("🩺 Check-Up Salute", width='stretch'):
                _render_health_dialog(health_score, health_issues)

    # 4. KPI Ultimo Rifornimento
    st.subheader("⛽ Ultimo Rifornimento")
    kpi.render_dashboard_last_record({
        "Data": last_record["Data"].strftime("%d/%m/%y"),
        "Spesa": f"{last_record['Costo']:.2f} €",
        "Prezzo": f"{last_record['Prezzo']:.3f} €",
        "Litri": f"{last_record['Litri']:.2f} L"
    })
    
    # Alert Parziali
    st.write("")
    partial_status = check_partial_accumulation(records)
    if partial_status["accumulated_cost"] > settings.max_accumulated_partial_cost:
        st.warning(f"⚠️ Accumulo parziali: {partial_status['accumulated_cost']:.2f} €. Consigliato fare il pieno!")
    
    st.divider()

    # ==========================================
    # SEZIONE: GRAFICI ANALITICI
    # ==========================================
    
    time_opts = ["Ultimo Mese", "Ultimi 3 Mesi", "Ultimi 6 Mesi", "Anno Corrente (YTD)", "Ultimo Anno", "Tutto lo storico"]

    # --- GRAFICO 1: TREND PREZZO ---
    with st.container(border=True):
        st.subheader("📉 Prezzo Carburante")
        with st.expander("⚙️ Filtra Periodo", expanded=False):
            range_price = st.selectbox("Periodo:", time_opts, index=1, key="p_filter", label_visibility="collapsed")

        df_p = filter_data_by_date(df, range_price)
        if not df_p.empty:
            st.plotly_chart(charts.build_price_trend_chart(df_p), width='stretch', config={'displayModeBar': False, 'scrollZoom': False})
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
            st.plotly_chart(charts.build_efficiency_chart(df_e), width='stretch', config={'displayModeBar': False, 'scrollZoom': False})
        else:
            st.warning("Dati insufficienti per calcolare l'efficienza.")

    # --- GRAFICO 3: SPESA MENSILE ---
    with st.container(border=True):
        st.subheader("💸 Analisi Spesa")
        with st.expander("⚙️ Filtra", expanded=False):
            range_cost = st.selectbox("Periodo:", time_opts, index=4, key="c_filter", label_visibility="collapsed")

        df_c = filter_data_by_date(df, range_cost)
        if not df_c.empty:
            st.plotly_chart(charts.build_spending_bar_chart(df_c), width='stretch', config={'displayModeBar': False, 'scrollZoom': False})
        else:
            st.warning("Nessuna spesa registrata.")


# --- DIALOGS ---

@st.dialog("🧮 Trip Calculator")
def _render_trip_calculator_dialog(avg_kml, last_price, key_suffix):
    """
    Mostra un modale per calcolare il costo stimato.
    Usa key_suffix per forzare il reset dei widget ad ogni apertura.
    """
    st.write("Stima il costo del tuo prossimo viaggio basandoti sui tuoi consumi storici.")
    
    # Input Utente (Key dinamica)
    trip_km = st.number_input(
        "Quanto è lungo il viaggio? (Km)", 
        min_value=1, value=100, step=10, 
        key=f"trip_km_{key_suffix}"
    )
    
    # Parametri Modificabili
    with st.expander("🔧 Parametri di Calcolo", expanded=False):
        c1, c2 = st.columns(2)
        calc_kml = c1.number_input(
            "Media Km/L", 
            value=float(f"{avg_kml:.2f}"), min_value=1.0, step=0.5, format="%.2f",
            key=f"trip_kml_{key_suffix}"
        )
        calc_price = c2.number_input(
            "Prezzo €/L", 
            value=float(f"{last_price:.3f}"), min_value=0.5, step=0.01, format="%.3f",
            key=f"trip_price_{key_suffix}"
        )
        st.caption("Default: La tua media storica e l'ultimo prezzo pagato.")

    if st.button("Calcola Costo", type="primary", width='stretch', key=f"trip_btn_{key_suffix}"):
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
        
        
@st.dialog("🩺 Check-Up Salute Auto")
def _render_health_dialog(score, issues):
    """Mostra i dettagli del punteggio e i problemi aperti."""
    
    # Colore dinamico
    color = "green" if score >= 80 else "orange" if score >= 50 else "red"
    
    st.markdown(
        f"""
        <div style="text-align: center; margin-bottom: 20px;">
            <h1 style="color: {color}; margin:0;">{score}%</h1>
            <span>Punteggio Salute</span>
        </div>
        """, 
        unsafe_allow_html=True
    )
    
    if score == 100:
        st.balloons()
        st.success("🌟 Complimenti! La tua auto è mantenuta perfettamente.")
        st.caption("Continua a registrare regolarmente i controlli di routine per mantenere il punteggio.")
    else:
        st.warning(f"Ci sono **{len(issues)}** aspetti da curare:")
        
        for issue in issues:
            st.error(f"🔴 {issue}", icon="🔧")
            
        st.divider()
        st.markdown("**Come migliorare?**")
        st.info("Vai alla sezione **Manutenzione** e risolvi le scadenze o registra i controlli di routine mancanti.")
        
        if st.button("Vai a Manutenzione", type="primary", width='stretch'):
            st.session_state.current_page = "Manutenzione"
            st.rerun()
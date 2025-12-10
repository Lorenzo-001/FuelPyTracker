import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from database.core import get_db
from database import crud
from services.calculations import calculate_stats, check_partial_accumulation

def filter_data_by_date(df, range_option):
    """
    Filtra il dataframe in base all'opzione temporale selezionata.
    Logica invariata rispetto all'originale.
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
    # Se "Tutto lo storico", cutoff_date rimane None
    
    if cutoff_date:
        return df[df["Data"] >= cutoff_date]
    return df

def render():
    """Vista principale: Dashboard Interattiva (Mobile Optimized)."""
    
    # --- 1. Recupero Dati (Logica Invariata) ---
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

    # --- SEZIONE 1: HEADER ---
    st.title("📊 Dashboard")
    
    # Usiamo un expander chiuso di default per risparmiare spazio verticale all'avvio
    with st.expander("ℹ️ Guida e Info", expanded=False):
        st.markdown("""
        **Benvenuto nella tua area di analisi.**
        - **Ultimo Rifornimento**: Dettagli operazione più recente.
        - **Trend**: Costo carburante ed efficienza (Km/L).
        - **Spesa**: Totali mensili.
        """)

    # --- SEZIONE 2: CARD "ULTIMO RIFORNIMENTO" (Mobile Grid) ---
    last_record = df.iloc[-1]
    
    st.subheader("⛽ Ultimo Rifornimento")
    
    # Preparazione dati formattati
    dati_kpi = {
        "Data": last_record["Data"].strftime("%d/%m/%y"),
        "Spesa": f"{last_record['Costo']:.2f} €",
        "Prezzo": f"{last_record['Prezzo']:.3f} €",
        "Litri": f"{last_record['Litri']:.2f} L"
    }

    # CSS Personalizzato per forzare il layout affiancato su mobile
    # Questo crea una griglia 2x2 che NON si impila (stack) su mobile
    custom_kpi_html = f"""
    <style>
        .kpi-container {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            justify-content: space-between;
            margin-bottom: 10px;
        }}
        .kpi-card {{
            background-color: #f0f2f6; /* Grigio chiaro standard Streamlit */
            border-radius: 8px;
            padding: 10px;
            flex: 1 1 45%; /* Occupa circa il 45% della larghezza, permettendo 2 per riga */
            text-align: center;
            border: 1px solid #e0e0e0;
        }}
        .kpi-label {{
            font-size: 0.8rem; /* Font più piccolo per l'etichetta */
            color: #555;
            margin-bottom: 2px;
        }}
        .kpi-value {{
            font-size: 1.1rem; /* Font valore ridotto rispetto allo standard (che è 1.6rem) */
            font-weight: 600;
            color: #000;
        }}
        /* Dark mode compatibility (opzionale, se usi il tema scuro) */
        @media (prefers-color-scheme: dark) {{
            .kpi-card {{ background-color: #262730; border-color: #444; }}
            .kpi-label {{ color: #aaa; }}
            .kpi-value {{ color: #fff; }}
        }}
    </style>

    <div class="kpi-container">
        <div class="kpi-card">
            <div class="kpi-label">📅 Data</div>
            <div class="kpi-value">{dati_kpi['Data']}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">💶 Spesa</div>
            <div class="kpi-value">{dati_kpi['Spesa']}</div>
        </div>
    </div>
    
    <div class="kpi-container">
        <div class="kpi-card">
            <div class="kpi-label">🏷️ Prezzo/L</div>
            <div class="kpi-value">{dati_kpi['Prezzo']}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-label">🛢️ Litri</div>
            <div class="kpi-value">{dati_kpi['Litri']}</div>
        </div>
    </div>
    """
    
    # Renderizziamo l'HTML invece di usare st.metric
    st.markdown(custom_kpi_html, unsafe_allow_html=True)

    # Avviso accumulo parziali
    partial_status = check_partial_accumulation(records)
    if partial_status["accumulated_cost"] > settings.max_accumulated_partial_cost:
        st.warning(f"⚠️ Accumulo parziali: {partial_status['accumulated_cost']:.2f} €. Fai il pieno!")

    st.markdown("---")

    # --- SEZIONE 3: GRAFICI (Stacking Verticale) ---
    
    time_options = ["Ultimo Mese", "Ultimi 3 Mesi", "Ultimi 6 Mesi", "Anno Corrente (YTD)", "Ultimo Anno", "Tutto lo storico"]

    # --- CARD 1: TREND PREZZO ---
    with st.container(border=True):
        # Header + Configurazione in Expander (Pattern "Clean Look")
        col_header, col_config = st.columns([3, 1])
        with col_header:
            st.subheader("📉 Prezzo Carburante")
        
        # Le impostazioni non rubano spazio al grafico, sono nascoste/richiamabili
        with st.expander("⚙️ Filtra Periodo", expanded=False):
            # Usiamo selectbox invece di radio per risparmiare altezza verticale
            range_price = st.selectbox("Seleziona periodo:", time_options, index=1, key="filter_price")

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
                mode='lines', name='Media', line=dict(color='gray', dash='dash')
            ))
            # Margini ottimizzati per mobile (meno spazio bianco ai lati)
            fig_price.update_layout(
                height=300, 
                margin=dict(l=10, r=10, t=10, b=10), 
                yaxis_title="€ / Litro",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig_price, width="stretch")
        else:
            st.warning("Nessun dato nel periodo.")

    # --- CARD 2: EFFICIENZA MOTORE ---
    with st.container(border=True):
        st.subheader("🚗 Efficienza (Km/L)")
        
        with st.expander("⚙️ Opzioni Grafico", expanded=False):
            c_f1, c_f2 = st.columns(2)
            with c_f1:
                range_eff = st.selectbox("Periodo:", time_options, index=2, key="filter_eff")
            with c_f2:
                # Checkbox allineata verticalmente
                st.write("") # Spacer
                st.write("") # Spacer
                show_trendline = st.checkbox("Trendline", value=False)
        
        df_eff_base = df.dropna(subset=["Efficienza"])
        df_filtered_eff = filter_data_by_date(df_eff_base, range_eff)
        
        if not df_filtered_eff.empty:
            fig_eff = go.Figure()
            fig_eff.add_trace(go.Scatter(
                x=df_filtered_eff["Data"], y=df_filtered_eff["Efficienza"],
                mode='lines+markers', name='Km/L', fill='tozeroy', line=dict(color='#00CC96')
            ))
            fig_eff.update_layout(
                height=300, 
                margin=dict(l=10, r=10, t=10, b=10), 
                yaxis_title="Km / Litro",
                legend=dict(orientation="h", y=1.1)
            )
            st.plotly_chart(fig_eff, width="stretch")
        else:
            st.warning("Dati insufficienti.")

    # --- CARD 3: SPESA ---
    with st.container(border=True):
        st.subheader("💸 Analisi Spesa")
        
        with st.expander("⚙️ Filtra Periodo", expanded=False):
            range_cost = st.selectbox("Visualizza:", time_options, index=4, key="filter_cost")

        df_filtered_cost = filter_data_by_date(df, range_cost)
        
        if not df_filtered_cost.empty:
            monthly_costs = df_filtered_cost.set_index("Data")[["Costo"]].resample("M").sum().reset_index()
            # Formato data breve per asse X mobile (Gen 23 invece di Gennaio 2023)
            monthly_costs["MeseStr"] = monthly_costs["Data"].dt.strftime('%b %y')
            
            fig_cost = px.bar(
                monthly_costs, x="MeseStr", y="Costo",
                text_auto='.0f',
                color_discrete_sequence=['#636EFA']
            )
            fig_cost.update_layout(
                height=300, 
                margin=dict(l=10, r=10, t=10, b=10), 
                yaxis_title="Totale €",
                xaxis_title=""
            )
            fig_cost.update_traces(textfont_size=14, textangle=0, textposition="outside", cliponaxis=False)
            
            st.plotly_chart(fig_cost, width="stretch")
        else:
            st.warning("Nessuna spesa nel periodo.")
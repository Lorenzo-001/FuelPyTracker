import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database.core import get_db
from database import crud
from services.calculations import calculate_stats, check_partial_accumulation

def render():
    """Vista principale: Dashboard Professionale con Plotly."""
    st.header("📊 Dashboard Analitica")
    
    # 1. Recupero dati DB e Settings
    db = next(get_db())
    records = crud.get_all_refuelings(db)
    settings = crud.get_settings(db)
    db.close()

    if not records:
        st.info("Nessun dato disponibile. Inizia aggiungendo un rifornimento!")
        return

    # 2. CONTROLLO "STALE DATA" (Parziali accumulati)
    # Verifica se l'utente ha accumulato troppi parziali senza fare il pieno
    partial_status = check_partial_accumulation(records)
    
    if partial_status["accumulated_cost"] > settings.max_accumulated_partial_cost:
        st.warning(
            f"⚠️ **Attenzione:** Hai accumulato **{partial_status['accumulated_cost']:.2f} €** di rifornimenti parziali ({partial_status['partials_count']} consecutivi) senza fare il pieno.\n\n"
            "Le statistiche di consumo (Km/L) sono attualmente sospese o stimate. "
            "Ti consigliamo di effettuare un **Pieno Completo** al prossimo rifornimento per ripristinare la precisione dei calcoli.",
            icon="⛽"
        )

    # 3. Preparazione Dataset
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

    # 4. Calcolo KPI
    last_record = df.iloc[-1]
    last_price = last_record["Prezzo"]
    
    valid_eff = df["Efficienza"].dropna()
    avg_efficiency = valid_eff.mean() if not valid_eff.empty else 0
    total_spent = df["Costo"].sum()
    avg_price = df["Prezzo"].mean()

    # 5. Visualizzazione KPI
    c1, c2, c3 = st.columns(3)
    c1.metric("Ultimo Prezzo", f"{last_price:.3f} €/L", delta=f"{last_price - avg_price:.3f} vs media", delta_color="inverse")
    c2.metric("Consumo Medio", f"{avg_efficiency:.2f} km/L")
    c3.metric("Spesa Totale", f"{total_spent:.2f} €")
    
    st.markdown("---")

    # 6. Grafici Avanzati con Plotly
    
    # --- GRAFICO 1: ANALISI PREZZO ---
    st.subheader("🏷️ Trend Prezzo Carburante")
    
    fig_price = go.Figure()
    
    fig_price.add_trace(go.Scatter(
        x=df["Data"], 
        y=df["Prezzo"],
        mode='lines+markers',
        name='Prezzo al Litro',
        line=dict(color='#EF553B', width=3),
        marker=dict(size=8),
        hovertemplate='<b>%{x|%d/%m/%Y}</b><br>Prezzo: %{y:.3f} €/L<extra></extra>'
    ))
    
    fig_price.add_trace(go.Scatter(
        x=df["Data"], 
        y=[avg_price] * len(df),
        mode='lines',
        name='Prezzo Medio Storico',
        line=dict(color='gray', width=2, dash='dash'),
        hovertemplate='Media: %{y:.3f} €/L<extra></extra>'
    ))

    fig_price.update_layout(
        height=350,
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis_title="Euro / Litro (€)",
        hovermode="x unified"
    )
    st.plotly_chart(fig_price, use_container_width=True)


    col_left, col_right = st.columns(2)

    # --- GRAFICO 2: EFFICIENZA MOTORE ---
    with col_left:
        st.subheader("🚗 Efficienza (Km/L)")
        if not valid_eff.empty:
            df_eff = df.dropna(subset=["Efficienza"])
            
            fig_eff = go.Figure()
            
            fig_eff.add_trace(go.Scatter(
                x=df_eff["Data"], 
                y=df_eff["Efficienza"],
                mode='lines+markers',
                fill='tozeroy', 
                name='Km/L',
                line=dict(color='#00CC96', width=2),
                hovertemplate='<b>%{y:.2f} km/L</b><extra></extra>'
            ))

            fig_eff.update_layout(
                height=300,
                margin=dict(l=20, r=20, t=30, b=20),
                yaxis_title="Km per Litro",
                showlegend=False
            )
            st.plotly_chart(fig_eff, use_container_width=True)
        else:
            st.warning("Dati insufficienti per il grafico consumi.")

    # --- GRAFICO 3: SPESA MENSILE ---
    with col_right:
        st.subheader("💸 Spesa Mensile")
        
        monthly_costs = df.set_index("Data")[["Costo"]].resample("M").sum().reset_index()
        monthly_costs["MeseStr"] = monthly_costs["Data"].dt.strftime('%b %Y') 

        if not monthly_costs.empty:
            fig_cost = go.Figure(go.Bar(
                x=monthly_costs["MeseStr"],
                y=monthly_costs["Costo"],
                text=monthly_costs["Costo"].apply(lambda x: f"{x:.0f}€"),
                textposition='auto',
                marker_color='#636EFA'
            ))

            fig_cost.update_layout(
                height=300,
                margin=dict(l=20, r=20, t=30, b=20),
                yaxis_title="Totale (€)",
                showlegend=False
            )
            st.plotly_chart(fig_cost, use_container_width=True)
        else:
            st.info("Dati insufficienti.")
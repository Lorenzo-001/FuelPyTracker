import streamlit as st
import textwrap

# ==========================================
# SEZIONE: KPI DASHBOARD
# ==========================================

def render_dashboard_last_record(dati: dict):
    """
    Renderizza la card 2x2 per l'ultimo rifornimento in Dashboard.
    """
    style = """
    <style>
        .db-kpi-container {
            display: flex; flex-wrap: wrap; gap: 10px;
            justify-content: space-between; margin-bottom: 10px;
        }
        .db-kpi-card {
            background-color: #f0f2f6; border-radius: 8px; padding: 10px;
            flex: 1 1 45%; /* 2 colonne su mobile */
            text-align: center; border: 1px solid #e0e0e0;
        }

        .db-kpi-label { 
            font-size: 1rem; 
            font-weight: 600; 
            color: #444; 
            margin-bottom: 2px; 
        }
        .db-kpi-value { font-size: 1.1rem; font-weight: 800; color: #000; }
        
        @media (prefers-color-scheme: dark) {
            .db-kpi-card { background-color: #262730; border-color: #444; }
            .db-kpi-label { color: #ccc; } /* Più chiaro in dark mode */
            .db-kpi-value { color: #fff; }
        }
    </style>
    """
    
    html = f"""
    {style}
    <div class="db-kpi-container">
        <div class="db-kpi-card"><div class="db-kpi-label">📅 Data</div><div class="db-kpi-value">{dati['Data']}</div></div>
        <div class="db-kpi-card"><div class="db-kpi-label">💶 Spesa</div><div class="db-kpi-value">{dati['Spesa']}</div></div>
    </div>
    <div class="db-kpi-container">
        <div class="db-kpi-card"><div class="db-kpi-label">🏷️ Prezzo/L</div><div class="db-kpi-value">{dati['Prezzo']}</div></div>
        <div class="db-kpi-card"><div class="db-kpi-label">🛢️ Litri</div><div class="db-kpi-value">{dati['Litri']}</div></div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
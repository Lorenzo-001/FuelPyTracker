import streamlit as st
import textwrap

# ==========================================
# SEZIONE: KPI RIFORNIMENTI (Fuel Cards)
# ==========================================

def render_fuel_cards(year, cost, liters, km_est, avg_price, min_eff, max_eff):
    """
    Renderizza la dashboard KPI per la pagina Rifornimenti.
    Layout: Big Card a sinistra (Spesa/Litri) + Grid 2x2 a destra (Km, Prezzo, Efficienza).
    Responsive: Si adatta automaticamente su mobile.
    """
    
    # 1. Definizione Stili CSS
    css_style = textwrap.dedent("""
        <style>
            /* Container Principale Flex */
            .kpi-container-wrapper {
                display: flex; flex-wrap: wrap; gap: 15px; margin-bottom: 20px;
                align-items: stretch; width: 100%;
            }
            
            /* Sezioni (Main SX / Grid DX) */
            .kpi-main-section { flex: 4; min-width: 250px; display: flex; flex-direction: column; }
            .kpi-grid-section { 
                flex: 6; min-width: 250px; display: grid; 
                grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr; gap: 8px; 
            }
            
            /* Card Principale (Spesa) */
            .big-card-compact {
                background-color: #f0f2f6; border-radius: 12px; padding: 15px;
                border-left: 6px solid #ff4b4b; height: 100%; display: flex;
                flex-direction: column; justify-content: center; 
                box-shadow: 0 2px 5px rgba(0,0,0,0.05); color: #31333F;
            }
            .big-card-title {
                margin: 5px 0; font-weight: 700; font-size: clamp(24px, 4vw, 32px); 
                white-space: nowrap; color: #31333F;
            }
            
            /* Card Secondarie (Grid) */
            .kpi-card-compact {
                background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 8px;
                padding: 8px; display: flex; flex-direction: column;
                justify-content: center; align-items: center; text-align: center;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1); white-space: nowrap;
            }
            
            .kpi-label { 
                font-size: 1rem; 
                font-weight: 800; 
                color: #444; 
                margin-bottom: 2px; 
            }
            .kpi-value { font-size: clamp(0.9rem, 2vw, 1.1rem); font-weight: 700; color: #333; }
            
            /* Dark Mode Overrides */
            @media (prefers-color-scheme: dark) {
                .big-card-compact { background-color: #262730; border: 1px solid #444; color: #FFF; }
                .big-card-title { color: #FFF; }
                .kpi-card-compact { background-color: #262730; border: 1px solid #444; }
                .kpi-label { color: #ccc; }
                .kpi-value { color: #fff; }
            }
        </style>
    """)

    # 2. Markup HTML
    html_content = textwrap.dedent(f"""
        <div class="kpi-container-wrapper">
            <div class="kpi-main-section">
                <div class="big-card-compact">
                    <p style="margin:0; font-size: 1rem; opacity: 0.9; font-weight: 600;">💰 Spesa Totale {year}</p>
                    <h2 class="big-card-title">{cost:.2f} €</h2>
                    <p style="margin:0; font-size: 1rem; opacity: 0.8;">⛽ <b>{liters:.1f}</b> Litri</p>
                </div>
            </div>
            
            <div class="kpi-grid-section">
                <div class="kpi-card-compact">
                    <div class="kpi-label">🛣️ Km Stimati</div>
                    <div class="kpi-value">{km_est}</div>
                </div>
                <div class="kpi-card-compact">
                    <div class="kpi-label">🏷️ Media €/L</div>
                    <div class="kpi-value">{avg_price:.3f} €</div>
                </div>
                <div class="kpi-card-compact">
                    <div class="kpi-label">📉 Min Km/L</div>
                    <div class="kpi-value">{min_eff:.1f}</div>
                </div>
                <div class="kpi-card-compact">
                    <div class="kpi-label">📈 Max Km/L</div>
                    <div class="kpi-value">{max_eff:.1f}</div>
                </div>
            </div>
        </div>
    """)
    
    st.markdown(css_style, unsafe_allow_html=True)
    st.html(html_content)
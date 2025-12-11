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


# ==========================================
# SEZIONE: KPI MANUTENZIONE (Maintenance Card)
# ==========================================

def render_maintenance_card(cost, year_label):
    """
    Renderizza la card orizzontale compatta per la pagina Manutenzione.
    Stile: Gradiente Arancione, layout Flexbox.
    """
    
    css = textwrap.dedent("""
        <style>
            .maint-card-grad {
                /* Layout Container */
                height: 40px; width: 100%; box-sizing: border-box;
                display: flex; flex-direction: row; 
                justify-content: space-between; align-items: center;
                
                /* Stile Visuale Light */
                background: linear-gradient(135deg, #FFF8E1 0%, #FFFFFF 100%);
                border-radius: 8px; padding: 0 15px;
                border: 1px solid rgba(255, 166, 0, 0.3);
                border-left: 5px solid #ffa600;
                box-shadow: 0 2px 4px rgba(255, 166, 0, 0.1);
            }

            .maint-label-grad {
                font-size: 0.9rem; /* Leggermente aumentato */
                font-weight: 700; /* Più bold */
                color: #333; 
                margin: 0;
            }

            .maint-value-grad {
                font-size: 1.1rem; font-weight: 800;
                background: -webkit-linear-gradient(rgb(255 60 0), #ff9100);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                white-space: nowrap;
            }
            
            /* Dark Mode */
            @media (prefers-color-scheme: dark) {
                .maint-card-grad { 
                    background: linear-gradient(135deg, #3e3020 0%, #262730 100%);
                    border: 1px solid #554433; border-left: 5px solid #ffa600;
                }
                .maint-label-grad { color: #ffb74d; }
                .maint-value-grad { 
                    background: none; -webkit-text-fill-color: #fff; color: #fff;
                }
            }
        </style>
    """)

    html = textwrap.dedent(f"""
        <div class="maint-card-grad">
            <div class="maint-label-grad">
                <span>Spesa totale {year_label}:</span>
            </div>
            <div class="maint-value-grad">{cost:,.2f} €</div>
        </div>
    """)
    
    st.markdown(css, unsafe_allow_html=True)
    st.html(html)
import streamlit as st
import textwrap

def render_fuel_cards(year, cost, liters, km_est, avg_price, min_eff, max_eff):
    """
    Renderizza la sezione KPI per i rifornimenti con layout responsive.
    """
    css_style = textwrap.dedent("""
        <style>
            .kpi-container-wrapper {
                display: flex; flex-wrap: wrap; gap: 15px; margin-bottom: 20px;
                align-items: stretch; width: 100%;
            }
            .kpi-main-section { flex: 4; min-width: 0; display: flex; flex-direction: column; }
            .kpi-grid-section { 
                flex: 6; min-width: 0; display: grid; 
                grid-template-columns: 1fr 1fr; grid-template-rows: 1fr 1fr; gap: 8px; 
            }
            .big-card-compact {
                background-color: #f0f2f6; border-radius: 12px; padding: 15px;
                border-left: 6px solid #ff4b4b; height: 100%; display: flex;
                flex-direction: column; justify-content: center; box-shadow: 0 2px 5px rgba(0,0,0,0.05);
                color: #31333F; overflow: hidden;
            }
            .big-card-title {
                margin: 5px 0; font-weight: 700; font-size: clamp(18px, 4vw, 32px); white-space: nowrap;
            }
            .kpi-card-compact {
                background-color: #262730; border: 1px solid #444; border-radius: 8px;
                padding: 8px; display: flex; flex-direction: column;
                justify-content: center; align-items: center; text-align: center;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2); white-space: nowrap; overflow: hidden;
            }
            .kpi-label { font-size: 0.75rem; color: #aaa; margin-bottom: 2px; width: 100%; text-overflow: ellipsis; overflow: hidden; }
            .kpi-value { font-size: clamp(0.9rem, 2vw, 1.1rem); font-weight: 600; color: #fff; }
            
            @media (prefers-color-scheme: dark) {
                .big-card-compact { background-color: #262730; border: 1px solid #444; border-left: 6px solid #ff4b4b; color: #FFFFFF; }
                .big-card-compact p { color: #cccccc; }
            }
        </style>
    """)

    html_content = textwrap.dedent(f"""
        <div class="kpi-container-wrapper">
            <div class="kpi-main-section">
                <div class="big-card-compact">
                    <p style="margin:0; font-size: 14px; opacity: 0.8;">💰 Spesa Totale {year}</p>
                    <h2 class="big-card-title">{cost:.2f} €</h2>
                    <p style="margin:0; font-size: 13px; opacity: 0.7;">⛽ <b>{liters:.1f}</b> Litri</p>
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
import streamlit as st
import textwrap

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
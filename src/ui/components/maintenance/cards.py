import streamlit as st
from datetime import date
from src.services.business.prediction import predict_reach_date
from src.ui.components.maintenance import dialogs

def render_predictive_section(db, user, records, last_known_km, daily_rate):
    """Renderizza le card scadenze con logica a semaforo."""
    
    # 1. LOGICA DI CALCOLO
    candidates = []
    today = date.today()
    
    for r in records:
        exp_km = getattr(r, 'expiry_km', None)
        exp_date = getattr(r, 'expiry_date', None)
        
        if not exp_km and not exp_date: continue

        km_left = (exp_km - last_known_km) if exp_km else None
        days_left = (exp_date - today).days if exp_date else None
        
        status_color = "#28a745" # Verde
        priority = 3
        
        is_expired_km = (km_left is not None and km_left < 0)
        is_expired_days = (days_left is not None and days_left < 0)

        if is_expired_km or is_expired_days:
            status_color = "#dc3545" # Rosso
            priority = 1
        elif (km_left is not None and km_left <= 1000) or (days_left is not None and days_left <= 30):
            status_color = "#ffc107" # Giallo
            priority = 2
            
        candidates.append({
            "record": r, "km_left": km_left, "days_left": days_left,
            "color": status_color, "priority": priority,
            "sort_val": km_left if km_left is not None else (days_left * 50 if days_left else 999999)
        })

    # 2. DEDUPLICAZIONE
    unique_upcoming = {}
    for c in candidates:
        m_type = c["record"].expense_type
        if m_type not in unique_upcoming:
            unique_upcoming[m_type] = c
        else:
            if c["priority"] < unique_upcoming[m_type]["priority"]:
                unique_upcoming[m_type] = c
    
    final_upcoming = sorted(list(unique_upcoming.values()), key=lambda x: (x["priority"], x["sort_val"]))
    
    if not final_upcoming:
        st.success("✅ Nessuna scadenza imminente! Sei in regola con la manutenzione.")
        return

    st.caption(f"Stima basata su un utilizzo medio di **{daily_rate:.1f} km/giorno**.")
    st.write("")    
    
    # 3. VISUALIZZAZIONE
    cols = st.columns(3)
    for idx, item_data in enumerate(final_upcoming):
        item = item_data["record"]
        col = cols[idx % 3]
        
        color = item_data["color"]
        km_left = item_data["km_left"]
        days_left = item_data["days_left"]
        
        with col:
            with st.container(border=True):
                # Header
                icon = "🔧"
                if "Gomme" in item.expense_type: icon = "🛞"
                elif "Revisione" in item.expense_type: icon = "📋"
                elif "Assicurazione" in item.expense_type: icon = "📄"
                elif "Bollo" in item.expense_type: icon = "💰"

                st.markdown(f"""
                    <div style="border-left: 5px solid {color}; padding-left: 10px; margin-bottom: 8px; font-weight: bold; font-size: 1.1em;">
                        {icon} {item.expense_type}
                    </div>
                    """, unsafe_allow_html=True)
                
                # Dati
                if km_left is not None:
                    st.caption(f"Scadenza: {item.expiry_km} Km")
                    if km_left < 0:
                        st.markdown(f"📉 Scaduta da **{-km_left} Km**")
                    else:
                        st.markdown(f"📉 **Tra {km_left} Km**")
                        if daily_rate > 0:
                            est_date = predict_reach_date(last_known_km, item.expiry_km, daily_rate)
                            if est_date: st.markdown(f"<span style='color:#3498db; font-size:0.9em'>📅 Stima: {est_date.strftime('%d/%m/%y')}</span>", unsafe_allow_html=True)
                
                elif days_left is not None:
                    st.caption(f"Scadenza: {item.expiry_date.strftime('%d/%m')}")
                    if days_left < 0:
                         st.markdown(f"⚠️ Scaduta da **{-days_left} Giorni**")
                    elif days_left <= 30:
                        st.markdown(f"<span style='color:#e74c3c; font-weight:bold'>⚠️ Tra {days_left} Giorni</span>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"📅 **Tra {days_left} Giorni**")

                st.write("")
                
                # Bottoni Azione
                c_done, c_trash = st.columns([2, 2])
                if c_done.button("✅", key=f"btn_done_{item.id}", help="Registra esecuzione", width='stretch'):
                    dialogs.render_resolve_dialog(db, user, item)
                
                if c_trash.button("❌", key=f"btn_del_{item.id}", help="Rimuovi solo scadenza", width='stretch'):
                    dialogs.render_remove_deadline_dialog(db, user, item)
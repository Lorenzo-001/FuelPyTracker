import streamlit as st
import pandas as pd
from datetime import date
from database.core import get_db
from database import crud
from services.calculations import calculate_stats
from services import importers

def render_dashboard():
    """
    Renderizza la pagina principale con i riepiloghi (KPI).
    """
    st.header("📊 Dashboard Riepilogativa")
    
    # 1. Recupero Dati
    db = next(get_db())
    all_refuelings = crud.get_all_refuelings(db)
    db.close()

    if not all_refuelings:
        st.info("Nessun dato disponibile. Inizia aggiungendo un rifornimento!")
        return

    # 2. Calcolo Statistiche Globali
    # Creiamo un DataFrame Pandas per facilitare i calcoli di media
    data_list = []
    
    # Per calcolare l'efficienza di ogni record, dobbiamo ri-applicare la logica su tutto lo storico
    # Nota: Questo potrebbe essere ottimizzato salvando il dato calcolato nel DB, 
    # ma per ora calcolarlo al volo va benissimo per dataset < 10.000 righe.
    for i, record in enumerate(all_refuelings):
        # history deve essere la lista completa (o almeno dal record corrente in giù)
        # Passiamo 'all_refuelings' che è già ordinata per data decrescente
        stats = calculate_stats(record, all_refuelings)
        
        row = {
            "date": record.date,
            "price": record.price_per_liter,
            "km_per_liter": stats["km_per_liter"],
            "total_cost": record.total_cost
        }
        data_list.append(row)

    df = pd.DataFrame(data_list)

    # --- KPI 1: Ultimo Prezzo ---
    last_record = all_refuelings[0]
    last_price = last_record.price_per_liter
    
    # --- KPI 2: Consumo Medio (Escludendo i parziali/null) ---
    avg_consumption = df["km_per_liter"].mean()
    
    # --- KPI 3: Totale Speso (All Time) ---
    total_spent = df["total_cost"].sum()

    # 3. Visualizzazione KPI
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="Ultimo Prezzo Carburante", value=f"{last_price:.3f} €/L")
    
    with col2:
        valore_media = f"{avg_consumption:.2f} km/L" if not pd.isna(avg_consumption) else "N/A"
        st.metric(label="Consumo Medio Storico", value=valore_media)
        
    with col3:
        st.metric(label="Spesa Totale (Storico)", value=f"{total_spent:.2f} €")

    st.divider()
    st.caption("I grafici di andamento verranno visualizzati qui nel prossimo step.")

def render_fuel_page():
    """
    Form per inserimento Rifornimenti con VALIDAZIONE.
    """
    st.header("⛽ Gestione Rifornimenti")

    # 1. Recuperiamo l'ultimo chilometraggio noto per aiutare l'utente
    db = next(get_db())
    last_known_km = crud.get_max_km(db)
    db.close()

    # --- FORM DI INSERIMENTO ---
    with st.expander("Aggiungi Nuovo Rifornimento", expanded=True):
        with st.form("fuel_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                d_date = st.date_input("Data", value=date.today())
                # VALIDAZIONE VISIVA:
                # Impostiamo il valore di default pari all'ultimo + 1 (o 0 se vuoto)
                # Non usiamo min_value=last_known_km qui perché potresti voler inserire
                # un dato vecchio (storico 2019) che è legittimamente inferiore all'oggi.
                default_km = last_known_km if last_known_km > 0 else 0
                d_km = st.number_input("Chilometri Totali (Odometer)", value=default_km, step=1, format="%d")
            
            with col2:
                d_price = st.number_input("Prezzo al Litro (€)", min_value=0.0, step=0.001, format="%.3f")
                d_cost = st.number_input("Spesa Totale (€)", min_value=0.0, step=0.01, format="%.2f")

            d_full = st.checkbox("Pieno Completato?", value=True)
            d_notes = st.text_area("Note (Opzionale)")

            submitted = st.form_submit_button("Salva Rifornimento")

            if submitted:
                # --- VALIDAZIONE LOGICA (IL CONTROLLO) ---
                validation_error = None
                
                # Check 1: Prezzi sensati
                if d_price <= 0 or d_cost <= 0:
                    validation_error = "⚠️ Inserisci un prezzo e un costo validi (maggiori di 0)."
                
                # Check 2: Controllo coerenza Kilometri (Solo se stiamo inserendo dati recenti)
                # Se la data inserita è OGGI o futura, i km DEVONO essere > del massimo storico.
                if d_date >= date.today() and d_km < last_known_km:
                    validation_error = f"⛔ Errore Chilometri: Hai inserito {d_km} km, ma l'ultimo rifornimento era a {last_known_km} km. Non puoi tornare indietro nel tempo!"

                # Se c'è un errore, blocchiamo tutto
                if validation_error:
                    st.error(validation_error)
                else:
                    # PROSEGUIAMO COL SALVATAGGIO
                    calculated_liters = d_cost / d_price
                    
                    db = next(get_db())
                    try:
                        crud.create_refueling(
                            db=db,
                            date_obj=d_date,
                            total_km=d_km,
                            price_per_liter=d_price,
                            total_cost=d_cost,
                            liters=calculated_liters,
                            is_full_tank=d_full,
                            notes=d_notes
                        )
                        st.success(f"✅ Rifornimento salvato! ({calculated_liters:.2f} L)")
                        st.cache_data.clear() # Pulisce la cache per aggiornare la tabella
                    except Exception as e:
                        st.error(f"Errore durante il salvataggio: {e}")
                    finally:
                        db.close()

    # --- TABELLA STORICO ---
    st.divider()
    st.subheader("Storico e Consumi")
    
    # ... (Il resto della funzione tabella rimane uguale a prima) ...
    # Se vuoi ricopio anche la tabella, ma quella non cambia.
    
    # [CODICE TABELLA IDENTICO AL PRECEDENTE...]
    db = next(get_db())
    records = crud.get_all_refuelings(db)
    db.close()

    if records:
        table_data = []
        for r in records:
            stats = calculate_stats(r, records)
            kml_str = f"{stats['km_per_liter']:.2f}" if stats['km_per_liter'] else "-"
            delta_str = f"+{stats['delta_km']}" if stats['delta_km'] > 0 else "-"

            table_data.append({
                "Data": r.date,
                "Km Totali": r.total_km,
                "Delta Km": delta_str,
                "Prezzo (€/L)": f"{r.price_per_liter:.3f}",
                "Spesa (€)": f"{r.total_cost:.2f}",
                "Litri": f"{r.liters:.2f}",
                "Km/L": kml_str,
                "Pieno": "✅" if r.is_full_tank else "❌"
            })
        
        df_display = pd.DataFrame(table_data)
        st.dataframe(df_display, width="stretch", hide_index=True)
    else:
        st.info("Nessun dato.")

def render_maintenance_page():
    """
    Form per inserimento Manutenzioni.
    """
    st.header("🔧 Registro Manutenzioni")

    with st.form("maintenance_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            m_date = st.date_input("Data Intervento", value=date.today())
            m_km = st.number_input("Chilometri al momento", min_value=0, step=1, format="%d")
        
        with col2:
            m_type = st.selectbox("Tipo Intervento", ["Tagliando", "Gomme", "Batteria", "Revisione", "Bollo", "Altro"])
            m_cost = st.number_input("Costo (€)", min_value=0.0, step=1.0, format="%.2f")

        m_desc = st.text_area("Dettagli Intervento")
        
        submitted = st.form_submit_button("Salva Manutenzione")

        if submitted:
            db = next(get_db())
            try:
                crud.create_maintenance(
                    db=db,
                    date_obj=m_date,
                    total_km=m_km,
                    expense_type=m_type,
                    cost=m_cost,
                    description=m_desc
                )
                st.success("✅ Intervento registrato correttamente!")
            except Exception as e:
                st.error(f"Errore: {e}")
            finally:
                db.close()


def render_settings_page():
    st.header("⚙️ Gestione Dati Avanzata")

    tab_import, tab_manage = st.tabs(["📥 Importazione (Staging Area)", "📝 Modifica Storico"])

    # --- TAB 1: IMPORTAZIONE CON STAGING ---
    with tab_import:
        st.subheader("1. Caricamento File")
        uploaded_file = st.file_uploader("Carica Excel/CSV", type=["csv", "xlsx"])
        
        if uploaded_file:
            # Step A: Parsing in memoria
            if uploaded_file.name.endswith('.csv'):
                raw_df = pd.read_csv(uploaded_file)
            else:
                raw_df = pd.read_excel(uploaded_file)
            
            # Usiamo il service per pulire i dati (ma non salvare)
            # Nota: qui dovresti chiamare la funzione parse_upload_file definita sopra
            # Per ora simuliamo un DF pulito se non hai aggiornato il service
            st.info("File letto. Verifica i dati nella tabella qui sotto PRIMA di confermare.")
            
            # Step B: Tabella Editabile (STAGING AREA)
            # L'utente può correggere i numeri qui se l'OCR ha sbagliato
            edited_df = st.data_editor(
                raw_df, 
                num_rows="dynamic", # Permette di aggiungere/togliere righe
                use_container_width=True,
                key="staging_editor"
            )

            # Step C: Conferma e Scrittura
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("✅ CONFERMA IMPORTAZIONE", type="primary"):
                    db = next(get_db())
                    progress_bar = st.progress(0)
                    
                    try:
                        # Iteriamo sul DataFrame MODIFICATO dall'utente
                        for i, row in edited_df.iterrows():
                            crud.create_refueling(
                                db=db,
                                date_obj=pd.to_datetime(row['Data']).date(), # Adatta in base alle tue colonne
                                total_km=int(row['Km']),
                                price_per_liter=float(row['Prezzo']),
                                total_cost=float(row['Costo']),
                                liters=float(row['Litri']), # O ricalcola
                                is_full_tank=True, # O leggi dal df
                                notes="Import Massivo"
                            )
                            progress_bar.progress((i + 1) / len(edited_df))
                        
                        st.success("Importazione completata con successo!")
                        st.cache_data.clear()
                        
                    except Exception as e:
                        st.error(f"Errore durante il salvataggio: {e}")
                    finally:
                        db.close()

    # --- TAB 2: GESTIONE RIGIDA (Modifica/Delete Last) ---
    with tab_manage:
        db = next(get_db())
        
        # A. Sezione Cancellazione (Solo Ultimo Record)
        last_record = crud.get_last_refueling(db)
        if last_record:
            st.subheader("Rimuovi Ultimo inserimento")
            st.write(f"L'ultimo record inserito è del **{last_record.date}** ({last_record.total_km} Km).")
            if st.button("🗑️ Elimina solo questo record"):
                crud.delete_refueling(db, last_record.id)
                st.success("Ultimo record eliminato. Lo storico precedente è intatto.")
                st.cache_data.clear()
                st.rerun()
        else:
            st.info("Database vuoto.")

        st.divider()

        # B. Sezione Modifica (Con Validazione Sandwich)
        st.subheader("Modifica Puntuale")
        records = crud.get_all_refuelings(db)
        # ... Qui mostri la tabella, l'utente seleziona un ID ...
        
        # Immagina che l'utente abbia selezionato l'ID 5 per modificarlo
        # ID_SELEZIONATO = ... (codice selezione)
        
        # LOGICA DI VALIDAZIONE
        # if st.button("Salva Modifiche"):
        #    neighbors = crud.get_neighbors(db, data_modificata)
        #    if neighbors['prev'] and nuovi_km <= neighbors['prev'].total_km:
        #        st.error(f"Errore: I km ({nuovi_km}) devono essere maggiori del precedente ({neighbors['prev'].total_km})")
        #    elif neighbors['next'] and nuovi_km >= neighbors['next'].total_km:
        #        st.error(f"Errore: I km ({nuovi_km}) devono essere minori del successivo ({neighbors['next'].total_km})")
        #    else:
        #        crud.update_refueling(...)
        #        st.success("Modifica salvata e coerente!")
        
        db.close()
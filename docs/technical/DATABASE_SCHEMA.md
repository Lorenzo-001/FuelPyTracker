<div align="justify">

# 🗃️ Modello Dati & Schema Database — V2.0

> **Struttura delle tabelle, relazioni e isolamento dei dati per ambienti SQLite e PostgreSQL.**

---

## 📐 Organizzazione Generale dei Dati

Questo documento descrive la struttura del database relazionale di FuelPyTracker V2, definita tramite i modelli ORM di **SQLAlchemy** (`backend/src/database/models.py`).  
Lo schema è progettato per funzionare senza modifiche sia su **SQLite** (in locale o dentro un container Docker) sia su **PostgreSQL / Supabase** (in ambiente cloud multi-utente).

Tutte le tabelle applicative fanno riferimento all'identificativo dell'utente (`user_id`), garantendo che ogni profilo abbia il proprio storico isolato di rifornimenti, interventi di manutenzione, promemoria e impostazioni.

---

## 🏛️ Descrizione delle Tabelle Principali

### 1. Tabella `refuelings` (Rifornimenti)
Memorizza ogni sosta al distributore registrata dall'utente.
- **Campi principali:** `id`, `user_id`, `date` (data del rifornimento), `total_km` (lettura del contachilometri), `price_per_liter` (€/L), `total_cost` (spesa totale in €), `liters` (litri erogati), `is_full_tank` (indica se è stato fatto il pieno completo) e `notes` (eventuali note o nome stazione di servizio).
- **Logica di calcolo:** I consumi in `km/L` e i chilometri percorsi dall'ultimo pieno (`delta_km`) vengono calcolati dinamicamente dal backend confrontando i record con `is_full_tank = True` e sommando eventuali rifornimenti parziali intermedi.

### 2. Tabella `maintenances` (Manutenzioni)
Registra gli interventi tecnici ordinari e straordinari effettuati sul veicolo.
- **Campi principali:** `id`, `user_id`, `date` (data dell'intervento), `total_km` (chilometri al momento del lavoro), `expense_type` (categoria: Tagliando, Freni, Gomme, Revisione, ecc.), `cost` (spesa in €), `description` (dettaglio lavori eseguiti).
- **Gestione scadenze:** Include due campi opzionali per programmare il prossimo intervento: `expiry_km` (chilometraggio limite) ed `expiry_date` (data di scadenza).

### 3. Tabella `reminders` (Promemoria Periodici)
Gestisce i controlli ricorrenti di routine (pressione gomme, controllo livello olio, liquidi).
- **Campi principali:** `id`, `user_id`, `title` (nome del controllo), `frequency_km` (ogni quanti chilometri ripeterlo), `frequency_days` (ogni quanti giorni ripeterlo), `last_km_check` e `last_date_check` (chilometri e data dell'ultima verifica effettuata), `is_active` e `notes`.
- **Calcolo avanzamento:** Confrontando l'ultima verifica con i chilometri e la data attuali del veicolo, il sistema determina se il controllo è in regola, in scadenza o scaduto.

### 4. Tabella `reminder_history` (Storico Controlli Eseguiti)
Conserva il registro cronologico di tutte le volte in cui un promemoria viene segnato come completato.
- **Campi principali:** `id`, `reminder_id` (chiave esterna collegata a `reminders.id` con cancellazione a cascata), `user_id`, `date_checked`, `km_checked` e `notes`.
- **Ruolo:** Quando l'utente preme *"Segna come eseguito"*, viene aggiunta una riga in questa tabella e vengono aggiornati i riferimenti dell'ultimo controllo nella tabella padre `reminders`.

### 5. Tabella `settings` (Impostazioni e Profilo Veicolo)
Archivia le preferenze personalizzate e i dati identificativi del veicolo, con una riga dedicata per ciascun utente (`user_id` univoco).
- **Anagrafica veicolo:** `vehicle_name` (marca/modello), `vehicle_plate` (targa), `vehicle_fuel_type` (Benzina, Diesel, GPL, Metano, Ibrida, Elettrica).
- **Soglie e preferenze:** limiti di avviso spesa (`max_total_cost`, `max_accumulated_partial_cost`, `price_fluctuation_cents`), soglie di controllo per l'importazione Excel (`import_kml_min`, `import_kml_max`, `import_kml_error`, `import_kmd_max`), liste personalizzate in formato JSON per le categorie (`maintenance_types`, `reminder_types`) e preferenze per le note generate dall'OCR (`ocr_add_station_to_notes`, `ocr_add_liters_to_notes`).

---

## ⚡ Indicizzazione e Prestazioni

Per mantenere veloci le letture e i calcoli statistici anche con uno storico di diversi anni:
- Tutte le tabelle hanno un indice sulla colonna `user_id` e sulla chiave primaria `id`.
- Le interrogazioni filtrano sempre a monte per `user_id` e ordinano i dati per data e chilometraggio (`date`, `total_km`), consentendo un recupero rapido sia per i grafici della Dashboard sia per il controllo di coerenza dei chilometri durante l'inserimento.

---

## 🛡️ Isolamento Dati con Row Level Security (RLS)

Quando l'applicazione è collegata a **PostgreSQL su Supabase**, la separazione dei dati tra utenti diversi è garantita su due livelli:
1. **Livello Applicativo (Backend):** Ogni operazione SQL eseguita dai servizi Python include obbligatoriamente il filtro `user_id == current_user_id`.
2. **Livello Database (RLS):** Sulle tabelle PostgreSQL sono attive regole *Row Level Security* che consentono la lettura o la scrittura dei record solo quando il valore di `user_id` coincide con l'identificativo dell'utente autenticato (`auth.uid() = user_id`).

</div>

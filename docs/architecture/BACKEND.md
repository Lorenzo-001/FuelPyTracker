<div align="justify">

# ⚙️ Architettura Backend — Motore FastAPI

> **Struttura tecnica del server Python: organizzazione delle API, accesso al database e servizi di calcolo e analisi.**

---

## 🏗️ Struttura e Principi del Backend

Questo documento illustra l'organizzazione interna del backend di FuelPyTracker V2, sviluppato in **Python** con il framework **FastAPI**.  
Il server espone tutte le funzionalità tramite API REST, separando in modo ordinato la ricezione delle richieste HTTP, la logica di calcolo e il salvataggio dei dati su database.

### Principi di Progettazione
1. **Separazione dei Compiti:** I router HTTP (`src/api/routers/`) si occupano solo di ricevere le richieste, verificare l'utente e restituire le risposte; tutte le regole di calcolo e di elaborazione risiedono nei moduli di servizio (`src/services/`).
2. **Controllo Preventivo dei Dati:** Ogni richiesta in ingresso e risposta in uscita passa attraverso schemi **Pydantic** (`src/api/schemas/`), che bloccano subito dati mancanti o malformati prima ancora di interrogare il database.
3. **Gestione Isolata dei Servizi Esterni:** Le integrazioni esterne (come la lettura degli scontrini tramite OpenAI o l'autenticazione cloud con Supabase) includono controlli di errore dedicati e modalità simulate per lavorare anche offline o in ambiente dimostrativo.

---

## 🧩 Moduli e Router API

Le API sono suddivise in moduli indipendenti, ciascuno dedicato a un'area specifica dell'applicazione:

| Modulo API | Responsabilità Principale | Funzioni Chiave |
| :--- | :--- | :--- |
| **Auth** (`/api/auth`) | Accesso, registrazione e sessione utente | Verifica credenziali, emissione e controllo dei token JWT, recupero password e gestione del profilo demo. |
| **Dashboard** (`/api/dashboard`) | Riepiloghi statistici, grafici e simulazioni | Calcolo degli indicatori generali (spesa, consumo medio, salute auto), serie storiche per i grafici e calcolatore costi di viaggio. |
| **Rifornimenti** (`/api/fuel`) | Gestione pieni, controllo chilometri e OCR | Operazioni di lettura/scrittura rifornimenti, verifica preventiva dei chilometri (`/validate`) e scansione scontrini (`/ocr`). |
| **Manutenzioni** (`/api/maintenance`) | Storico interventi di officina e scadenze | Registrazione spese per categoria, filtri per anno e calcolo delle scadenze future (`/deadlines`). |
| **Promemoria** (`/api/reminders`) | Controlli periodici di routine | Monitoraggio stato avanzamento (in regola, in scadenza, scaduto), registrazione esecuzione (`/complete`) e storico controlli. |
| **Report e Dati** (`/api/reports`) | Esportazione e importazione archivio | Creazione libretto PDF, esportazione Excel multi-foglio, download modello vuoto e importazione guidata in due fasi. |
| **Impostazioni** (`/api/settings`) | Configurazione veicolo e preferenze | Salvataggio dati del veicolo, soglie di avviso, preferenze note OCR e gestione delle categorie personalizzate. |
| **Health Check** (`/health`) | Diagnostica e stato del servizio | Verifica immediata dell'operatività del server e della connessione attiva con il database. |

---

## 🗄️ Accesso ai Dati e Database

Il livello di persistenza (`src/database/`) utilizza **SQLAlchemy** per astrarre il database relazionale sottostante:
- **Compatibilità SQLite e PostgreSQL:** Le stesse query operano in modo identico sia su file locale **SQLite** (per sviluppo o installazioni autonome) sia su **PostgreSQL / Supabase** in cloud.
- **Sessioni Sicure per Richiesta:** Ogni chiamata API riceve una sessione database dedicata che viene chiusa automaticamente al termine dell'operazione, evitando connessioni lasciate aperte.
- **Isolamento Multi-Utente:** Tutte le tabelle includono la colonna `user_id`. Oltre al filtro applicato da ogni query del backend, in ambiente PostgreSQL su Supabase è attivo l'isolamento *Row Level Security (RLS)* direttamente sul database.

---

## 🛠️ Servizi Fondamentali di Backend

Il cuore logico dell'applicazione risiede nella cartella `backend/src/services/`, organizzata nei seguenti servizi principali:

### 1. Calcolo Consumi e Controllo Chilometrico (`services/business/`)
- **Algoritmo *Full-to-Full* (`calculations.py`):** Calcola il consumo reale (km/L) solo quando viene registrato un pieno completo, sommando automaticamente i litri di eventuali rifornimenti parziali effettuati nel frattempo rispetto al pieno precedente.
- **Validazione Cronologica (`fuel_logic.py`):** Prima di salvare o modificare un rifornimento, confronta la data e i chilometri inseriti con il record precedente e con quello successivo, impedendo l'inserimento di letture incoerenti del contachilometri.
- **Analisi e Simulazione Viaggio (`analysis.py`):** Elabora le serie temporali per i grafici della Dashboard e calcola i preventivi di spesa e carburante per il simulatore di viaggio.

### 2. Manutenzione Predittiva e Salute Veicolo (`services/business/`)
- **Stima delle Scadenze (`prediction.py`):** Analizza i rifornimenti storici per ricavare i chilometri percorsi mediamente ogni giorno dall'utente; usa questo ritmo per stimare la data in cui verranno raggiunte le prossime scadenze chilometriche d'officina.
- **Indice di Salute (`gamification.py`):** Calcola il punteggio *Car Health Score* (da 0 a 100%) valutando la presenza di manutenzioni o controlli periodici in scadenza o scaduti.

### 3. Importazione ed Esportazione Dati (`services/data/`)
- **Motore di Importazione a Due Fasi (`importers/`):** Legge file Excel (`.xlsx`) e CSV riconoscendo automaticamente i fogli *Rifornimenti* e *Manutenzioni*, confronta ogni riga con il database per individuare nuovi inserimenti, modifiche, duplicati o valori fuori scala, e permette di rivalidare le righe corrette dall'utente prima del salvataggio definitivo.
- **Esportazione Excel (`exporters/reports.py`, `templates.py`):** Genera file Excel formattati su più fogli con tutti i dati storici dell'utente oppure il modello vuoto pronto da compilare.
- **Generatore Libretto PDF (`exporters/pdf_generator.py`):** Costruisce con `FPDF` il Libretto di Manutenzione in formato PDF stampabile, completo di intestazione del veicolo, tabella cronologica degli interventi e riepilogo dei costi.

### 4. Lettura Ottica Scontrini con AI (`services/ocr/`)
- **Analisi Immagini (`engine.py`, `pipeline.py`):** Codifica temporaneamente in memoria la foto dello scontrino e la invia al modello **OpenAI GPT-4o Vision** per estrarre in formato JSON data, spesa totale, prezzo al litro, litri erogati e nome del distributore.
- **Ricalcolo Matematico di Verifica:** Se sullo scontrino uno dei tre valori numerici (totale, prezzo/L, litri) risulta sbiadito o mancante, il servizio lo ricava matematicamente dagli altri due valori letti.

### 5. Autenticazione e Modalità Demo (`services/auth/`, `demo.py`)
- **Gestione Identità (`auth_service.py`):** Si interfaccia con Supabase Auth per login, registrazione e recupero password, validando i token JWT nelle chiamate protette.
- **Protezione Modalità Demo (`demo.py`):** Quando è attiva la variabile `DEMO_MODE=True`, blocca qualsiasi modifica o cancellazione sui dati dimostrativi e sostituisce le chiamate esterne verso OpenAI con risposte simulate realistiche.

</div>

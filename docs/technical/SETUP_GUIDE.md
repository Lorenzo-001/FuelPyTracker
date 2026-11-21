<div align="justify">

# 🛠️ Guida all'Installazione e Configurazione — V2.0

> **Istruzioni pratiche per avviare FuelPyTracker in locale, tramite Docker Compose o in ambiente cloud.**

---

## 📋 Requisiti di Sistema

A seconda della modalità di avvio scelta:

- **Con Docker (Consigliato per un avvio immediato):** Docker e Docker Compose installati.
- **Sviluppo Locale (Senza Docker):**
  - **Python 3.11+** con `pip`
  - **Node.js 20+** con `npm`
  - **Git**

---

## 🚀 Metodo 1: Avvio Rapido con Docker Compose (Consigliato)

È il modo più veloce per far partire l'intera applicazione (Frontend + Backend + Database locale) con un solo comando:

1. **Clona il repository:**
   ```bash
   git clone https://github.com/Lorenzo-001/FuelPyTracker.git
   cd FuelPyTracker
   ```

2. **Configura il file delle variabili d'ambiente:**
   Copia il modello di esempio nella cartella del backend:
   ```bash
   # Su Linux / macOS:
   cp backend/.env.example backend/.env

   # Su Windows (PowerShell):
   Copy-Item backend/.env.example backend/.env
   ```

3. **Avvia i container:**
   ```bash
   docker compose up --build -d
   ```

4. **Apri l'applicazione nel browser:**
   - **Interfaccia Web:** `http://localhost:80` (oppure `http://localhost:3000`)
   - **Documentazione API Interattiva (Swagger):** `http://localhost:8000/docs`
   - **Controllo Stato Server (Health Check):** `http://localhost:8000/health`

Per fermare i servizi:
```bash
docker compose down
```

---

## 💻 Metodo 2: Avvio Locale per Sviluppo (Frontend + Backend)

Ideale se vuoi modificare il codice sorgente vedendo le modifiche applicate in tempo reale.

### 1. Avvio del Backend (FastAPI)
Apri un terminale nella cartella principale del progetto:

```bash
# Crea e attiva l'ambiente virtuale Python
python -m venv venv
# Su Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Su Linux/macOS:
source venv/bin/activate

# Installa le dipendenze del backend
pip install -r backend/requirements.txt

# Copia la configurazione di esempio (se non l'hai già fatto)
cp backend/.env.example backend/.env

# Avvia il server FastAPI sulla porta 8000
uvicorn backend.src.api.server:app --reload --port 8000
```
Il backend risponderà all'indirizzo `http://localhost:8000` (con documentazione su `http://localhost:8000/docs`).

### 2. Avvio del Frontend (React + Vite)
Apri un **secondo terminale** e spostati nella cartella `frontend`:

```bash
cd frontend

# Installa i pacchetti Node.js
npm install

# Avvia il server di sviluppo Vite
npm run dev
```
L'interfaccia web sarà raggiungibile su `http://localhost:5173` e inoltrerà automaticamente tutte le richieste `/api` al backend sulla porta `8000`.

---

## ⚙️ Configurazione delle Variabili d'Ambiente (`backend/.env`)

Il file `backend/.env` controlla il funzionamento del server. Ecco le impostazioni principali:

### 1. Scelta del Database
- **Modalità Locale con SQLite (Predefinita per test e uso locale):**
  ```env
  LOCAL_SQLITE=True
  ```
  *Non richiede alcuna configurazione esterna: il database viene creato automaticamente nel file `data/fuel_tracker.db`.*

- **Modalità Cloud con PostgreSQL / Supabase:**
  ```env
  LOCAL_SQLITE=False
  DATABASE_URL=postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
  SUPABASE_URL=https://tuo-progetto.supabase.co
  SUPABASE_KEY=tua-chiave-anon-supabase
  SUPABASE_JWT_SECRET=tuo-segreto-jwt-supabase
  ```

### 2. Scansione Scontrini con OpenAI (Smart OCR)
La lettura automatica delle ricevute di rifornimento utilizza il modello **OpenAI GPT-4o Vision** (servizio API a consumo basato su token):
```env
OPENAI_API_KEY=sk-proj-...
```
*Se la chiave `OPENAI_API_KEY` non viene impostata (oppure se è attiva la modalità demo), la funzione di scansione non genera errori ma risponde con dati simulati di prova.*

### 3. Modalità Dimostrativa
Per avviare l'applicazione in modalità dimostrativa (sola lettura, con utente di prova pre-autenticato e scansione OCR simulata):
```env
DEMO_MODE=True   # Imposta False per l'utilizzo reale con salvataggio dati
```

---

## 🩺 Verifica Rapida e Test Automatici

Dopo l'avvio puoi verificare che tutto funzioni correttamente:
- **Controllo connessione:** apri `http://localhost:8000/health` nel browser per verificare che il server risponda con `"status": "ok"` e `"database": "connected"`.
- **Esecuzione test backend (Pytest):**
  ```bash
  pytest backend/tests
  ```
- **Controllo codice e compilazione frontend:**
  ```bash
  cd frontend
  npm run lint
  npm run build
  ```

</div>

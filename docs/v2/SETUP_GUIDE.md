# 🛠️ SETUP_GUIDE.md — FuelPyTracker v2.0 (Backend API)

> **Destinatari:** Developer Onboarding, Contributor, QA & Tester.  
> Questa guida illustra come configurare, avviare e collaudare in locale il **Backend FastAPI** di FuelPyTracker v2.0, sia in modalità Sandbox/Demo che collegato al database PostgreSQL Supabase reale.

---

## 📋 Indice

1. [Prerequisiti di Sistema](#1-prerequisiti-di-sistema)
2. [Configurazione dell'Ambiente Virtuale](#2-configurazione-dellambiente-virtuale)
3. [Configurazione delle Variabili (.env)](#3-configurazione-delle-variabili-env)
4. [Avvio del Server API (FastAPI & Uvicorn)](#4-avvio-del-server-api-fastapi--uvicorn)
5. [Collaudo tramite Swagger UI](#5-collaudo-tramite-swagger-ui)
6. [Esecuzione dei Test Unitari (pytest)](#6-esecuzione-dei-test-unitari-pytest)
7. [Esecuzione Parallela con Streamlit V1](#7-esecuzione-parallela-con-streamlit-v1)

---

## 1. Prerequisiti di Sistema

Assicurati di disporre dei seguenti requisiti minimi:
- **Python 3.11+** installato e configurato nel `PATH`.
- **Git** per la gestione del versionamento.

Verifica la versione nel tuo terminale:
```bash
python --version
# Output atteso: Python 3.11.x o superiore
```

---

## 2. Configurazione dell'Ambiente Virtuale

Dalla cartella principale del repository (`FuelPyTracker`):

1. **Crea l'ambiente virtuale (`venv`):**
   ```powershell
   python -m venv venv
   ```

2. **Attiva l'ambiente:**
   - Su Windows (PowerShell):
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - Su Linux / macOS:
     ```bash
     source venv/bin/activate
     ```

3. **Installa le dipendenze del Backend:**
   ```powershell
   pip install -r backend/requirements.txt
   ```

---

## 3. Configurazione delle Variabili (.env)

Il backend carica le variabili d'ambiente cercando prima in `backend/.env` e poi nella radice.

### Modalità A: Zero-Cloud Bootstrap (SQLite Locale)
Non richiede alcun account Supabase o OpenAI:
1. Copia il template di esempio:
   ```powershell
   Copy-Item backend/.env.example backend/.env
   ```
2. Assicurati che nel file `backend/.env` siano presenti:
   ```ini
   LOCAL_SQLITE=True
   DEMO_MODE=True
   DEMO_USER_ID=00000000-0000-4000-8000-000000000001
   DEMO_USER_EMAIL=demo@local.fuelpytracker
   ```

### Modalità B: Produzione / Cloud Supabase
Se intendi connetterti al database reale:
1. Inserisci la stringa di connessione PostgreSQL:
   ```ini
   DATABASE_URL=postgresql://postgres.[REF]:[PASS]@aws-1-eu-central-1.pooler.supabase.com:6543/postgres
   SUPABASE_URL=https://[REF].supabase.co
   SUPABASE_KEY=eyJhbGciOi...
   OPENAI_API_KEY=sk-proj-...
   LOCAL_SQLITE=False
   DEMO_MODE=False
   ```

---

## 4. Avvio del Server API (FastAPI & Uvicorn)

Dalla cartella principale del repository, avvia il server di sviluppo con auto-reload abilitato:

```powershell
.\venv\Scripts\uvicorn backend.src.api.server:app --host 127.0.0.1 --port 8000 --reload
```

Output atteso nel terminale:
```text
INFO:     Will watch for changes in these directories: ['C:\\Progetti\\git\\FuelPyTracker']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxx] using StatReload
INFO:     Started server process [yyyy]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

---

## 5. Collaudo tramite Swagger UI

Una volta avviato il server, apri il browser su:

👉 **[http://localhost:8000/docs](http://localhost:8000/docs)** (oppure direttamente [http://localhost:8000](http://localhost:8000))

### Cosa puoi testare subito:
1. **`GET /health`**: Verifica che il server risponda con `{"status": "ok", "version": "2.0.0"}`.
2. **`POST /api/auth/login`**:
   - In modalità Demo puoi inserire qualsiasi email (es. `demo@fuelpytracker.com`) e password: riceverai immediatamente un token Bearer e il profilo utente `DEMO_USER`.
3. **`GET /api/auth/me`**:
   - Inserisci il token ricevuto nel pulsante **Authorize 🔓** in alto a destra su Swagger: l'endpoint risponderà con i dettagli anagrafici del profilo.

---

## 6. Esecuzione dei Test Unitari (pytest)

Per eseguire l'intera suite di collaudo automatica del repository:

```powershell
.\venv\Scripts\pytest backend/tests
```

Per testare esclusivamente i componenti e i router della nuova API:
```powershell
.\venv\Scripts\pytest backend/tests/unit/api
```

---

## 7. Esecuzione Parallela con Streamlit V1

Durante la fase transitoria di sviluppo della V2, l'applicazione Streamlit v1.1.0 può girare contemporaneamente in un terminale separato:

```powershell
.\venv\Scripts\streamlit run backend/main.py
```
- **Streamlit V1 UI:** `http://localhost:8501`
- **FastAPI V2 API & Swagger:** `http://localhost:8000`

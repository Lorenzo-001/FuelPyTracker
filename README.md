<div align="center">

# ⛽ FuelPyTracker

### L'hub definitivo per la gestione **data-driven** del tuo veicolo

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/downloads/release/python-3110/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Supabase](https://img.shields.io/badge/Supabase-Backend-3ECF8E?style=for-the-badge&logo=supabase&logoColor=white)](https://supabase.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)
[![Release](https://img.shields.io/badge/Release-v1.0.0-brightgreen?style=for-the-badge)](https://github.com/Lorenzo-001/FuelPyTracker/releases/tag/v1.0.0)

</div>

---

## 🚀 Prova la Demo Live — Nessuna Registrazione Richiesta

<div align="center">

### **[→ Apri la Demo su Streamlit Cloud ←](https://fuelpytracker-demo.streamlit.app/)**

</div>

> La demo è una **vetrina Read-Only** dell'applicazione. Il login non è necessario né disponibile: l'app si apre direttamente con un utente dimostrativo preconfigurato. I pulsanti di **salvataggio ed eliminazione sono disabilitati** e tutti i dati visualizzati sono simulati. È possibile esplorare ogni funzionalità liberamente e in totale sicurezza.

<div align="center">

| Schermata di Autenticazione | Dashboard Principale |
|:---:|:---:|
| ![Auth](assets/auth_preview.png) | ![Dashboard](assets/dashboard_preview.png) |

</div>

---

## ✨ Caratteristiche Principali

- 📊 **Dashboard e Statistiche** — Monitoraggio in real-time dei **consumi in km/L**, dei **trend di spesa mensile** e di tutte le statistiche dei rifornimenti con grafici interattivi.
- 🔧 **Gestione Manutenzioni e Scadenziario** — Nessuna scadenza dimenticata. Gestione di **bollo, assicurazione, revisione e tagliandi** con un'unica vista e alert preventivi.
- 📥 **Import & Export** — Caricamento di storici di rifornimento via **CSV/Excel** con validazione intelligente delle anomalie; esportazione di report **Excel** e **PDF** in un click.
- 🔒 **Dati Privati e al Sicuro** — La **Row Level Security** di Supabase garantisce che ogni utente veda esclusivamente i propri dati, direttamente a livello di database — non solo nel codice applicativo.
- 🤖 **Modulo OCR con IA** *(opzionale)* — Integrazione premium con **OpenAI GPT-4o Vision** per estrarre automaticamente litri, importo e stazione di servizio da una foto dello scontrino. Il modulo è completamente opzionale: l'app funziona al 100% anche senza una chiave API OpenAI.

---

## 🛠️ Stack Tecnologico

| Componente | Tecnologia | Perché questa scelta |
|---|---|---|
| **Frontend & App** | [Streamlit](https://streamlit.io/) | UI reattiva in puro Python, senza HTML/JS |
| **Auth & Database** | [Supabase](https://supabase.com/) | PostgreSQL managed, Auth e Row Level Security integrati |
| **Computer Vision** | [OpenAI GPT-4o](https://openai.com/) | Modello multimodale per l'estrazione dati da immagini reali |
| **Containerizzazione** | [Docker](https://www.docker.com/) | Deploy riproducibile in un solo comando su qualsiasi macchina |
| **ORM & Query** | [SQLAlchemy](https://www.sqlalchemy.org/) | Astrazione del layer dati con gestione sicura delle sessioni |

### 🏷️ Come funziona la Demo Pubblica

Per la demo pubblica, l'app utilizza una variabile d'ambiente `DEMO_MODE=True` che fa tre cose semplici:

1. **Inietta un utente fittizio** in sessione — non è necessario un vero account Supabase.
2. **Disabilita tutte le scritture** sul database — nessun dato reale può essere modificato.
3. **Sostituisce il modulo OpenAI** con un mock locale — zero chiamate API a pagamento.

Il risultato è un'applicazione identica nella UI ma completamente sicura da esporre pubblicamente.


## ⚡ Quick Start — Sviluppo Locale con Docker

### Prerequisiti

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installato e in esecuzione
- [Git](https://git-scm.com/)
- Un account [Supabase](https://supabase.com/) gratuito

> Per una guida dettagliata all'installazione manuale (senza Docker) e alla configurazione completa del database Supabase, è possibile consultare la **[📚 Documentazione](#-documentazione)** qui sotto.

---

#### Step 1 — Clona il Repository

```bash
git clone https://github.com/Lorenzo-001/FuelPyTracker.git
cd FuelPyTracker
```

#### Step 2 — Configura le Variabili d'Ambiente

**a) File `.env`** — Copia il template:

```bash
cp .env.example .env
```

Poi apri il file `.env` e imposta la modalità demo (lascia `False` per un'installazione standard):

```
DEMO_MODE=False
```

**b) File `.streamlit/secrets.toml`** — Questo è il file principale con le credenziali. Copia il template:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Poi apri `.streamlit/secrets.toml` e compila le sezioni obbligatorie:

```toml
[database]
# Stringa di connessione PostgreSQL diretta — usata da SQLAlchemy per le query.
# Disponibile in Supabase Dashboard → Project Settings → Database → Connection string (Transaction mode, porta 6543)
url = "postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"

[supabase]
# Credenziali API — usate dal client Supabase per l'autenticazione degli utenti.
# Disponibili in Supabase Dashboard → Project Settings → API
url = "https://[PROJECT_REF].supabase.co"
key = "your-anon-public-key"
redirect_url = "http://localhost:8501"

[openai]
# Opzionale — solo per utilizzare il modulo OCR di scansione scontrini
api_key = "sk-proj-..."
```

> ⚠️ Il progetto usa **due connessioni distinte a Supabase**: SQLAlchemy si connette direttamente a PostgreSQL tramite la stringa `[database] url` per tutte le operazioni CRUD, mentre il client Supabase usa `[supabase] url` e `key` esclusivamente per l'autenticazione degli utenti. Entrambe le sezioni sono obbligatorie.

> Il file `secrets.toml` è già escluso dal `.gitignore`. Non committarli mai con le credenziali reali.

#### Step 3 — Avvia l'App

```bash
docker compose up -d
```

Docker eseguirà il build dell'immagine e avvierà il container in background. Al termine apparirà:

```
✔ Container FuelPyTracker  Started
```

#### Step 4 — Apri il Browser

```
http://localhost:8501
```

Per fermare il container: `docker compose down`

Per seguire i log in tempo reale (utile al primo avvio per diagnosticare eventuali errori): `docker compose logs -f`

---

## 📚 Documentazione

Una documentazione più approfondita è disponibile nella cartella [`docs/`](docs/):

| Documento | Contenuto |
|---|---|
| [`SETUP_GUIDE.md`](docs/SETUP_GUIDE.md) | Manuale dettagliato passo-passo per l'installazione manuale (senza Docker), i requisiti di sistema e la configurazione completa del database Supabase (schema, RLS, variabili d'ambiente). |
| [`ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Documentazione funzionale e tecnica unificata: struttura dei moduli, flussi dati, pattern architetturali e decisioni di design. |

---

## 📁 Struttura del Progetto

```
FuelPyTracker/
│
├── main.py                     # Entry point — routing e gestione sessione
├── Dockerfile                  # Immagine Python 3.11-slim con healthcheck
├── docker-compose.yml          # Orchestrazione container + mount secrets
├── config.toml                 # Configurazione centralizzata (soglie, costanti)
├── requirements.txt
│
├── assets/                     # Risorse statiche (logo, screenshot)
│
├── src/
│   ├── config.py               # Loader TOML con fallback e logging
│   ├── demo.py                 # Logica Demo Mode — inject utente fittizio
│   │
│   ├── database/               # Layer dati
│   │   ├── models.py           # Definizione tabelle SQLAlchemy (ORM)
│   │   ├── crud.py             # Operazioni CRUD (Read/Write con RLS)
│   │   └── core.py             # Connessione e factory della sessione DB
│   │
│   ├── services/               # Logica di business (separata dalla UI)
│   │   ├── ocr/                # Pipeline OCR: engine GPT-4o + mock Demo
│   │   │   ├── engine.py       # Integrazione OpenAI Vision API
│   │   │   └── pipeline.py     # Orchestratore (reale o mock)
│   │   ├── auth/               # Wrapper autenticazione Supabase
│   │   ├── business/           # Regole di business (validazione, calcoli)
│   │   └── data/               # Trasformazione e aggregazione dati
│   │
│   └── ui/
│       └── components/         # Componenti Streamlit per feature area
│           ├── dashboard/      # KPI cards, grafici trend, trip calculator
│           ├── fuel/           # Form inserimento + lista rifornimenti
│           ├── maintenance/    # Scadenziario e report manutenzione
│           ├── profile/        # Gestione profilo utente e veicolo
│           ├── settings/       # Configurazioni applicazione
│           ├── sidebar.py      # Navigazione globale
│           └── startup_alerts.py # Banner alert all'avvio (es. DEMO_MODE)
│
├── tests/
│   └── unit/                   # Suite pytest per services e validazione
└── docs/                       # Documentazione estesa (Setup, Architettura)
```

---

## 🤝 Contribuire

Le **Pull Request** sono benvenute e incoraggiate! Per contribuire con un bug fix, una nuova funzionalità o un miglioramento alla documentazione, ecco come procedere:

1. **Fare il Fork** del repository tramite il pulsante in alto a destra su GitHub.
2. **Clonare** il proprio fork in locale e creare un branch dedicato con un nome descrittivo.
3. **Implementare** le modifiche, assicurandosi che i test esistenti continuino a passare.
4. **Aprire la Pull Request** su GitHub verso il branch `main` di questo repository, descrivendo chiaramente cosa fa e perché.

```bash
# 1. Fare il fork del repository e clonarlo in locale
git clone https://github.com/TUO_USERNAME/FuelPyTracker.git

# 2. Creare un branch descrittivo
git checkout -b feature/nome-della-feature

# 3. Committare le modifiche e fare il push
git commit -m "feat: descrizione della modifica"
git push origin feature/nome-della-feature

# 4. Aprire una Pull Request su GitHub verso il branch main
```

Per segnalare un bug o proporre una funzionalità, è possibile [**aprire una Issue**](https://github.com/Lorenzo-001/FuelPyTracker/issues) — ogni contributo è apprezzato.

> Assicurarsi che tutti i test passino prima di aprire una PR. Poiché il progetto gira in Docker, eseguire i test all'interno del container:
>
> ```bash
> docker compose exec fuel-tracker pytest tests/
> ```

---

## 📄 Licenza

Distribuito sotto licenza **MIT** — per i dettagli consultare il file [LICENSE](LICENSE).

La licenza MIT protegge l'autore da responsabilità legali per l'uso del codice da parte di terzi, garantendo al contempo la massima libertà di utilizzo, modifica e distribuzione.

---

<div align="center">

Creato con ❤️ da **[Lorenzo Polizzi](https://www.linkedin.com/in/lorenzo-polizzi-profile/)**

Se questo progetto è stato utile, lasciare una ⭐ su GitHub è molto apprezzato!

</div>

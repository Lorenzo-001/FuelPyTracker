<div align="justify">

# 🏛️ Panoramica Architetturale — FuelPyTracker V2.0

> **Architettura disaccoppiata client-server, progettata per separare l'interfaccia utente dalla logica di calcolo e garantire flessibilità di installazione sia in locale che in cloud.**

---

## 📐 Struttura Generale del Sistema

Questo documento offre una vista d'insieme su come è strutturato FuelPyTracker V2 e su come dialogano tra loro i vari livelli dell'applicazione.

A differenza della prima versione basata interamente su Streamlit, la versione 2.0 separa nettamente due componenti indipendenti:
- **Un'interfaccia web lato client (Frontend React):** si occupa della navigazione, dei grafici, della validazione immediata dei moduli e dell'adattamento visivo tra computer e smartphone.
- **Un servizio applicativo centrale (Backend FastAPI in Python):** espone le API REST, esegue tutti i calcoli sui consumi e sulle scadenze, genera i report PDF/Excel, gestisce l'analisi degli scontrini e governa il salvataggio dei dati sul database.

---

## 🔑 Caratteristiche Principali dell'Architettura

### 1. Separazione tra Interfaccia e Logica di Dominio
Il frontend e il backend comunicano esclusivamente tramite chiamate HTTP JSON documentate secondo lo standard **OpenAPI 3.1**.  
I dati inseriti dall'utente vengono controllati una prima volta nell'interfaccia per offrire un riscontro visivo immediato, e una seconda volta sul server tramite schemi **Pydantic** prima di essere salvati nel database, garantendo la coerenza dello storico (ad esempio sulla progressione dei chilometri).

### 2. Doppia Modalità di Database (Locale o Cloud)
Il livello di persistenza è basato su **SQLAlchemy** e può operare in due configurazioni senza alcuna modifica al codice:
- **Modalità Cloud Multi-Utente (PostgreSQL / Supabase):** pensata per l'accesso da più dispositivi sincronizzati in rete, con gestione delle identità utente e isolamento dei dati per singolo profilo.
- **Modalità Locale Autonoma (SQLite):** pensata per l'esecuzione su computer personale, server domestico (NAS, Raspberry Pi) o container Docker locale, salvando tutti i dati in un singolo file senza dipendere da database esterni.

### 3. Distribuzione e Servizi Infrastrutturali
L'applicazione è strutturata in moduli leggeri che possono essere distribuiti su infrastrutture cloud standard o eseguiti in self-hosting:
- **Frontend Web:** compilato come insieme di file statici, distribuibile su qualsiasi servizio di hosting web o CDN (come Vercel, Netlify o Nginx).
- **Backend API:** applicazione Python containerizzabile con Docker ed eseguibile su piattaforme PaaS (come Render, Fly.io o Railway) o su server dedicati.
- **Database e Autenticazione:** gestibili tramite istanza PostgreSQL su Supabase oppure localmente su SQLite.
- **Servizio OCR per Scontrini (OpenAI API):** la funzione di lettura automatica delle ricevute si appoggia alle API **OpenAI (modello GPT-4o Vision)** tramite chiave API configurabile a livello di ambiente, con tariffazione a consumo basata sui token utilizzati. In assenza di chiave o in modalità dimostrativa, il sistema utilizza un risponditore simulato che permette comunque di testare l'intero flusso applicativo.

### 4. Sicurezza dei Dati e Trattamento delle Immagini
- **Isolamento per Utente:** Ogni record (rifornimenti, manutenzioni, promemoria e impostazioni) è legato all'identificativo dell'utente autenticato (`user_id`). In ambiente PostgreSQL/Supabase questo isolamento è rinforzato anche a livello di database tramite regole *Row Level Security (RLS)*, impedendo qualsiasi accesso incrociato tra profili diversi.
- **Gestione delle Foto degli Scontrini:** Le immagini caricate per la scansione OCR non vengono salvate in modo permanente né sul disco del server né nel database di FuelPyTracker. Il file viene letto temporaneamente in memoria dal backend il tempo necessario per codificarlo e inviarlo tramite connessione cifrata alle API di OpenAI (GPT-4o) per l'estrazione dei dati testuali, dopodiché viene scartato.

</div>

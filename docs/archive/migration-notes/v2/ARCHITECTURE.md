<div align="justify">

# 📓 Note di Migrazione e Scelte Architetturali — FuelPyTracker V2.0

> **Dal prototipo monolitico in Streamlit a un'applicazione web moderna con FastAPI e React.**  
> Questo documento raccoglie in un'unica guida la storia tecnica della Versione 2.0: come avviare subito l'intero progetto, perché è stata ripensata l'architettura, come è stata gestita la transizione dalla V1 e quali compromessi tecnici sono stati scelti lungo il percorso.

---

## ⚡ 1. Quick Start Unificato (Frontend + Backend)

Prima di entrare nei dettagli progettuali, ecco come far partire l'intera applicazione (Frontend React + Backend FastAPI) in locale in un paio di minuti.  
Di base il progetto è preconfigurato per usare un database **SQLite locale** e la **modalità dimostrativa**, quindi puoi avviarlo subito senza dover creare account su Supabase o chiavi API su OpenAI.

### Opzione A: Avvio con un solo comando (Docker Compose)
Assicurati di avere Docker attivo, poi esegui dalla cartella principale del progetto:

```bash
# 1. Crea il file di configurazione partendo dal modello di esempio
cp backend/.env.example backend/.env

# 2. Costruisci e avvia i container (Backend + Frontend)
docker compose up --build -d
```

- **Applicazione Web (React):** [http://localhost:80](http://localhost:80) (oppure [http://localhost:3000](http://localhost:3000))
- **Documentazione API Interattiva (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Per fermare tutto:** `docker compose down`

### Opzione B: Avvio locale per sviluppo (Senza Docker)
Se vuoi lavorare sul codice con ricaricamento automatico delle modifiche, apri due terminali nella cartella del progetto:

**Terminale 1 — Backend (Python 3.11+ / FastAPI):**
```bash
python -m venv venv
# Su Windows: .\venv\Scripts\Activate.ps1  |  Su Linux/macOS: source venv/bin/activate
pip install -r backend/requirements.txt
cp backend/.env.example backend/.env
uvicorn backend.src.api.server:app --reload --port 8000
```

**Terminale 2 — Frontend (Node.js 20+ / React + Vite):**
```bash
cd frontend
npm install
npm run dev
```
Aprendo **[http://localhost:5173](http://localhost:5173)** vedrai l'interfaccia React collegata automaticamente al backend sulla porta `8000`.

---

## 🎯 2. Perché siamo passati alla Versione 2.0

La prima versione di FuelPyTracker (v1.0 – v1.1) era stata costruita interamente con **Streamlit**. È stata una scelta ottima per dare vita rapidamente al progetto e mettere a punto tutta la logica di calcolo: l'algoritmo *Full-to-Full* per i consumi reali, i controlli sui chilometri, la lettura degli scontrini tramite intelligenza artificiale e l'esportazione in PDF ed Excel.

Col passare dei mesi e con l'uso reale, però, i limiti strutturali di Streamlit sono diventati evidenti:
1. **Riesecuzione continua dello script:** In Streamlit ogni clic su un pulsante o su un filtro fa ripartire lo script Python dall'inizio alla fine. Questo rendeva la gestione dello stato sempre più intricata e introduceva piccoli ritardi a ogni interazione.
2. **Assenza di una vera navigazione web:** Non esistevano URL distinti per le varie sezioni (`/dashboard`, `/fuel`, `/maintenance`), né era possibile usare comodamente i tasti avanti/indietro del browser.
3. **Scomodità su smartphone:** Quando ci si trova fermi al distributore e si vuole registrare un pieno o scattare una foto allo scontrino con una mano sola, l'interfaccia di Streamlit risultava rigida e poco adatta agli schermi piccoli.

### La soluzione: separare Interfaccia e Motore di Calcolo
Anziché buttare via il lavoro fatto, nella V2 abbiamo diviso l'applicazione in due parti ben distinte all'interno dello stesso repository (`backend/` e `frontend/`):
- **Backend in FastAPI:** Ha ereditato tutta la logica Python già collaudata nella V1, esponendola tramite API REST veloci e ben strutturate.
- **Frontend in React 19 e TypeScript:** Un'interfaccia web costruita su misura con Vite e Tailwind CSS, progettata per caricarsi all'istante e adattarsi davvero sia al monitor di casa sia allo schermo dello smartphone.

---

## 🌿 3. La Transizione Graduale ("Strangler Fig") e il Pensionamento di Streamlit

Riscrivere un'applicazione da zero chiudendo tutto per settimane porta spesso a introdurre errori nei calcoli che prima funzionavano. Per evitarlo abbiamo seguito un approccio graduale, noto in ingegneria del software come *Strangler Fig* (costruire il nuovo sistema attorno a quello esistente finché non è pronto a sostituirlo del tutto).

### Come hanno convissuto Vecchio e Nuovo durante i lavori
1. **Sganciamento della logica da Streamlit:** Nella V1 molti moduli del database e dei servizi chiamavano direttamente funzioni grafiche di Streamlit (come `st.secrets` per leggere le password o `st.error()` e `st.stop()` per fermare la pagina in caso di errore). Il primo passo è stato ripulire `src/database/` e `src/services/` da queste dipendenze, facendo in modo che lavorassero con normali variabili d'ambiente ed eccezioni Python.
2. **Verifica incrociata dei numeri:** Mentre sviluppavamo i nuovi endpoint FastAPI e le prime pagine React, la vecchia interfaccia Streamlit è rimasta funzionante sullo stesso database. Questo ci ha permesso di fare una verifica preziosa: inserire un pieno o calcolare una media sulla nuova app e controllare in tempo reale che il risultato coincidesse al centesimo con quello mostrato dalla V1.

### Lo spegnimento definitivo di Streamlit
Una volta completate tutte le schermate in React (Dashboard, Rifornimenti con OCR, Manutenzioni, Promemoria, Report e Impostazioni) e verificato con la suite di test automatici che ogni flusso rispondesse correttamente, l'interfaccia Streamlit ha concluso il suo compito:
- Il punto d'ingresso ufficiale del progetto diventa esclusivamente la coppia **React + FastAPI** (orchestrata anche nel `docker-compose.yml`).
- La documentazione della V1 viene spostata nella cartella storica `docs/archive/v1-legacy/`.
- I vecchi file dell'interfaccia Streamlit non vengono più avviati né mantenuti, lasciando il codice del backend libero da qualsiasi legame con il vecchio framework grafico.

---

## ⚙️ 4. Come è progettato il Backend (FastAPI)

Il backend (`backend/src/`) è organizzato per mantenere separati il trasporto HTTP, la validazione dei dati e le regole di calcolo.

### Contratti Dati e Isolamento Utente
Ogni richiesta che arriva al server passa prima dagli schemi **Pydantic** (`src/api/schemas/`): se manca un campo obbligatorio o un numero è negativo, il server rifiuta subito la chiamata con un errore chiaro senza nemmeno interrogare il database.  
L'identità dell'utente viene verificata tramite dipendenze riutilizzabili (`src/api/deps.py`):
- In produzione controlla il token JWT rilasciato da **Supabase Auth** ed estrae l'identificativo dell'utente (`user_id`).
- In locale o in modalità demo utilizza automaticamente un profilo di prova, permettendo di testare tutte le API anche da Swagger UI (`/docs`) senza configurazioni esterne.
- Ogni singola query SQLAlchemy filtra sempre i record per `user_id`, garantendo che nessun utente possa mai leggere o modificare dati altrui.

### Le Scelte Principali nella Logica di Dominio

| Area Funzionale | Perché è stata progettata così |
| :--- | :--- |
| **Consumi *Full-to-Full*** | Dividere i chilometri per i litri di un singolo rifornimento parziale (es. 20 €) darebbe un consumo completamente falsato. Il backend calcola il valore in `km/L` solo quando l'utente segna un *Pieno Completo*, andando a ritroso fino al pieno precedente e sommando tutti i litri degli eventuali parziali intermedi. |
| **Controllo Chilometri in Tempo Reale** | Per evitare errori di battitura sul contachilometri, l'endpoint `/api/fuel/validate` confronta i chilometri digitati con il rifornimento precedente e con quello successivo nella linea del tempo, avvisando subito l'utente mentre sta ancora compilando il modulo. |
| **Scadenze Predittive e Salute Auto** | Oltre a controllare le date fisse, il backend calcola quanti chilometri l'utente percorre in media ogni giorno e stima la data solare in cui raggiungerà la prossima scadenza chilometrica (es. tagliando a 80.000 km), riassumendo lo stato generale in un punteggio da 0 a 100 (*Car Health Score*). |
| **Importazione Excel in Due Fasi** | Importare direttamente un file Excel rischia di inserire doppioni o righe sbagliate. Per questo il flusso è diviso in due passaggi: prima `/api/reports/import/preview` analizza il file e classifica ogni riga (*Nuovo*, *Modifica*, *Invariato*, *Warning*, *Errore*); poi l'utente può correggere le righe anomale direttamente dall'interfaccia, rivalidarle e infine confermare il salvataggio con `/commit`. |
| **Lettura Scontrini (OCR OpenAI)** | La foto della ricevuta viene letta in memoria e inviata a **OpenAI GPT-4o Vision** con istruzioni mirate per i distributori italiani. Se uno dei tre dati numerici (spesa totale, prezzo/L, litri) è sbiadito sulla carta termica, il backend lo ricalcola matematicamente a partire dagli altri due. |

---

## 💻 5. Come è progettato il Frontend (React & TypeScript)

Nell'ideare il frontend (`frontend/src/`) l'obiettivo non era semplicemente rifare le stesse pagine di prima con una grafica più bella, ma risolvere i problemi pratici d'uso quotidiano.

### Gestione Dati Semplice e Reattiva
Invece di appesantire l'app con gestori di stato globali complessi, abbiamo distinto due soli livelli:
1. **Dati provenienti dal server (TanStack Query):** Si occupa di scaricare i dati dalle API, conservarli in cache per rendere istantanei i cambi pagina e aggiornare automaticamente tutte le schermate collegate non appena viene salvato un nuovo dato (ad esempio, aggiungendo un pieno si aggiornano da soli anche i grafici della Dashboard e l'avanzamento dei promemoria chilometrici).
2. **Stato dei moduli (React Hook Form + Zod):** Gestisce la compilazione delle finestre di inserimento, come il calcolo automatico bidirezionale tra spesa, prezzo al litro e litri erogati.

### Un'Interfaccia che Cambia tra Scrivania e Distributore
L'applicazione viene usata in due modi molto diversi a seconda del dispositivo:
- **Da computer** si consultano i grafici annuali, si ordinano le tabelle storiche, si importa un archivio Excel o si scarica il Libretto di Manutenzione in PDF. Qui il layout sfrutta tutta la larghezza dello schermo con una barra laterale fissa e tabelle ricche di dettagli.
- **Da smartphone** si usa quasi sempre in auto o fermi alla pompa di benzina. Su schermi mobili la barra laterale sparisce per lasciare posto a una **barra inferiore a portata di pollice** con un pulsante centrale `+` ben visibile per inserire subito un pieno. Le tabelle larghe si trasformano automaticamente in schede verticali compatte, e il pulsante di scansione scontrino apre direttamente la fotocamera posteriore del telefono.

### Piccole Attenzioni per l'Uso Quotidiano
- **Tre temi visivi senza sfarfallii:** Oltre al tema scuro predefinito (*Dark Slate*) e a quello chiaro (*Clean Light*), è stato aggiunto il tema *OLED Pure Black* (nero assoluto per risparmiare batteria e non abbagliare di sera). La preferenza viene applicata prima ancora che la pagina venga disegnata a schermo, evitando fastidiosi lampi bianchi all'apertura.
- **Ripresa della sessione:** Se lasci l'app aperta in background sul telefono e la riapri dopo più di mezz'ora, il frontend aggiorna automaticamente tutti i dati dal server e riporta la vista sulla Dashboard in modo ordinato.

---

## ☁️ 6. Infrastruttura, Hosting e il Perché del "Keep-Alive"

Il progetto può essere eseguito interamente in casa su Docker, ma è stato configurato anche per essere pubblicato online mantenendo i costi fissi di infrastruttura pari a zero per l'uso dimostrativo:
- **Frontend:** distribuito gratuitamente come sito statico su CDN (**Vercel** / **Netlify**).
- **Database:** ospitato sul piano gratuito di **Supabase** (PostgreSQL).
- **Backend:** ospitato sul piano gratuito di **Render.com** (`render.yaml`).

### Una riflessione onesta sul meccanismo di Keep-Alive
Nel repository è presente un workflow GitHub Actions (`.github/workflows/keep-alive.yml`) che invia una richiesta all'endpoint `/health` del backend ogni 14 minuti, abbinato a un filtro nei log di Python (`logging_config.py`) per non riempire il terminale con queste chiamate di controllo.

A prima vista potrebbe sembrare una complicazione non necessaria per un'applicazione di monitoraggio carburante. La ragione è puramente pratica: i piani gratuiti di servizi come Render mettono in pausa il server dopo 15 minuti di inattività, causando un'attesa di 30–50 secondi (*cold start*) alla prima persona che apre l'app.  
Trattandosi di un progetto personale per il quale non aveva senso sostenere un abbonamento mensile fisso per un server dedicato sempre acceso, questo piccolo accorgimento permette a chiunque apra la demo pubblica di trovare l'applicazione subito reattiva. In un contesto aziendale o commerciale standard, naturalmente, questo workaround non verrebbe utilizzato e si adotterebbe semplicemente un'istanza cloud sempre attiva.

---

## ⚖️ 7. Limiti Attuali e Compromessi Accettati (Known Issues)

Ogni architettura nasce da scelte di equilibrio tra semplicità di sviluppo, costi e funzionalità. Di seguito sono riassunti in modo trasparente i limiti attuali della versione 2.0 e i compromessi accettati consapevolmente:

1. **Salvataggio del Token JWT nel `localStorage`:**  
   Per semplificare il dialogo tra il frontend (ospitato su CDN) e il backend (ospitato su un dominio diverso) senza complessità legate ai cookie cross-domain, il token di autenticazione viene salvato nel `localStorage` del browser e inviato nell'header `Authorization: Bearer`. È una soluzione comune e pratica per una SPA personale, ma meno robusta rispetto a cookie `HttpOnly` con protezione CSRF nel caso in cui il client dovesse subire attacchi XSS.
2. **Gestione della Concorrenza (*Last-Write-Wins*):**  
   Il database non implementa un sistema di blocco ottimistico (come numeri di versione sulle righe) per gestire modifiche simultanee. Se lo stesso account venisse usato nello stesso istante da due dispositivi diversi per modificare il medesimo rifornimento, prevarrebbe l'ultimo salvataggio inviato. Per un'app gestita dal proprietario del veicolo questo scenario è del tutto marginale.
3. **Limiti Fisiologici della Scansione OCR (OpenAI Vision):**  
   L'estrazione automatica dei dati dallo scontrino richiede una connessione internet attiva e comporta un piccolo costo a consumo legato ai token delle API di OpenAI (GPT-4o). Inoltre, la qualità del risultato dipende dallo stato fisico della ricevuta: scontrini in carta termica sbiaditi dal sole, stropicciati o fotografati al buio possono richiedere una correzione manuale da parte dell'utente. Infine, i chilometri attuali segnati dal cruscotto dell'auto non sono presenti sullo scontrino e vanno sempre digitati a mano.
4. **Supporto a un Singolo Veicolo per Account:**  
   Attualmente tutte le tabelle (`refuelings`, `maintenances`, `reminders`, `settings`) sono collegate direttamente all'identificativo dell'utente (`user_id`). Questo significa che ogni profilo utente gestisce un solo veicolo. Il supporto per più veicoli sotto lo stesso account (es. auto + moto o parco auto familiare) è previsto come passo evolutivo futuro attraverso l'introduzione di una tabella dedicata `vehicles`.

</div>

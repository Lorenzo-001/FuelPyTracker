# 🛠️ FuelPyTracker — Guida all'Installazione Completa

> Questa guida ti accompagnerà passo dopo passo fino ad avere FuelPyTracker in esecuzione sul tuo PC locale, in circa **10–15 minuti**.
> Non è richiesta alcuna esperienza con Python o con i database — tutto quello che devi saper fare è copiare un comando e incollarlo nel terminale. Se non sei uno sviluppatore, non preoccuparti: Docker si occuperà dell'ambiente per te.

---

## 📋 Indice

1. [Fase 1 — Prerequisiti](#fase-1--prerequisiti-gli-attrezzi-del-mestiere)
2. [Fase 2 — Clonazione del Codice](#fase-2--clonazione-del-codice)
3. [Fase 3 — Configurazione Supabase](#fase-3--configurazione-supabase-il-boss-finale-)
4. [Fase 4 — Integrazione OpenAI (Opzionale)](#fase-4--integrazione-openai-opzionale)
5. [Fase 5 — I File di Configurazione](#fase-5--i-file-di-configurazione-collegare-i-fili)
6. [Fase 6 — Avvio dell'Applicazione](#fase-6--avvio-dellapplicazione-accendiamo-i-motori-)
7. [Risoluzione dei Problemi Comuni](#-risoluzione-dei-problemi-comuni)

---

## Fase 1 — Prerequisiti (Gli attrezzi del mestiere)

Prima ancora di toccare il codice, assicurati di avere i seguenti strumenti installati. Sono pochi, ma indispensabili. Clicca sui link per scaricare quello che manca.

| Strumento | Perché serve | Obbligatorio? | Link |
|---|---|:---:|---|
| **Docker Desktop** | Esegue l'app in un ambiente isolato e riproducibile, senza installare Python o librerie direttamente sul tuo sistema | ✅ Sì | [download](https://www.docker.com/products/docker-desktop/) |
| **Git** | Scarica il codice sorgente dal repository GitHub | ✅ Sì | [download](https://git-scm.com/downloads) |
| **VS Code** | Editor consigliato per modificare i file di configurazione con evidenziazione della sintassi | ⚪ Consigliato | [download](https://code.visualstudio.com/) |

> 💡 **Perché Docker?** Invece di installare Python 3.11, dipendenze e librerie direttamente sul tuo sistema (e rischiare conflitti con altri progetti), Docker crea un ambiente virtuale isolato e autosufficiente. L'app gira al suo interno come se fosse in una scatola separata. Sul tuo PC rimane tutto pulito.

> 🪟 **Nota per utenti Windows:** Docker Desktop su Windows richiede **WSL2** (Windows Subsystem for Linux) — un componente che permette a Docker di girare in modo efficiente. Durante l'installazione, Docker te lo chiederà automaticamente. Accetta senza timore: è un processo guidato di un paio di minuti, e una volta completato non dovrai più preoccupartene. Se il tuo Windows è aggiornato, WSL2 è già presente nel sistema.

**Verifica rapida — prima di andare avanti:**

Apri un terminale (PowerShell su Windows, Terminal su Mac/Linux) ed esegui entrambi i comandi. Se restituiscono un numero di versione, sei pronto per iniziare.

```bash
docker --version
# Output atteso: Docker version 24.x.x, ...

git --version
# Output atteso: git version 2.x.x
```

Se uno dei due comandi non viene riconosciuto, installa lo strumento mancante prima di procedere.

---

## Fase 2 — Clonazione del Codice

Scaricare il codice è il primo vero passo — ed è anche il più semplice. Il comando `git clone` crea una copia locale del repository, mentre `cd` ti sposta nella cartella appena creata.

```bash
git clone https://github.com/Lorenzo-001/FuelPyTracker.git
cd FuelPyTracker
```

Tutti i comandi che eseguirai da questo momento in poi devono essere lanciati **dall'interno di questa cartella**. Se apri un nuovo terminale in un secondo momento, ricordati di tornarci con `cd FuelPyTracker`.

> 💡 Un modo comodo: in VS Code puoi aprire direttamente la cartella con `File → Open Folder`, e il terminale integrato (`` Ctrl+` ``) si posizionerà automaticamente nella directory corretta.

---

> 🔗 **Il collegamento logico tra questa fase e la prossima:** hai appena scaricato il motore dell'app sul tuo PC. Ma un motore senza carburante non parte. FuelPyTracker ha bisogno di un posto dove salvare i tuoi dati: i rifornimenti, le manutenzioni, le impostazioni. Invece di costringerti a installare un pesante server PostgreSQL in locale, useremo **Supabase** — un servizio cloud gratuito che fa tutto questo per te in pochi clic. Una volta configurato (e lo farai una volta sola), il tuo database sarà pronto ovunque tu voglia usare l'app.

## Fase 3 — Configurazione Supabase (Il Boss Finale 🐉)

Supabase è il cuore dell'intera applicazione. Fornisce due cose fondamentali:

- Un **database PostgreSQL** gestito nel cloud, senza bisogno di installare nulla in locale.
- Un sistema di **autenticazione** integrato (login, registrazione, reset password) pronto all'uso.

> 🛡️ **Una nota sulla sicurezza dei dati:** FuelPyTracker garantisce la separazione dei dati tra utenti filtrando le query direttamente nel codice Python — ogni operazione sul database include esplicitamente l'⁠`user_id` dell'utente loggato, rendendo impossibile leggere i record altrui. Supabase offre anche la Row Level Security (RLS), una funzionalità avanzata che sposta queste regole direttamente al livello del database SQL — un'estensione futura attivabile via SQL Editor senza modifiche all'applicazione.

Questo è il passaggio più articolato della guida, ma è necessario farlo **una volta sola**. Seguilo con calma: ti guidiamo clic per clic.

---

### 3.1 — Crea un Progetto Supabase

1. Vai su **[supabase.com](https://supabase.com/)** e crea un account gratuito, oppure accedi se ne hai già uno. Il piano gratuito è più che sufficiente per uso personale.

2. Dalla dashboard, clicca su **"New Project"** e scegli un nome descrittivo, ad esempio `fuelpytracker`.

3. Ti verrà chiesto di impostare una **password per il database**. Scegline una sicura.

   > ⚠️ **Salva questa password adesso, da qualche parte sicura.** Supabase non te la mostrerà di nuovo dopo la creazione. Ti servirà tra pochi minuti per costruire la stringa di connessione al database.

4. Seleziona la **regione** più vicina alla tua posizione geografica. Per l'Europa, `eu-central-1` (Frankfurt) è in genere la scelta ottimale in termini di latenza.

5. Clicca su **"Create new project"** e attendi 1–2 minuti che il progetto venga inizializzato. Supabase mostrerà una barra di progresso — aspetta che sia completamente verde prima di procedere.

---

### 3.2 — Recupero delle Chiavi API

Una volta che il progetto è attivo, hai bisogno di **tre valori** che userai nella configurazione. L'interfaccia di Supabase si aggiorna spesso, ma ecco i percorsi attuali.

---

#### 🔑 Valore 1 — Project URL 

Nel menu laterale sinistro, vai su **Integrations → Data API**. Copia il link presente nel riquadro **API URL**.

Esempio: `https://abcdefghij.supabase.co`

![Schermata Integrations > Data API](../assets/supa_data_api.png)

---

#### 🔑 Valore 2 — Anon Key (per l'autenticazione)

Nel menu laterale sinistro, sotto **Project Settings → Configuration**, vai su **API Keys**. Seleziona il tab **"Legacy anon, service_role API keys"** e copia la stringa molto lunga associata alla voce `anon public`.

Esempio: `eyJhbGci...` (una stringa di circa 200 caratteri)

> 💡 L'Anon Key è una chiave **pubblica** per design — viene inclusa nelle richieste client-side ed è normale che sia visibile. Non è un segreto assoluto, ma è comunque bene non diffonderla inutilmente.

![Schermata Project Settings > Configuration > API Keys](../assets/supa_api_keys.png)

---

#### 🔑 Valore 3 — Connection String (per il database)

Questa stringa permette all'app di salvare i dati direttamente su PostgreSQL. Non si trova nei menu laterali, ma in un pannello dedicato accessibile dall'alto:

1. Guarda in alto al centro nella dashboard (accanto al nome del progetto) e clicca sul pulsante **"Connect"**.
2. Nel pannello che si apre, seleziona il tab **URI**.
3. Seleziona la modalità **Transaction** — è fondamentale: usa la porta `6543` del connection pooler, l'unica compatibile con SQLAlchemy.
4. Copia la stringa risultante, che avrà questo formato:
   ```
   postgresql://postgres.[PROJECT_REF]:[YOUR-PASSWORD]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
   ```
5. **Sostituisci `[YOUR-PASSWORD]`** con la password del database scelta al passo 3.1.

> ⚠️ **Caratteri speciali nella password:** se contiene simboli come `@`, `#`, `!` o `%`, vanno codificati in formato URL (es. `@` → `%40`). Usa [urlencoder.org](https://www.urlencoder.org/) per farlo in automatico. Se la password è solo alfanumerica, non è necessario fare nulla.

![Schermata pannello Connect > tab URI > modalità Transaction](../assets/supa_connect_db.png)

---

### 3.3 — Il Database si Crea da Solo ✨

Potresti aspettarti di dover eseguire uno script SQL per creare le tabelle. **Non è necessario.**

FuelPyTracker usa SQLAlchemy con la funzione `create_all()`: al **primo avvio dell'applicazione**, tutte le tabelle (`refuelings`, `maintenances`, `reminders`, `settings`, `reminder_history`) vengono create automaticamente nel tuo database Supabase se non esistono ancora. L'operazione è idempotente — se le tabelle esistono già, non vengono toccate.

Il tuo unico compito è fornire la stringa di connessione corretta nel passo 5.2. L'app fa il resto.

---

## Fase 4 — Integrazione OpenAI (Opzionale)

Il modulo OCR consente di fotografare uno scontrino del distributore e lasciare che l'app estragga automaticamente litri, importo e stazione di servizio, usando **GPT-4o Vision** di OpenAI.

> **Questa funzionalità è completamente opzionale.** Puoi saltare questa fase interamente — FuelPyTracker funziona al 100% anche senza di essa. Se non configuri la chiave, il pulsante di scansione OCR mostrerà un messaggio di errore, ma dashboard, inserimento manuale, manutenzioni, report e tutto il resto rimarranno perfettamente operativi.

Se vuoi abilitarla:

1. Vai su **[platform.openai.com](https://platform.openai.com/)** e crea un account (o accedi).
2. Nel menu laterale, vai su **API Keys** e clicca su **"Create new secret key"**. Dagli un nome riconoscibile (es. `FuelPyTracker`).
3. Copia immediatamente la chiave generata — inizia con `sk-proj-...`.

   > ⚠️ OpenAI mostra la chiave **una volta sola** al momento della creazione. Se chiudi la finestra prima di copiarla, dovrai generarne una nuova.

4. **Attenzione ai costi:** GPT-4o Vision è un'API a consumo. Ogni scansione elabora un'immagine e ha un piccolo costo associato. Per un uso personale e occasionale si tratta di frazioni di centesimo a scontrino, ma è bene saperlo. Consulta il [pricing di OpenAI](https://openai.com/pricing) per i dettagli aggiornati.

---

## Fase 5 — I File di Configurazione (Collegare i fili)

Sei quasi in fondo. In questa fase "colleghi" le chiavi raccolte all'applicazione, creando due file di configurazione a partire dai template già inclusi nel progetto.

> 💡 **Perché due file separati?** Perché hanno responsabilità diverse e non si mescolano mai.
> - **`.env`** dice all'app *come comportarsi*: modalità normale o demo pubblica, e quale utente fittizio iniettare. È la mente dell'applicazione.
> - **`.streamlit/secrets.toml`** custodisce le *chiavi della cassaforte*: le credenziali per il database, per l'autenticazione e per OpenAI. È il portachiavi.
>
> Docker li gestisce entrambi in modo sicuro: le variabili dell'`.env` vengono iniettate nell'ambiente del container tramite la direttiva `env_file`, mentre `secrets.toml` viene montato come volume — il file resta fisicamente sul tuo PC e non finisce mai dentro l'immagine Docker né, tantomeno, su GitHub.

---

### 5.1 — File `.env` (comportamento dell'applicazione)

Il file `.env` non contiene le credenziali di accesso ai servizi, ma controlla il **comportamento generale** dell'app — in particolare, se deve avviarsi in modalità demo pubblica o in modalità normale (con i tuoi dati).

Crea il file partendo dal template:

```bash
# Su Mac/Linux:
cp .env.example .env

# Su Windows (PowerShell):
Copy-Item .env.example .env
```

Apri il file `.env` appena creato e lascialo così per un'installazione personale standard:

```dotenv
# Modalità demo: imposta True solo per una vetrina pubblica Read-Only.
# Con False (default), l'app funziona normalmente con il tuo account Supabase.
DEMO_MODE=False

# Le variabili seguenti sono obbligatorie SOLO se DEMO_MODE=True.
# Consulta docs/SETUP_GUIDE.md per istruzioni sulla configurazione della demo.
DEMO_USER_ID=your-demo-user-uuid
DEMO_USER_EMAIL=demo@example.com
```

I campi `DEMO_USER_ID` e `DEMO_USER_EMAIL` sono usati **solo** quando `DEMO_MODE=True` (per la vetrina pubblica). In modalità normale puoi lasciarli invariati — non vengono letti.

> 💡 Non trovi `PYTHONPATH` in questo file? È normale. Il percorso Python è fisso per design — il container usa sempre `/app` come root — e viene impostato direttamente nel `Dockerfile`. Non è una configurazione che devi gestire tu.

---

### 5.2 — File `.streamlit/secrets.toml` (le credenziali)

Questo è il file più critico: contiene tutte le chiavi segrete che permettono all'app di connettersi a Supabase (database + auth) e a OpenAI. È anche il file che Docker "monta" direttamente nel container al momento dell'avvio — le credenziali non finiscono mai dentro l'immagine Docker stessa.

Crea il file partendo dal template:

```bash
# Su Mac/Linux:
cp .streamlit/secrets.toml.example .streamlit/secrets.toml

# Su Windows (PowerShell):
Copy-Item .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Apri `.streamlit/secrets.toml` e sostituisci i placeholder con i valori reali raccolti nelle fasi precedenti:

```toml
[database]
# La stringa di connessione Transaction Mode (porta 6543) — ricavata dalla Fase 3.2.
# Ricorda: se la password contiene caratteri speciali, codificali in URL.
url = "postgresql://postgres.[TUO-PROJECT-REF]:[PASSWORD]@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"

[supabase]
# Il Project URL e l'Anon Key dalla sezione Project Settings → API (Fase 3.2).
url = "https://[TUO-PROJECT-REF].supabase.co"
key = "eyJhbGci..."        # Incolla qui la tua Anon Key completa
redirect_url = "http://localhost:8501"

[openai]
# Opzionale — se non usi l'OCR, puoi lasciare questo placeholder invariato.
api_key = "sk-proj-..."
```

> **Due regole di sintassi TOML da non dimenticare:**
> - Tutti i valori stringa devono essere racchiusi tra **virgolette doppie** `"..."`. Una virgoletta mancante causa un crash immediato all'avvio.
> - Il `redirect_url` deve puntare a `http://localhost:8501` **senza** slash finale — un piccolo dettaglio che può causare errori nel flusso di autenticazione.

> **Sicurezza:** Entrambi i file (`.env` e `.streamlit/secrets.toml`) sono già inclusi nel `.gitignore` del progetto. Non verranno mai caricati su GitHub accidentalmente, neanche con un `git add .`. Non condividerli con nessuno e non allegarli mai a email o chat.

---

## Fase 6 — Avvio dell'Applicazione (Accendiamo i motori 🚀)

Tutto è pronto. Dalla cartella radice del progetto (`FuelPyTracker/`), esegui:

```bash
docker compose up --build -d
```

Il flag `--build` dice a Docker di costruire l'immagine partendo dal `Dockerfile` (necessario la prima volta e dopo ogni modifica al codice). Il flag `-d` avvia il container in background, liberando il terminale.

**Cosa accade nei secondi successivi:**

1. Docker scarica l'immagine base **Python 3.11-slim** (~100MB — solo la prima volta).
2. Installa tutte le librerie Python elencate in `requirements.txt`.
3. Avvia il container `FuelPyTracker` in ascolto sulla porta `8501`.
4. Al primo accesso nel browser, l'app si connette a Supabase e crea automaticamente le tabelle del database.

**⏱️ Quanto ci vuole?** La prima build richiede **3–5 minuti** (dipende dalla velocità della connessione e del PC). Dall'avvio successivo in poi — senza il flag `--build` — il container parte in **meno di 10 secondi**.

Quando il container è pronto vedrai nel terminale:

```
✔ Container FuelPyTracker  Started
```

Apri il browser e vai a:

```
http://localhost:8501
```

🎉 L'applicazione è live. Puoi registrare un nuovo account usando la schermata di login — Supabase Auth si occupa di tutto il flusso di autenticazione.

---

### Comandi utili da tenere a portata di mano

| Cosa vuoi fare | Comando |
|---|---|
| Avviare l'app (prima volta o dopo modifiche al codice) | `docker compose up --build -d` |
| Avviare l'app (avvii successivi, senza rebuild) | `docker compose up -d` |
| Fermare il container | `docker compose down` |
| Vedere i log in tempo reale (utile per debug) | `docker compose logs -f` |
| Controllare se il container è attivo | `docker ps` |

---

## 🆘 Risoluzione dei Problemi Comuni

I problemi che seguono coprono la grande maggioranza dei casi in cui l'installazione non va a buon fine al primo tentativo. Leggi il **sintomo**, trovalo nella lista e segui la soluzione corrispondente.

---

### ❌ "Port 8501 is already in use"

**Sintomo:** Docker tenta di avviare il container ma fallisce subito, segnalando che la porta 8501 è già in uso.

**Causa più comune:** un container `FuelPyTracker` è già in esecuzione in background da una sessione precedente, oppure un altro processo Streamlit è attivo.

**Soluzione:**

```bash
# Ferma e rimuovi i container definiti nel docker-compose.yml:
docker compose down

# Se il messaggio persiste, forza la rimozione del container per nome:
docker rm -f FuelPyTracker
```

Se il problema non è Docker ma un altro processo, puoi anche semplicemente usare una porta diversa: modifica la riga `ports` nel file `docker-compose.yml` da `"8501:8501"` a `"8502:8501"` e riavvia. L'app sarà raggiungibile su `http://localhost:8502`.

---

### ❌ "Database non raggiungibile" / Errore rosso all'avvio

**Sintomo:** L'app si apre nel browser ma mostra immediatamente un blocco rosso con un messaggio di errore relativo al database o alla connessione.

**Checklist da seguire in ordine:**

1. **Controlla la password nella Connection String.** La password nella sezione `[database]` di `secrets.toml` deve essere quella che hai scelto su Supabase al momento della creazione del progetto — non quella del tuo account Google o GitHub. Se contiene caratteri speciali (`@`, `!`, `#`, `%`), devono essere codificati in URL (usa [urlencoder.org](https://www.urlencoder.org/)).

2. **Verifica che la porta sia `6543`, non `5432`.** La stringa di connessione deve puntare a `pooler.supabase.com:6543` (Transaction Mode). La porta `5432` è quella della connessione diretta al database, incompatibile con la configurazione del connection pool dell'app.

3. **Il progetto Supabase potrebbe essere in pausa.** Sul piano gratuito, i progetti vengono automaticamente sospesi dopo 7 giorni senza attività. Vai sulla [dashboard di Supabase](https://supabase.com/dashboard), entra nel tuo progetto e, se vedi un banner di "Project paused", clicca su "Restore project". La riattivazione richiede circa 30 secondi.

4. **Riavvia il container dopo ogni modifica ai secrets.** Le variabili in `secrets.toml` vengono lette all'avvio — se cambi qualcosa, il container deve essere riavviato per recepire le modifiche:
   ```bash
   docker compose down && docker compose up -d
   ```

---

### ❌ Registrazione bloccata / Email di conferma che non arriva

**Sintomo:** Inserisci email e password per registrarti, ma non ricevi l'email di conferma, oppure il flusso di login si blocca dopo il click sul link.

**Soluzione 1 — Disabilita la conferma email per lo sviluppo locale:**

Il piano gratuito di Supabase permette solo **2 email di conferma all'ora**. Per sviluppare e testare in locale, la cosa più pratica è disabilitare temporaneamente questo requisito:

1. Vai su **Authentication → Providers → Email** nella dashboard Supabase.
2. Disabilita l'opzione **"Confirm email"**.
3. Salva. Da questo momento puoi registrarti senza aspettare email.

> Se stai configurando un'istanza per uso condiviso o pubblico, ri-abilita la conferma email per sicurezza.

**Soluzione 2 — Verifica il redirect URL:**

Se il click sul link di conferma porta a un errore, il problema è quasi certamente che il `redirect_url` in `secrets.toml` non corrisponde a quello configurato in Supabase. Assicurati che sia esattamente `http://localhost:8501` (senza slash finale) sia nel file che in **Authentication → URL Configuration → Site URL** sulla dashboard.

---

### ❌ Il modulo OCR restituisce un errore

**Sintomo:** Carichi un'immagine di uno scontrino, premi il pulsante di scansione, e ricevi un messaggio di errore invece del risultato.

**Cause possibili:**

- La chiave `api_key` in `secrets.toml` è errata o è rimasta il placeholder `sk-proj-...`. Verifica che sia la chiave reale generata su platform.openai.com.
- Il tuo account OpenAI ha esaurito il credito disponibile. Accedi alla [dashboard OpenAI](https://platform.openai.com/usage) per verificare il saldo.
- La chiave è stata revocata o è scaduta. In quel caso, generane una nuova e aggiorna `secrets.toml`.

Ricorda: se non hai bisogno dell'OCR, puoi ignorare completamente questo errore — non ha nessun impatto sulle altre funzionalità dell'app.

---

*Hai trovato un bug, un errore nella guida o un passaggio poco chiaro? [Apri una Issue su GitHub](https://github.com/Lorenzo-001/FuelPyTracker/issues) — ogni segnalazione è preziosa e ti verrà risposto al più presto.*

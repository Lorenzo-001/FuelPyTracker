<div align="justify">

# 📡 Riferimento API & Contratti di Integrazione — V2.0

> **Panoramica dei contratti di comunicazione, convenzioni REST e domini operativi esposti dal backend FastAPI.**

---

## 🌐 Standard e Convenzioni REST

Questo documento riassume le convenzioni di comunicazione e i gruppi di endpoint messi a disposizione dal server FastAPI per il dialogo con il frontend React o con client esterni.

Le API di FuelPyTracker seguono le convenzioni **RESTful** e lo standard **OpenAPI 3.1**:

- **Formato dei Dati:** Tutti i dati in ingresso e in uscita utilizzano il formato `application/json` (ad eccezione del caricamento delle immagini per la scansione OCR e del download dei file binari PDF ed Excel).
- **Codici di Stato HTTP Standard:**
  - `200 OK` / `201 Created`: Operazione completata con successo.
  - `400 Bad Request`: Parametri della richiesta non validi a livello applicativo (es. chilometri incoerenti).
  - `401 Unauthorized`: Autenticazione assente, scaduta o non valida.
  - `403 Forbidden`: Operazione di scrittura bloccata (ad esempio quando è attiva la modalità dimostrativa in sola lettura).
  - `404 Not Found`: Risorsa richiesta inesistente o non appartenente all'utente autenticato.
  - `422 Unprocessable Entity`: Errore di validazione dello schema dati Pydantic.
  - `500 Internal Server Error`: Errore non gestito lato server.
- **Formato degli Errori:** Gli errori restituiscono una risposta JSON strutturata con il messaggio descrittivo del problema (`{"detail": "Descrizione dell'errore"}`).

---

## 📖 Documentazione Interattiva Live

Quando il backend è in esecuzione, genera automaticamente la specifica completa e le interfacce di prova:
- **Swagger UI:** Disponibile all'indirizzo `http://localhost:8000/docs` (consente di consultare gli schemi JSON e testare direttamente gli endpoint dal browser).
- **ReDoc:** Disponibile all'indirizzo `http://localhost:8000/redoc` (visualizzazione ordinata pensata per la lettura).

---

## 🧩 Domini Operativi delle API

Di seguito sono descritti i moduli principali in cui sono organizzate le rotte del backend:

### 1. Autenticazione e Sessione (`/api/auth`)
- **Registrazione e Login (`POST /login`, `POST /register`):** Verifica delle credenziali ed emissione del token JWT di sessione (o accesso immediato con profilo dimostrativo se attivo `DEMO_MODE`).
- **Verifica Sessione (`GET /me`):** Controllo della validità del token corrente e restituzione dei dati del profilo utente attivo.
- **Logout e Recupero Password (`POST /logout`, `POST /reset-password`):** Chiusura sessione e invio dell'email per il ripristino delle credenziali tramite Supabase Auth.

### 2. Dashboard e Analisi (`/api/dashboard`)
- **Riepilogo Generale (`GET /summary`):** Restituisce in un'unica chiamata l'ultimo rifornimento, la spesa totale (carburante e officina), il consumo medio storico, gli avvisi sui parziali accumulati e il punteggio di salute del veicolo (*Car Health Score*).
- **Serie Storiche per Grafici (`GET /charts`):** Estrae i dati temporali filtrabili per periodo (`1m`, `3m`, `6m`, `ytd`, `1y`, `all`) per disegnare l'andamento dei prezzi al litro, dei consumi in km/L e della spesa mensile.
- **Calcolatore Costi di Viaggio (`POST /trip-calculator`):** Calcola la stima di litri necessari, spesa totale e costo al chilometro per una determinata distanza in base alla media reale del veicolo.

### 3. Rifornimenti e Smart OCR (`/api/fuel`)
- **Elenco e Filtri (`GET /`):** Recupero cronologico dei rifornimenti con filtro opzionale per anno solare e calcolo automatico di `delta_km`, `km_per_liter` (algoritmo *Full-to-Full*) e giorni trascorsi.
- **Inserimento, Modifica ed Eliminazione (`POST /`, `PUT /{id}`, `DELETE /{id}`):** Gestione completa dei record di rifornimento con ricalcolo automatico delle statistiche collegate.
- **Validazione Preventiva Chilometri (`POST /validate`):** Controllo immediato durante la compilazione del modulo per verificare che i chilometri inseriti siano coerenti con il rifornimento precedente e quello successivo.
- **Scansione Scontrino OCR (`POST /ocr`):** Ricezione della foto dello scontrino via upload multipart, analisi tramite **OpenAI GPT-4o Vision** e restituzione dei dati estratti (data, spesa totale, prezzo al litro, litri e distributore).

### 4. Manutenzioni (`/api/maintenance`)
- **Storico Interventi (`GET /`, `POST /`, `PUT /{id}`, `DELETE /{id}`):** Gestione delle spese di officina suddivise per categoria (Tagliando, Freni, Gomme, Revisione, ecc.) con filtro per anno e tipologia.
- **Scadenze Predittive (`GET /deadlines`):** Calcolo dello stato delle prossime scadenze temporali o chilometriche con stima della data di raggiungimento in base ai chilometri percorsi in media ogni giorno.

### 5. Promemoria Periodici (`/api/reminders`)
- **Elenco e Avanzamento (`GET /`, `POST /`, `PUT /{id}`, `DELETE /{id}`):** Gestione dei controlli periodici con calcolo in tempo reale della percentuale di avanzamento e dei chilometri o giorni rimanenti.
- **Registrazione Controllo Eseguito (`POST /{id}/complete`):** Aggiorna la data e il chilometraggio dell'ultima verifica, azzera la barra di avanzamento per il nuovo ciclo e salva una voce nello storico (`GET /{id}/history`).

### 6. Report, Esportazione e Importazione (`/api/reports`)
- **Statistiche e Download Excel (`GET /stats`, `GET /excel`, `GET /template`):** Conteggio dei dati in archivio, generazione del file Excel completo multi-foglio (`.xlsx`) e download del modello vuoto pre-impostato.
- **Libretto Manutenzione PDF (`POST /pdf`):** Generazione dinamica del documento PDF formattato per la stampa con intestazione veicolo e storico interventi.
- **Importazione Guidata (`POST /import/preview`, `POST /import/revalidate`, `POST /import/commit`):**
  - *Fase 1 (Anteprima):* Analisi del file CSV/Excel caricato e classificazione di ogni riga (nuovo record, modifica, invariato, avviso o errore).
  - *Rivalidazione:* Verifica immediata delle righe corrette dall'utente nell'interfaccia.
  - *Fase 2 (Salvataggio):* Scrittura definitiva nel database di tutti i record validati.

### 7. Impostazioni e Categorie (`/api/settings`)
- **Preferenze e Profilo Veicolo (`GET /`, `PUT /`):** Lettura e salvataggio dei dati del veicolo (nome/modello, targa, alimentazione), delle soglie di spesa/tolleranza e delle opzioni per le note OCR.
- **Categorie Personalizzate (`POST` e `DELETE` su `/maintenance-categories` e `/reminder-categories`):** Aggiunta e rimozione delle categorie utilizzate nei moduli di manutenzione e promemoria.

### 8. Health Check (`/health` e `/api/health`)
- **Stato del Servizio (`GET` e `HEAD`):** Endpoint leggero di diagnostica che verifica l'operatività del server FastAPI e controlla con una query rapida (`SELECT 1`) la connessione attiva al database.

</div>

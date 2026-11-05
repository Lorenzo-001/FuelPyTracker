<div align="justify">

# 💻 Architettura Frontend — Interfaccia Web React

> **Organizzazione tecnica dell'interfaccia utente: gestione dei dati, temi visivi e adattamento tra computer e smartphone.**

---

## 🚀 Struttura dell'Interfaccia

Questo documento descrive come è costruita l'interfaccia web di FuelPyTracker V2 e come gestisce la navigazione, il dialogo con il server e la presentazione dei dati.

L'applicazione è sviluppata con **React**, **TypeScript** e **Vite**. Tutte le schermate (Dashboard, Rifornimenti, Manutenzioni, Promemoria, Report e Impostazioni) vengono gestite direttamente nel browser: il passaggio da una sezione all'altra è immediato e non richiede il ricaricamento dell'intera pagina web.

---

## ⚡ Gestione dei Dati e Sincronizzazione con il Server

Per mantenere l'interfaccia veloce e sempre allineata con il database, il frontend distingue tra i **dati provenienti dal server** e lo **stato temporaneo delle schermate**:

### 1. Dati del Server e Aggiornamento Automatico
- **Memoria Temporanea (Cache):** Quando apri una pagina (ad esempio la Dashboard o lo storico dei rifornimenti), i dati ricevuti dal backend vengono conservati in memoria. Se torni sulla stessa pagina pochi istanti dopo, le informazioni sono già pronte senza dover attendere un nuovo caricamento.
- **Allineamento Automatico dopo ogni Modifica:** Quando aggiungi, modifichi o elimini un rifornimento o una manutenzione, l'applicazione aggiorna automaticamente tutte le viste collegate (come le medie della Dashboard e i grafici), senza bisogno di ricaricare manualmente la pagina.
- **Riduzione delle Chiamate di Rete:** Se più elementi della stessa schermata hanno bisogno della stessa informazione (ad esempio i dati del veicolo o il riepilogo spese), viene effettuata una sola richiesta verso il server.

### 2. Interattività Locale nei Moduli
- **Controlli in Tempo Reale:** I moduli di inserimento controllano subito i valori digitati (ad esempio il calcolo automatico dei litri a partire da spesa e prezzo al litro, oppure la verifica che i chilometri inseriti siano superiori a quelli del pieno precedente).
- **Strumenti Istantanei:** I filtri di ricerca nella tabella rifornimenti e i cambi di periodo nei grafici lavorano direttamente sui dati caricati, rispondendo all'istante.

---

## 🎨 Sistema dei Temi e Stile Grafico

Lo stile visivo è realizzato con **Tailwind CSS** e si appoggia a un set centralizzato di variabili colore per gestire i tre temi disponibili (*Dark Slate*, *OLED Pure Black* e *Clean Light*):
- **Cambio Tema Immediato:** Ogni componente dell'interfaccia (sfondi, schede, testi, bordi) fa riferimento a variabili cromatiche comuni. Quando l'utente cambia tema, i colori si aggiornano all'istante su tutta l'applicazione.
- **Caricamento del Tema all'Avvio:** La preferenza scelta viene salvata nel browser e letta subito all'apertura della pagina, prima ancora di disegnare le schermate, evitando fastidiosi sfarfallii luminosi per chi usa i temi scuri.

---

## 📐 Adattamento tra Computer e Smartphone

L'interfaccia modifica automaticamente la propria struttura e il modo di presentare le informazioni in base alle dimensioni dello schermo:

### Su Computer e Schermi Ampi
- **Menu Laterale e Barra Superiore:** Navigazione completa sempre visibile, con indicatori dello stato di connessione al server e pulsante rapido per registrare un nuovo rifornimento.
- **Viste Tabellari Complete:** I rifornimenti e i controlli di importazione vengono mostrati in tabelle ampie con colonne ordinabili e filtri rapidi.

### Su Smartphone e Schermi Touch
- **Barra di Navigazione Inferiore:** Il menu si sposta nella parte bassa dello schermo con un pulsante centrale (`+`) facilmente raggiungibile con il pollice per inserire subito un nuovo pieno.
- **Trasformazione in Schede Verticali:** Le tabelle con molte colonne lasciano spazio a schede verticali compatte, pensate per essere lette comodamente scorrendo solo dall'alto verso il basso.
- **Pannelli a Scorrimento dal Basso:** I dettagli dei singoli rifornimenti e i menu secondari si aprono come pannelli scorrevoli dal basso, facilitando l'utilizzo con una sola mano e la compilazione con la tastiera dello smartphone.

</div>

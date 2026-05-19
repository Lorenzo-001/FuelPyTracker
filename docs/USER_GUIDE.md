# 📖 Guida Utente — FuelPyTracker v1.0.0

> **Benvenuto nella tua guida di riferimento.**
> Questo documento ti accompagnerà passo dopo passo alla scoperta di tutte le funzionalità di FuelPyTracker,
> senza gergo tecnico — solo quello che ti serve per tenere la tua auto sotto controllo.

---

## Indice

1. [🚀 Introduzione e Navigazione Base](#1--introduzione-e-navigazione-base)
   - [🔐 Accesso e Registrazione](#-accesso-e-registrazione)
   - [🗺️ La Barra Laterale](#-la-barra-laterale-sidebar)
   - [🚨 Il Sistema di Avvisi](#-il-sistema-di-avvisi)
2. [📊 La Dashboard: Il Polso della Situazione](#2--la-dashboard-il-polso-della-situazione)
3. [⛽ Gestione Rifornimenti](#3--gestione-rifornimenti)
4. [🔧 Manutenzione: Scadenze vs Promemoria](#4--manutenzione-scadenze-vs-promemoria)
5. [⚙️ Impostazioni e Gestione Dati](#5--impostazioni-e-gestione-dati)
6. [👤 Profilo Utente](#6--profilo-utente)

---

## 1. 🚀 Introduzione e Navigazione Base

### Benvenuto in FuelPyTracker!

FuelPyTracker è il tuo libretto di bordo digitale. Tiene traccia di ogni rifornimento, ogni spesa di manutenzione e ogni scadenza — così tu puoi dimenticare tutto e pensare solo a guidare. 🚗

Con un colpo d'occhio puoi vedere:

- **Quanto spendi** di carburante al mese e all'anno
- **Quanto consuma** la tua auto (in Km per Litro)
- **Cosa si sta avvicinando** a scadenza (tagliando, gomme, revisione…)
- **Quanto ti costerà** il prossimo viaggio

> 💡 **Nota:** FuelPyTracker è progettato per gestire **un singolo veicolo per account**. Se possiedi più veicoli (auto + moto, o due auto), crea un account separato per ciascuno — ogni account ha il proprio storico, le proprie scadenze e le proprie statistiche completamente indipendenti.

---

### 🔐 Accesso e Registrazione

Prima di poter usare FuelPyTracker è necessario disporre di un account personale. La schermata di accesso si presenta appena si apre l'applicazione e offre due schede:

**Scheda 🔐 Accedi**
Inserisci la tua **email** e la tua **password** e clicca **Entra**. Se le credenziali sono corrette verrai portato direttamente alla Dashboard. In caso di errore, l'app ti mostra un messaggio chiaro: *"Credenziali non valide"*.

- **Password dimenticata?** Clicca l'omonimo link sotto il pulsante di accesso. Si aprirà un pannello dove inserire la tua email: riceverai un link di ripristino nella tua casella di posta. Cliccando il link verrai reindirizzato a una pagina dedicata per scegliere la nuova password (minimo 6 caratteri). Una volta salvata, l'app ti porta automaticamente alla Dashboard.

**Scheda 📝 Registrati**
Se non hai ancora un account, vai sulla scheda di registrazione. Inserisci:
- La tua **email** (sarà il tuo nome utente)
- La **password** (minimo 6 caratteri)
- La **conferma password** (deve coincidere esattamente)

Dopo aver cliccato **Crea Account**, il profilo viene creato istantaneamente e l'app ti porta direttamente alla Dashboard, già autenticato.

> 💡 **Tip:** I tuoi dati sono privati e separati da quelli di qualsiasi altro utente. Non è possibile accedere ai dati di un altro account, nemmeno con la stessa password.

> ⚠️ **Importante:** Se ricevi il messaggio *"Email già registrata"* durante la registrazione, significa che esiste già un account con quell'indirizzo. Usa la scheda **Accedi** e il link *"Password dimenticata?"* se non ricordi le credenziali.

---

### 🗺️ La Barra Laterale (Sidebar)

Tutto il navigatore dell'app vive nella barra laterale a sinistra dello schermo. Da lì puoi accedere a tutte le sezioni con un clic:

| Voce | Cosa trovi |
|---|---|
| **📊 Dashboard** | Panoramica generale, grafici, salute veicolo |
| **⛽ Rifornimenti** | Inserimento e storico dei pieni |
| **🔧 Manutenzione** | Scadenze, interventi e promemoria |
| **⚙️ Impostazioni** | Configurazioni, importazione e esportazione dati |
| **👤 Profilo** | Gestione account e cambio password |

In fondo alla sidebar trovi il tuo nome utente e il pulsante **Esci (Logout)**.

---

### 🚨 Il Sistema di Avvisi

FuelPyTracker ti avvisa automaticamente quando qualcosa richiede la tua attenzione. Gli avvisi funzionano su **due livelli**:

**1. Il Popup di Avvio (one-shot per sessione)**
All'apertura dell'app, se ci sono promemoria di routine scaduti (es. "Pressione Gomme" oltre la soglia di km impostata), compare un dialogo a schermo intero con l'elenco dei problemi. Puoi chiuderlo cliccando **"Ho capito, vado ai Promemoria"** per essere portato direttamente alla sezione Manutenzione. Questo popup si mostra una sola volta per sessione di lavoro.

**2. Il Badge Arancione nella Sidebar**
Se hai delle **scadenze già superate** (una revisione già scaduta, un tagliando oltre i km previsti), nella sidebar compare un avviso arancione con il numero di scadenze passate e un pulsante rapido **"Vai a Scadenze"**. Questo badge è sempre visibile, su ogni pagina, finché le scadenze non vengono risolte.

> 💡 **Tip:** Il badge nella sidebar controlla le **Scadenze** (eventi puntuali, come la revisione), mentre il popup di avvio controlla i **Promemoria** (routine periodiche, come il cambio olio). Sono due sistemi distinti, entrambi utili!

*[Placeholder Immagine: Dashboard Avvisi]*

---

## 2. 📊 La Dashboard: Il Polso della Situazione

La Dashboard è la tua homepage. Si apre automaticamente dopo il login e ti mostra tutto ciò che conta in pochi secondi.

*[Placeholder Immagine: Dashboard Principale]*

---

### 🩺 Lo Stato Salute Veicolo

In cima alla pagina trovi l'indicatore più importante: **lo Stato Salute Veicolo**, espresso come percentuale colorata.

| Colore | Valore | Significato |
|---|---|---|
| 🟢 **Verde** | 80% – 100% | Tutto sotto controllo |
| 🟠 **Arancione** | 50% – 79% | Attenzione richiesta |
| 🔴 **Rosso** | 0% – 49% | Intervento urgente |

**Come viene calcolato?**
Il punteggio parte da **100 punti** e scende in base agli elementi scaduti o trascurati. Il sistema controlla due tipi di voci:

**Scadenze (impatto alto):**
- Una scadenza **di km superata** (es. tagliando oltre i km previsti) sottrae **20 punti**.
- Una scadenza **di data superata** (es. revisione scaduta ieri) sottrae **15 punti**.

**Promemoria di Routine (impatto moderato):**
- Un promemoria **di km** non resettato (es. cambio olio da troppi km) sottrae **10 punti**.
- Un promemoria **di tempo** non resettato (es. controllo pressione gomme da troppi giorni) sottrae **5 punti**.

Il punteggio non scende mai sotto lo **0%**.

> 💡 **Tip:** Clicca su **"🛠️ Funzionalità → 🩺 Check-Up Salute"** per aprire un pannello dettagliato che ti elenca esattamente cosa sta abbassando il punteggio — e un tasto rapido per andare a risolverlo.

---

### 📉 I Grafici Principali

Sotto l'indicatore di salute trovi tre grafici interattivi. Ognuno dispone di un piccolo menu a tendina **"⚙️ Filtra Periodo"** che ti permette di zoomare su una finestra temporale specifica: puoi scegliere tra Ultimo Mese, Ultimi 3 Mesi, Ultimi 6 Mesi, Anno Corrente (YTD), Ultimo Anno oppure Tutto lo Storico. I grafici si aggiornano istantaneamente a ogni selezione, senza ricaricare la pagina.

---

**📉 Trend Prezzo Carburante**

Questo grafico a linee mostra l'evoluzione del prezzo al litro pieno dopo pieno. Il punto più recente è sempre a destra, il più lontano nel tempo a sinistra. All'interno del grafico è tracciata anche una **linea tratteggiata grigia** che rappresenta la **media del periodo selezionato**: in un colpo d'occhio puoi capire se il tuo ultimo rifornimento è stato sopra o sotto la tua media storica. Passando il cursore su un punto, compare un tooltip con data e prezzo esatto di quel rifornimento.

> 💡 **Tip:** Usa il filtro "Tutto lo storico" per vedere l'andamento pluriennale dei prezzi. Noterai chiaramente i periodi di crisi energetica o i cali stagionali.

---

**🚗 Efficienza (Km/L)**

Questo grafico a area mostra il consumo reale del tuo veicolo, calcolato pieno dopo pieno con l'algoritmo Full-to-Full (vedi sezione Rifornimenti). L'area colorata sotto la curva riempie visivamente lo spazio fino allo zero, rendendo immediatamente percepibile quando i consumi sono buoni (area grande) o peggiori del solito (curva che scende). I rifornimenti parziali non compaiono in questo grafico: vengono accumulati e calcolati solo quando fai il pieno successivo, garantendo dati sempre corretti.

> 📌 **Il primo rifornimento come punto di partenza:** Se stai iniziando a usare l'app oggi, il primissimo rifornimento che inserisci stabilisce il **chilometraggio di riferimento iniziale** (il "punto zero" dell'odometro). Per questo motivo non genererà un valore Km/L — l'app non ha un pieno precedente da cui calcolare la distanza percorsa. Il grafico Efficienza comincerà a popolarsi a partire dal **secondo rifornimento**. È normale e atteso: più dati accumuli, più preciso diventerà.

Questo grafico è particolarmente utile per individuare:
- **Anomalie** (un singolo pieno con consumo anomalo segnala forse una perdita o un errore di km)
- **Stagionalità** (i consumi tendono ad alzarsi in estate/autostrada e scendere in inverno/città)
- **Miglioramenti dopo un tagliando** (il grafico registra fedelmente se l'auto "respira meglio" dopo la manutenzione)

> 💡 **Tip:** Se un punto appare molto più basso degli altri, verifica quel rifornimento nella sezione **Storico**: potrebbe essere stato segnato come "Pieno" per errore quando in realtà era parziale.

---

**💸 Analisi Spesa**

Questo grafico a barre verticali raggruppa automaticamente le spese per **mese**, sommando tutti i rifornimenti del periodo. Ogni barra mostra il totale in € con il valore numerico visibile direttamente sulla barra. È perfetto per ragionare sul budget: puoi confrontare mesi estivi (spesso più alti per i viaggi) con mesi abituali, e pianificare di conseguenza.

> 💡 **Tip:** Seleziona il filtro "Anno Corrente (YTD)" per vedere l'accumulo mese per mese dall'1 gennaio e capire quanto hai già speso di carburante in questo anno.

---

### 🛠️ Gli Strumenti Rapidi

Nell'area **"ℹ️ Strumenti e Guida"** trovi due calcolatori istantanei:

**🧮 Calcola Viaggio**
Stima il costo del tuo prossimo viaggio. L'app precompila automaticamente:
- La **media Km/L** calcolata su tutto il tuo storico
- Il **prezzo dell'ultimo rifornimento**

Puoi modificarli liberamente. La formula è: `(Km del viaggio ÷ Km/L) × Prezzo €/L = Costo Stimato`.

**🩺 Check-Up Salute**
Apre un pannello che mostra il punteggio corrente con l'elenco dettagliato di tutti gli elementi che lo penalizzano. Perfetto dopo ogni intervento di manutenzione, per vedere il punteggio risalire.

---

## 3. ⛽ Gestione Rifornimenti

Questa sezione è il cuore pulsante di FuelPyTracker. Ogni rifornimento registrato alimenta i grafici della dashboard, i calcoli di consumo e le previsioni di manutenzione.

*[Placeholder Immagine: Gestione Rifornimenti]*

---

### ➕ Inserire un Rifornimento Manualmente

Clicca su **"➕ Registra Nuovo Rifornimento"** per aprire il pannello di inserimento. Compila i campi:

| Campo | Cosa inserire |
|---|---|
| **Data** | La data del rifornimento (default: oggi) |
| **Km Odometro** | Il valore attuale del contachilometri del veicolo |
| **Prezzo (€/L)** | Il prezzo al litro indicato sulla pompa |
| **Costo Totale (€)** | La somma totale pagata |
| **Pieno** | ✅ Selezionato = hai fatto il pieno; ☐ Deselezionato = rifornimento parziale |
| **Note** | Campo libero opzionale |

> 💡 **Tip:** Non inserire manualmente i litri — l'app li calcola automaticamente dividendo il costo totale per il prezzo al litro. Risultato sempre preciso!

L'app verifica automaticamente che i chilometri inseriti siano **cronologicamente coerenti**: non puoi inserire meno km di un rifornimento precedente, né più km di un rifornimento futuro già registrato. In caso di errore, un messaggio chiaro ti spiega cosa correggere.

---

### ⚡ La Differenza Vitale: Pieno vs Parziale

Questo è il concetto più importante per ottenere calcoli di consumo accurati.

**Rifornimento PIENO ✅ (spunta selezionata)**
L'app sa esattamente quanta benzina hai messo e quanti km hai percorso dall'ultimo pieno. Con questi due dati calcola il consumo reale con l'algoritmo **"Full-to-Full"**.

**Rifornimento PARZIALE ☐ (spunta deselezionata)**
Hai messo solo un po' di carburante perché ne avevi ancora in serbatoio. In questo caso l'app **accumula** i litri di tutti i parziali e li aggiunge al successivo pieno per calcolare il consumo corretto su tutto il tratto percorso.

**Esempio pratico:**
- Lunedì: pieno da 40L a 120.000 km ✅
- Mercoledì: parziale da 15L a 120.500 km ☐
- Venerdì: pieno da 35L a 121.200 km ✅

→ L'app calcola: `(35 + 15) litri = 50L` per `(121.200 - 120.000) = 1.200 km` = **24 km/L** ✓

> 💡 **Tip:** Se fai sempre il pieno, l'app calcolerà i consumi con precisione millimetrica. Se fai spesso rifornimenti parziali non preoccuparti: il sistema gestisce qualsiasi combinazione correttamente, purché tu segnali onestamente la spunta "Pieno".

---

### 📸 La Magia dell'OCR: Scansione AI dello Scontrino

Niente più digitazione manuale! Clicca **"🚀 SCANSIONA SCONTRINO CON AI"** per aprire il pannello di scansione.

**Come funziona:**
1. L'app apre uno scanner. Su **mobile** puoi usare direttamente la fotocamera; su **desktop** carichi un'immagine dal tuo computer (JPG, PNG).
2. Dopo aver caricato l'immagine clicca **"✨ Analizza con AI"**.
3. L'intelligenza artificiale legge lo scontrino e precompila automaticamente data, prezzo al litro e costo totale nel form sottostante.
4. Verifica i valori, compila manualmente il campo **Km Odometro** e salva.

**Consigli per foto perfette:**
- 📸 Inquadra **solo lo scontrino**, dal bordo superiore a quello inferiore
- ☀️ Assicurati che la foto sia **ben illuminata** e assolutamente **a fuoco**
- 🚫 Evita ombre, riflessi o dita che coprono parte del testo
- 📐 Tieni lo scontrino **più dritto possibile** (non in diagonale)

> 💡 **Tip:** Su uno smartphone moderno, la modalità "documento" della fotocamera nativa dà ottimi risultati. Se l'AI non riconosce lo scontrino, l'app ti spiega la causa specifica (immagine sfocata, scontrino non leggibile, ecc.) e ti suggerisce come migliorare.

---

### 📊 I KPI della Sezione Rifornimenti

In cima alla pagina Rifornimenti trovi i tuoi **indicatori chiave** per l'anno selezionato:

| KPI | Descrizione |
|---|---|
| **Totale Spesa** | Quanto hai speso in carburante nell'anno |
| **Totale Litri** | Quanti litri hai fatto nell'anno |
| **Prezzo Medio €/L** | Il prezzo medio pagato al litro |
| **Km Stimati** | Km percorsi nell'anno (max km − min km dell'anno) |
| **Min Km/L** | Il rifornimento con il consumo peggiore |
| **Max Km/L** | Il rifornimento con il consumo migliore |

---

## 4. 🔧 Manutenzione: Scadenze vs Promemoria

La sezione Manutenzione è il cuore della cura del tuo veicolo. Si articola in quattro tab ben distinti — **Storico**, **Gestione**, **Scadenze** e **Promemoria** — ognuno pensato per un'esigenza diversa. Capire la differenza tra di loro è fondamentale per sfruttarla al massimo.

---

### 📋 Tab Storico — Il Libretto Digitale

Il tab **"📋 Storico"** è il tuo libretto di manutenzione digitale. Ogni intervento effettuato sul veicolo viene registrato qui — tagliandi, cambi gomme, freni, interventi straordinari e qualsiasi altra spesa meccanica.

**Come si aggiunge un intervento:**
Clicca **"➕ Nuovo"** in alto a destra. Comparirà il form di inserimento con i seguenti campi:

| Campo | Descrizione |
|---|---|
| **Data** | La data in cui è stato eseguito l'intervento |
| **Km Odometro** | Il chilometraggio al momento dell'intervento |
| **Categoria** | Il tipo di intervento (scelta da un elenco personalizzabile nelle Impostazioni) |
| **Costo (€)** | Il costo dell'intervento |
| **Descrizione** | Note libere (es. "Sostituito con Pirelli P7") |
| **Scadenza Km** *(opzionale)* | Il km assoluto dell'odometro al quale questo intervento andrà ripetuto |
| **Scadenza Data** *(opzionale)* | La data calendario entro cui l'intervento dovrà essere rifatto |

I campi **Scadenza Km** e **Scadenza Data** sono opzionali: compilali solo per interventi con una scadenza futura nota (es. tagliando, revisione, bollo). Lascia vuoti per interventi straordinari senza scadenza prevedibile.

Lo storico mostra tutti gli interventi in una tabella filtrabile per **Categoria** (es. vuoi vedere solo i tagliandi, o solo le gomme) tramite il menu multiselect in cima al tab.

*[Placeholder Immagine: Registro Manutenzioni]*

---

### 🛠️ Tab Gestione — Modifica e Cancellazione

Il tab **"🛠️ Gestione"** ti permette di correggere o rimuovere interventi già registrati. Seleziona prima l'**anno** dal menu a tendina, poi scegli l'intervento specifico dall'elenco.

- **✏️ Modifica:** Apre un form precompilato con tutti i dati dell'intervento. Puoi correggere qualsiasi campo (data, km, costo, categoria, descrizione, scadenze). La validazione assicura che la data di scadenza sia sempre successiva alla data dell'intervento e che i km di scadenza siano superiori a quelli attuali.
- **❌ Elimina:** Mostra una richiesta di conferma prima di procedere. L'eliminazione è definitiva.

> 💡 **Tip:** Se hai registrato per errore un intervento con km sbagliati, usa Modifica invece di eliminare e reinserire — mantieni l'ID del record e non perdi il collegamento con eventuali scadenze predittive.

> ⚠️ **Effetto delle modifiche sullo storico:** Tutte le statistiche della Dashboard vengono ricalcolate in tempo reale ad ogni caricamento della pagina. Questo significa che modificare un vecchio record — in particolare il campo **Pieno/Parziale** — può influenzare i valori di Km/L dei rifornimenti successivi e i grafici dell'Efficienza per i mesi precedenti. È il comportamento corretto: l'app riflette sempre fedelmente i dati reali che hai inserito.

---

### 🔮 Tab Scadenze — Manutenzione Predittiva

Il tab **"🔮 Scadenze"** mostra solo gli interventi dello Storico che hanno almeno un campo scadenza compilato (Km o Data). È il sistema di **manutenzione predittiva** dell'app: non devi ricordarti nulla, ci pensa lui.

**Esempi tipici:** Tagliando ogni 15.000 km, Revisione entro il 15/06/2026, Bollo entro il 31/03/2026, Cambio gomme ogni 40.000 km.

**Come funziona la previsione intelligente:**
L'applicazione calcola la tua **media di utilizzo giornaliero** analizzando l'intero storico dei rifornimenti: `km medi al giorno = (km totali ultimo rifornimento − km totali primo rifornimento) ÷ giorni trascorsi`.

Con questa media, per ogni scadenza a km stima automaticamente la **data futura** in cui raggiungerai quel chilometraggio. Esempio: hai percorso in media 35 km/giorno, mancano 2.100 km al prossimo tagliando → la stima è **circa 60 giorni**. La stima viene mostrata in blu sulla card.

> 📌 **Nessuno storico rifornimenti disponibile?** Se hai inserito una scadenza prima di aver registrato almeno due rifornimenti, l'app non dispone dei dati sufficienti per calcolare la media giornaliera. In questo caso la stima della data comparirà come **"Non stimabile"** — la scadenza resta visibile e attiva, con il semaforo colorato corretto, ma senza la previsione temporale. Non appena avrai almeno due rifornimenti registrati, la stima apparirà automaticamente.

Le schede delle scadenze usano un sistema a **semaforo**:

| Bordo card | Condizione |
|---|---|
| 🟢 **Verde** | Scadenza lontana — tutto ok |
| 🟡 **Giallo** | Meno di 30 giorni **o** meno di 1.000 km al limite |
| 🔴 **Rosso** | Scadenza già superata (per data o per km) |

Se una scadenza è già scaduta e ne esiste un'altra identica più aggiornata (es. hai rifatto il tagliando e registrato il nuovo), l'app mostra automaticamente solo quella con la **priorità peggiore** (rosso batte giallo batte verde) per evitare duplicati e farti concentrare solo su ciò che conta.

**Azioni disponibili su ogni card:**
- **✅ Registra:** Apre un pannello per confermare che l'intervento è stato eseguito. Collega il record esistente e rimuove la scadenza superata.
- **❌ Rimuovi scadenza:** Elimina solo il campo scadenza dall'intervento (non cancella l'intervento dallo storico).

*[Placeholder Immagini: Scadenze Predittive]*

> 💡 **Tip:** La stima della data è tanto più precisa quanto più ricco è il tuo storico di rifornimenti. Con soli 2 rifornimenti la media è approssimativa; con 12 mesi di dati diventa molto affidabile.

---

### ⏰ Tab Promemoria — Routine Periodica

Il tab **"⏰ Promemoria"** gestisce i **controlli ricorrenti** che non hanno una data di scadenza fissa, ma che vanno eseguiti ogni tot km o ogni tot giorni. A differenza delle Scadenze (che sono legate a un singolo intervento già fatto), i Promemoria sono cicli continui che si resettano automaticamente dopo ogni esecuzione.

**Esempi tipici:** Controllo pressione gomme ogni 3.000 km, livello olio ogni 30 giorni, sostituzione filtro abitacolo ogni 15.000 km.

**Come creare un Promemoria:**
1. Apri il pannello **"➕ Crea Nuovo Promemoria"**
2. Scegli il tipo di trigger: **Chilometri** oppure **Tempo (Giorni)**
3. Seleziona la **Categoria** dall'elenco (voci personalizzabili dalle Impostazioni)
4. Inserisci la **frequenza** (es. ogni 10.000 km, oppure ogni 30 giorni)
5. Aggiungi una **nota fissa** opzionale (es. "Controllare a freddo") — comparirà sempre sulla card come promemoria
6. Clicca **Salva Promemoria**

L'app mostra immediatamente la stima del **prossimo controllo** (data o km) già durante la compilazione, prima ancora di salvare.

> ⚠️ **Nota Anti-Duplicati:** Non puoi avere due Promemoria attivi della stessa categoria. Se la categoria che cerchi non appare nell'elenco, significa che hai già un promemoria attivo per essa.

*[Placeholder Immagine: Promemoria]*

**Le card dei Promemoria** mostrano una barra di avanzamento che si riempie progressivamente man mano che percorri chilometri (o scorrono giorni) dall'ultimo reset. La card mostra sempre:
- 🏁 **Inserito:** il km (o la data) dell'ultimo reset
- 🎯 **Target:** il km (o la data) del prossimo controllo
- Il testo dello stato: *"Mancano X km alla scadenza"* oppure *"⚠️ Attenzione: limite superato da X km"* in rosso
- Le **note fisse** che hai inserito alla creazione

**Quando esegui il controllo:**
Clicca il pulsante **"Fatto"** sulla card. Si apre un pannello di conferma dove inserire:
- I **Km attuali** (precompilati con l'ultimo valore noto)
- La **Data di esecuzione** (precompilata con oggi)
- **Note opzionali** sull'intervento

Dopo aver cliccato **Conferma e Aggiorna**, il promemoria viene **resettato automaticamente**: la barra riparte da zero dal km/data attuale, pronta per il prossimo ciclo. L'esecuzione viene registrata internamente ma non aggiunge un record visibile nello Storico Manutenzioni.

**Altre azioni disponibili (menu ⚙️ in alto a destra della card):**
- **✏️ Modifica:** Cambia la frequenza (km o giorni) e le note del promemoria. Non puoi modificare la categoria, ma puoi mettere a 0 la frequenza che non ti serve.
- **✖️ Elimina:** Rimuove definitivamente il promemoria dalla lista attiva (con richiesta di conferma).

> 💡 **Tip:** La categoria di un promemoria viene presa dall'elenco che tu stesso puoi configurare in **⚙️ Impostazioni → Categorie Promemoria**. Se non trovi "Filtro Abitacolo" nell'elenco, aggiungila tu in pochi secondi — comparirà subito tra le opzioni disponibili!

---

## 5. ⚙️ Impostazioni e Gestione Dati

Questa sezione è il pannello di controllo avanzato. Troverai quattro schede: **Configurazioni**, **Esportazione Dati**, **Importazione Dati** e **Libretto Service**.

*[Placeholder Immagine: Impostazioni]*

---

### 🔧 Configurazioni — Parametri di Sicurezza e Comportamento

Questa scheda raccoglie tutti i parametri che influenzano direttamente come l'app convalida i dati, come li visualizza e come ti avvisa. Ogni modifica entra in vigore al clic del pulsante **"💾 Salva Configurazioni"** in fondo alla pagina.

---

#### 🎚️ Range Oscillazione Prezzo (€/L)

**Cosa fa:** Controlla l'ampiezza dello slider del prezzo carburante che compare nel form di inserimento manuale di un rifornimento. Lo slider si centra automaticamente sull'**ultimo prezzo pagato** e si estende di questo valore in entrambe le direzioni.

**Effetto visivo:** Se l'ultimo prezzo registrato è **1,859 €/L** e imposti un range di **0,15 €**, lo slider coprirà il range **1,709 – 2,009 €/L**. Questo rende l'inserimento più rapido nei giorni normali, perché puoi regolare con un trascinamento invece di digitare. Se il prezzo odierno è fuori da questo range (es. hai fatto il pieno all'estero), puoi comunque digitare il valore a mano nel campo numerico affiancato.

**Quando modificarlo:** Tienilo a `0,15 €` se usi sempre la stessa pompa o stazione. Alzalo a `0,20–0,30 €` se fai spesso rifornimenti in zone o paesi diversi dove il prezzo varia di più.

---

#### 💰 Tetto Massimo Spesa per Pieno (€)

**Cosa fa:** Definisce la soglia massima di costo che l'app considera "plausibile" per un singolo rifornimento. Questo parametro ha un effetto **duplice**:

1. **Nel form manuale:** Se inserisci un costo superiore al tetto, il form te lo permette ma potrebbe evidenziarlo. Utile per individuare subito uno zero di troppo (es. hai digitato `1500` invece di `150`).
2. **Nell'importazione Excel:** Qualsiasi riga del file con un costo superiore a questo valore viene automaticamente classificata come **Warning** nella tabella di anteprima — importabile, ma marcata in giallo per richiedere la tua revisione.

**Esempio pratico:** Con il tetto a `150 €`: una riga con costo `1500 €` evidenziata in giallo ti salta agli occhi subito; una riga con costo `200 €` ti viene segnalata come anomala; una riga da `148 €` passa senza warning.

**Quando modificarlo:** Alzalo a `250 €` o più se hai un veicolo a gasolio con serbatoio grande (furgoni, SUV) o se fai spesso rifornimenti completi a prezzi più alti. Non modificarlo per auto normali.

---

#### ⚠️ Soglia Allerta Parziali Cumulati (€)

**Cosa fa:** Tiene un contatore nascosto della **spesa totale accumulata** nei rifornimenti parziali consecutivi dall'ultimo pieno. Ogni volta che la dashboard si ricarica, confronta questo totale con la soglia configurata. Se la supera, mostra un avviso giallo direttamente nella Dashboard, in corrispondenza dell'ultimo rifornimento.

**Logica di calcolo:** L'app scorre i rifornimenti in ordine cronologico inverso (dal più recente al più vecchio). Somma i costi di tutti i rifornimenti parziali consecutivi finché non incontra un pieno — quel pieno fa da "azzeratore". Se la somma dei parziali supera la soglia, scatta l'alert.

**Esempio pratico:** Soglia a `80 €` — hai fatto tre rifornimenti parziali da 25 € (totale: 75 €): nessun avviso. Al quarto parziale da 10 € (totale: 85 €): compare in Dashboard il messaggio *"⚠️ Accumulo parziali: 85,00 €. Consigliato fare il pieno!"*. Non appena fai il pieno, il contatore si azzera.

**A cosa serve:** Un eccesso di rifornimenti parziali riduce la precisione del calcolo Km/L (l'algoritmo Full-to-Full funziona meglio con pieni completi frequenti). Questo avviso è un promemoria amichevole, non un blocco: puoi ignorarlo e continuare normalmente.

---

#### 📊 Limiti Importazione Excel

Questi quattro parametri avanzati governano la validazione automatica applicata **durante la verifica dei file importati**. Non influenzano l'inserimento manuale. Trovi questa sotto-sezione nella pagina Configurazioni, sotto un separatore dedicato.

Funzionano su due livelli di gravità distinti:
- **⚠️ Warning** (riga importabile, ma evidenziata in giallo): segnala un valore insolito che potresti voler verificare, ma non blocca l'importazione.
- **❌ Errore** (riga bloccata, non importabile): segnala un valore fisicamente impossibile. La riga non può essere salvata finché non viene corretta.

| Parametro | Default | Livello | Quando modificarlo |
|---|---|---|---|
| **Consumo Minimo km/L** | 4,0 | ⚠️ Warning | Abbassa a `2,0` per furgoni pesanti o veicoli ad alto consumo |
| **Consumo Massimo km/L** | 25,0 | ⚠️ Warning | Alza a `35` per auto ibride in ambito urbano molto efficienti |
| **Soglia Impossibile km/L** | 150 | ❌ Errore | Non modificare — nessun veicolo stradale supera questo valore |
| **Velocità Massima km/giorno** | 1.500 | ❌ Errore | Alza a `2.000` solo per autisti professionisti con turni molto lunghi |

**Come si calcola il consumo km/L durante l'importazione:** L'app prende ogni riga con stato "Pieno", trova il record immediatamente precedente (nel file o nel database) e calcola `(km attuali - km precedenti) / litri`. Se il precedente era un parziale, il check viene saltato per evitare falsi positivi. Se il precedente è un pieno (come dovrebbe essere), il calcolo viene fatto e confrontato con i 4 parametri sopra.

> 💡 **Tip:** Se importi dati di un'auto che hai cambiato (es. sei passato da un diesel a un'ibrida), aggiustare questi parametri ti aiuta a ricevere solo i warning davvero utili, evitando il rumore di segnalazioni irrilevanti.

---

#### 🏷️ Gestione Categorie

Questa sezione ti permette di personalizzare i menu a tendina che compariranno nel resto dell'app. Ci sono due elenchi separati:

**🔔 Categorie Promemoria:** Le voci selezionabili quando crei un nuovo Promemoria periodico (es. "Pressione Gomme", "Livello Olio", "Filtro Abitacolo"). Aggiungi, modifica o elimina le voci con i pulsanti ✏️ ed ❌ su ogni card.

**🔧 Categorie Manutenzione:** Le voci selezionabili nel campo "Categoria" quando aggiungi un intervento allo storico, e anche nella colonna "Tipo Intervento" durante l'importazione Excel. Assicurati che i nomi qui corrispondano esattamente a quelli nei tuoi file Excel, altrimenti le righe importate potrebbero non essere riconosciute correttamente.

> 💡 **Cosa succede agli interventi passati se elimino una categoria?** Eliminare una categoria dalla lista la rimuove solo dai **menu a tendina** per i nuovi inserimenti. Gli interventi già registrati nello Storico Manutenzioni che usavano quella categoria restano intatti nel database — nessun dato storico viene perso. La categoria eliminata non comparirà più come filtro nel tab Storico, ma tutti i record che la usavano rimangono perfettamente visibili e consultabili.

> ⚠️ **Importante:** Ricordati sempre di cliccare **"💾 Salva Configurazioni"** dopo aver modificato le categorie. Le modifiche non vengono salvate automaticamente finché non si clicca questo pulsante.

---

### 📤 Esportazione Dati

Con un clic puoi scaricare un backup completo dei tuoi dati in formato **Excel (.xlsx)**. Il file include due fogli:
- **Foglio "Rifornimenti"**: tutto lo storico dei pieni, con date, km, litri, prezzi, costi e note.
- **Foglio "Manutenzione"**: tutti gli interventi registrati.

Questo file è anche il formato ideale per **importazioni massive**: puoi scaricarlo, modificare liberamente i dati (es. correggere prezzi vecchi, aggiungere righe mancanti) e ricaricarlo tramite la scheda Importazione Dati.

---

### 📄 Libretto Service (PDF)

Genera un documento PDF ufficiale con lo storico delle manutenzioni. Puoi scegliere di includere **tutti gli anni** o filtrare per un anno specifico. Il PDF è pensato per essere stampato oppure conservato digitalmente insieme ai documenti del veicolo.

> 💡 **Tip:** Il Libretto Service PDF è disponibile solo se hai registrato almeno un intervento di manutenzione.

---

### 📥 Importazione Massiva — Flusso Completo

L'importazione è il modo più rapido per portare dentro FuelPyTracker anni di storico in pochi minuti. Segui questo flusso sicuro:

*[Placeholder Immagine: Importazione Dati]*

#### Passo 1 — Scarica il Modello (se non hai un file)

Apri il pannello **"❓ Non hai un file? Scarica il modello"** e clicca **"📥 Scarica Modello .xlsx"**. Ricevi un file Excel vuoto con già le intestazioni corrette, pronto da compilare.

#### Passo 2 — Compila il File

Regole fondamentali per compilare il file senza errori:

| Campo | Formato Corretto | ⚠️ Errori Comuni |
|---|---|---|
| **Data** | `GG/MM/AAAA` (es. `25/12/2023`) | Non usare formati americani (MM/DD/YYYY) |
| **Km** | Numero intero (es. `125000`) | Non usare punti come separatori di migliaia |
| **Prezzo** | Decimale con punto o virgola (es. `1.859` o `1,859`) | — |
| **Costo** | Decimale con punto o virgola (es. `75.50`) | — |
| **Pieno** | Scrivi `Sì` oppure lascia vuoto per "Sì" | Usa solo Sì/No, non True/False |
| **Note** | Testo libero | — |

> ⚠️ **Importante:** Non modificare i nomi delle colonne nella prima riga. L'app li usa per riconoscere i dati. Puoi rinominare il file come vuoi, ma non le intestazioni.

#### Passo 3 — Carica il File

Trascina il file nella zona di upload oppure cliccaci sopra per selezionarlo. Sono supportati sia `.xlsx` che `.csv`.

#### Passo 4 — Leggi la Tabella di Validazione

Questa è la fase più importante. Prima di salvare qualsiasi dato, l'app li analizza tutti e ti mostra una **tabella di anteprima** con ogni riga colorata in base al suo stato:

| Stato | Sigla | Cosa significa | Cosa fare |
|---|---|---|---|
| ✅ **Invariato** | bianco | Record già presente nel database, identico | Niente, verrà ignorato |
| 🔵 **Nuovo** | blu | Record nuovo, pronto per essere salvato | Controlla e conferma |
| 🟡 **Warning** | giallo | Record importabile ma con anomalia segnalata | Leggi la nota, poi decidi |
| 🟠 **Modifica** | arancione | Record esistente con valori diversi (es. prezzo corretto) | Controlla le differenze |
| 🔴 **Errore** | rosso | Record bloccato, non può essere salvato così com'è | Leggi la nota e correggi |

**Tipi di errori più comuni e come correggerli:**

- `"Data invalida"` → Il formato della data è sbagliato. Correggi la cella e ricarica il file.
- `"Data nel futuro"` → Hai inserito una data successiva a oggi.
- `"Km ≤ del GG/MM/AAAA (XXXXX)"` → I km di questa riga sono minori o uguali al rifornimento precedente in storico. Controlla il valore dell'odometro.
- `"Data già presente (ID: X)"` → Esiste già un rifornimento registrato in questa data con km diversi. Per aggiornarne i valori (es. correggere il prezzo), usa lo stato "Modifica" oppure abbina la riga ai km esatti del record originale.
- `"Spesa > 150 €"` → Superato il tetto massimo configurato nelle impostazioni (Warning, non errore bloccante).
- `"Consumo anomalo: X,X km/L (range atteso: Y–Z)"` → Warning: il consumo calcolato è fuori dal range normale che hai configurato. Potrebbe essere corretto (es. un viaggio in autostrada con vento contrario) oppure un errore di digitazione.
- `"Consumo impossibile: X,X km/L"` → Errore bloccante: il valore è fisicamente impossibile per qualsiasi veicolo. Quasi certamente c'è un errore nei km o nei litri.
- `"Velocità impossibile: X km/giorno"` → Errore bloccante: i km percorsi tra due rifornimenti sono troppi per il numero di giorni trascorsi.

#### Passo 5 — Correggi gli Errori Direttamente in Tabella

Non devi riaprire Excel! La tabella di anteprima è **editabile direttamente nell'app**. Clicca su una cella con un valore sbagliato, modificala, e premi **Invio**. La validazione si aggiorna istantaneamente.

> 💡 **Tip:** Le righe in stato **Errore** non verranno mai salvate, anche se clicchi Conferma. Correggi tutti gli errori prima di procedere, oppure ignorali consapevolmente — solo le righe Nuovo, Warning e Modifica vengono salvate.

#### Passo 6 — Conferma l'Importazione

Quando sei soddisfatto della revisione, clicca il pulsante **"Conferma Importazione"**. Solo le righe con stato **Nuovo**, **Warning** e **Modifica** vengono salvate. Le righe **Errore** e **Invariato** vengono ignorate silenziosamente.

Vuoi ricominciare con un file diverso? Clicca **"🔄 Pulisci tutto e carica altro file"**.

---

## 6. 👤 Profilo Utente

La sezione **Profilo** mostra una card riepilogativa con la tua email, la data di iscrizione e l'ora dell'ultimo accesso. Da qui puoi gestire tre aspetti del tuo account tramite altrettante schede:

---

### 📷 Foto Profilo

Carica un'immagine personalizzata che comparirà come avatar. Sono supportati i formati **JPG** e **PNG**. Dopo il caricamento l'immagine viene aggiornata in tempo reale senza ricaricare la pagina. Se non hai ancora caricato una foto, l'app usa un avatar generato automaticamente con le tue iniziali.

---

### 📧 Modifica Email

Puoi cambiare l'indirizzo email associato al tuo account. Il flusso è il seguente:
1. Inserisci il **nuovo indirizzo** nel campo apposito e clicca **Invia**.
2. Riceverai una **email di conferma** al nuovo indirizzo: dovrai cliccare il link contenuto per completare la modifica.
3. Finché non hai confermato, il tuo accesso continua a funzionare con l'email attuale — nessuna interruzione di servizio.

> ⚠️ **Attenzione:** Se perdi accesso anche alla nuova email prima di confermare, il cambio non va a buon fine e puoi ritentare dal profilo.

---

### 🔐 Sicurezza — Cambio Password

Per motivi di sicurezza, per cambiare password è richiesta anche la **password attuale** come conferma dell'identità. Inserisci:
- **Password Attuale** (obbligatoria)
- **Nuova Password** (minimo 6 caratteri)
- **Conferma Nuova Password** (deve coincidere)

Se la password attuale è errata, l'operazione viene rifiutata. Se le due nuove password non coincidono, riceverai un messaggio d'errore prima di qualsiasi modifica.

> 💡 **Tip:** Usa una password con almeno 8 caratteri, che combini lettere maiuscole, minuscole, numeri e un simbolo. Le password sono conservate in forma cifrata: nemmeno gli amministratori dell'app possono vederle in chiaro.

---

## Appendice — Domande Frequenti

**D: Posso usare FuelPyTracker su smartphone?**
R: Sì! L'interfaccia si adatta automaticamente agli schermi mobile. Lo scanner AI degli scontrini su mobile ti permette persino di scattare la foto direttamente dalla fotocamera del telefono.

**D: Cosa succede se inserisco per errore un km sbagliato?**
R: Vai alla sezione **⛽ Rifornimenti → 🛠️ Gestione**, seleziona il record dall'elenco e clicca **"✏️ Modifica"**. Puoi correggere qualsiasi campo.

**D: Perché il mio "Stato Salute" è basso anche se ho fatto tutto?**
R: Probabilmente hai delle voci nella sezione **⏰ Promemoria** che non sono state resettate. Apri il Check-Up Salute dalla Dashboard per vedere l'elenco esatto degli elementi penalizzanti.

**D: Posso avere più di un rifornimento per giorno?**
R: L'inserimento manuale dal form lo accetta senza problemi, purché i km siano strettamente progressivi (es. due pieni in due stazioni diverse nello stesso giorno di viaggio). Durante l'importazione Excel, se una data è già presente nel database con km diversi, la riga viene marcata come errore — in quel caso, o correggi i km per farli combaciare con il record esistente e usa lo stato "Modifica", oppure inserisci il secondo rifornimento manualmente dal form dopo l'importazione.

**D: Il file PDF del Libretto Service è adatto per il collaudo?**
R: Il documento è pensato come resoconto personale e non ha valore legale certificato. Per la revisione portate sempre il libretto di manutenzione originale del veicolo.

---

*Ultima revisione: Aprile 2026 — FuelPyTracker v1.0.0*

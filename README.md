⛽ FuelPyTracker
===============

### Advanced Vehicle Cost & Efficiency Management System


📋 Abstract
-----------

**FuelPyTracker** è un'applicazione web full-stack progettata per digitalizzare, monitorare e trasformare i costi di gestione di un veicolo privato in metriche azionabili. Nato come evoluzione digitale del taccuino da cruscotto, il sistema combina un'architettura modulare in Python, la robustezza di un database relazionale in cloud e un'interfaccia reattiva mobile-first.

Il progetto non si limita all'archiviazione: è un motore di analisi che calcola consumi reali, monitora l'inflazione dei carburanti e abilita la manutenzione predittiva. Rappresenta un caso di studio completo di ingegneria del software, coprendo l'intero ciclo: dalla progettazione dei dati con **SQLAlchemy** al deployment su infrastruttura **Serverless**.

💡 Project Philosophy & Vision
------------------------------

Molti strumenti di gestione auto sono frammentari o "black-box". FuelPyTracker colma il divario tra sovranità dei dati e potenza di calcolo.

*   **Monolite Modulare:** Invece di una prematura frammentazione in microservizi, l'architettura è un monolite coeso ma rigorosamente stratificato.
    
*   **Separation of Concerns (SoC):** La logica di business è disaccoppiata dall'UI e dal Data Layer. Questo permette di evolvere componenti critici senza riscrivere l'applicazione.
    
*   **Data Sovereignty:** Totale controllo sui propri dati storici, senza lock-in proprietari.
    

⚙️ Technical Architecture
-------------------------

Il sistema è sviluppato in **Python 3.11+**, sfruttando un ecosistema open-source maturo per garantire affidabilità.

### 1\. Frontend Layer: Streamlit "App-like"

L'interfaccia è realizzata con **Streamlit**, ottimizzata pesantemente per l'uso in mobilità.

*   **Layout Fluidi:** Adattamento automatico al viewport del dispositivo.
    
*   **State Management:** Gestione avanzata dello stato di sessione per minimizzare i reload e mantenere la persistenza dei dati durante la navigazione.
    
*   **Touch Optimization:** Controlli dimensionati per l'interazione da smartphone.
    

### 2\. Business Logic Layer

Questo layer contiene funzioni pure che operano su oggetti di dominio. È completamente agnostico rispetto al database o all'interfaccia grafica, facilitando il testing unitario degli algoritmi di calcolo.

### 3\. Data Access Layer: SQLAlchemy ORM

L'interazione con i dati avviene tramite **SQLAlchemy**.

*   **Sicurezza:** Prevenzione nativa della SQL Injection.
    
*   **Astrazione:** Uso di modelli dichiarativi e sessioni gestite automaticamente.
    
*   **Robustezza:** Rollback automatico delle transazioni in caso di errori di runtime.
    

### 4\. Cloud Infrastructure: Supabase (PostgreSQL)

Il persistency layer è affidato a **Supabase**. L'applicazione gestisce specificamente il _Transaction Pooling_ per supportare le connessioni effimere tipiche degli ambienti serverless come Streamlit Cloud, evitando l'esaurimento delle connessioni al database.

🧮 Key Algorithmic Features
---------------------------

FuelPyTracker implementa logiche di validazione che superano i comuni fogli di calcolo.

### ⛽ Full-to-Full Consumption Logic

Il calcolo del consumo medio non è una media aritmetica semplice. L'algoritmo distingue tra rifornimenti "Parziali" e "Pieni". Il sistema consolida il consumo (Km/L) solo al raggiungimento del pieno, aggregando correttamente i chilometri e i litri dei rifornimenti parziali intermedi. Questo garantisce la correttezza scientifica del dato.

### 🥪 Sandwich Data Validation

Per mitigare l'errore umano nel data entry (es. typos nel chilometraggio), è stato implementato un algoritmo di validazione temporale.Prima di accettare un record, il sistema verifica che il chilometraggio $K\_{new}$ soddisfi la condizione:

$$K\_{prev} < K\_{new} < K\_{next}$$

Dove $K\_{prev}$ e $K\_{next}$ sono rispettivamente i record cronologicamente adiacenti. Questo previene la corruzione della serie storica.
   
*   **Ghost Records:** Logica di pulizia in fase di importazione per identificare e scartare righe corrotte o vuote tipiche degli export CSV/Excel.
    

📊 UX & Analytics
-----------------

L'interfaccia segue il principio **Information at a Glance**:

*   **KPI Visivi:** Costo Totale, Costo/Km ed Efficienza media visibili immediatamente.
    
*   **Grafici Interattivi (Plotly):** Analisi deep-dive con zoom temporali per correlare l'inflazione carburante al costo di gestione o analizzare la stagionalità dei consumi.
    

🛠️ Project Structure
---------------------

L'organizzazione del codice riflette la natura professionale del progetto:

*   **src/**: Root del codice sorgente.
    
    *   **src/database/**: Contiene la configurazione del motore SQLAlchemy (core.py), i modelli ORM (models.py) e le funzioni CRUD (crud.py).
        
    *   **src/services/**: Contiene la logica pura di calcolo e validazione.
        
    *   **src/ui/**: Suddiviso in pages (le viste principali) e components (elementi riutilizzabili come grafici o form).
        
*   **.streamlit/**: Configurazioni specifiche del framework.
    
*   **scripts/**: Utilità per la manutenzione, come lo script di generazione dati di test.

🚀 Roadmap (v2.0)
-----------------

Il progetto è in continua evoluzione. I prossimi passi includono:

*   \[ \] **Auth Layer:** Sistema multi-tenant con login sicuro.
    
*   \[ \] **OCR Module:** Integrazione Computer Vision per la scansione automatica degli scontrini.
    
*   \[ \] **Advanced Reporting:** Export PDF per reportistica fiscale o certificazione di vendita.
    
*   \[ \] **Weather API:** Correlazione tra consumi ed eventi meteorologici.
    

📄 License
----------

Distribuito sotto licenza **MIT**. Il codice è aperto a scopi educativi per lo studio di architetture Python moderne.

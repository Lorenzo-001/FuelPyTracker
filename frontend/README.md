# 💻 FuelPyTracker — Frontend Client (V2.0)

> **Single Page Application reattiva per il tracciamento del veicolo, sviluppata con React 19, TypeScript, Vite e Tailwind CSS.**

---

## 🚀 Script Disponibili

Dalla cartella `frontend/`:

- `npm run dev`: Avvia il server di sviluppo locale con Hot Module Replacement (HMR) su `http://localhost:5173`.
- `npm run build`: Compila l'applicazione per la produzione e verifica i tipi con `tsc -b`.
- `npm run preview`: Avvia un server locale per visualizzare l'anteprima della build di produzione.
- `npm run lint`: Esegue il linter ultrarapido `oxlint` sui file TypeScript e TSX.

---

## 📂 Struttura del Progetto

```
frontend/src/
├── components/          # Componenti riutilizzabili (modali, selector, layout, forms)
│   ├── auth/            # Form di login, registrazione e recupero credenziali
│   ├── dashboard/       # KPI cards, grafici temporali, calcolatore viaggio
│   ├── fuel/            # Modali e tabelle rifornimenti, Smart OCR dialog
│   ├── layout/          # Navbar desktop, bottom navigation mobile, theme selector
│   ├── maintenance/     # Gestione tagliandi, scadenze e form interventi
│   ├── reminders/       # Scadenziario controlli periodici
│   ├── reports/         # Pipeline di importazione e generatore libretto PDF
│   └── settings/        # Schede configurazione profilo veicolo e sicurezza
├── context/             # React Context (AuthContext, ThemeContext)
├── hooks/               # Custom hooks per data fetching e mutazioni (TanStack Query)
├── lib/                 # Utility condivise, client API axios/fetch, parser
├── pages/               # Pagine principali dell'applicazione
└── types/               # Definizioni TypeScript e contratti di dominio
```

---

## 🎨 Temi e Anti-Flicker Boot

L'applicazione supporta tre temi grafici nativi:
- `dark` (Dark Slate)
- `black` (OLED Pure Black)
- `light` (Clean Light)

All'avvio, un micro-script inline presente in `index.html` legge la preferenza salvata in `localStorage` e assegna la classe corrispondente all'elemento radice prima del primo ciclo di render React, eliminando qualsiasi sfarfallio bianco (*Flash of Unstyled Content*).

Per maggiori dettagli sull'architettura complessiva, consulta la documentazione in [`docs/architecture/FRONTEND.md`](../docs/architecture/FRONTEND.md).

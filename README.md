# Gestionale Edile

Applicazione Streamlit per la gestione di una piccola impresa edile (pensata
per 1-2 operai): cantieri, manodopera, costi, scadenze e fatture.

## Funzionalità

- **Cantieri** — anagrafica cantiere, preventivo, stato avanzamento lavori (SAL), calcolo del margine
- **Operai** — anagrafica con costo orario aziendale
- **Ore lavorate** — registrazione ore per cantiere, con calcolo automatico del costo manodopera
- **Costi** — materiali, noleggi, subappalti per cantiere
- **Scadenze** — DURC, revisioni mezzi, ecc., con vista sulle scadenze imminenti
- **Fatture** — emissione e riepilogo per cantiere
- **Dashboard** — margine per cantiere e scadenze in arrivo

## Struttura del progetto

```
.
├── app.py                 # interfaccia Streamlit
├── gestionale_edile.py    # modelli (dataclass) e logica di business
├── requirements.txt
└── README.md
```

La logica è separata dall'interfaccia: `gestionale_edile.py` può essere
importato e testato indipendentemente da Streamlit.

## Requisiti

- Python 3.10+ (per via delle annotazioni `list[...]` / `dict[...]`)

## Installazione

```bash
git clone <url-del-repo>
cd <nome-repo>
python3 -m venv venv
source venv/bin/activate      # su Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Avvio

```bash
streamlit run app.py
```

L'app si apre di default su `http://localhost:8501`. Dalla sidebar puoi
caricare dei dati di esempio ("Carica dati di esempio") per esplorare subito
le funzionalità, o ripartire da zero ("Svuota tutto").

## Note

- I dati vivono in `st.session_state`: si perdono al riavvio dell'app. Non
  c'è ancora persistenza su file o database — è la prossima estensione
  naturale (es. SQLite o un file JSON caricato/salvato a ogni sessione).
- `gestionale_edile.py` contiene anche una funzione `demo()` eseguibile da
  riga di comando (`python3 gestionale_edile.py`) per un esempio testuale
  indipendente da Streamlit.

## Possibili sviluppi futuri

- Persistenza dati (SQLite/JSON)
- Gestione fornitori e mezzi dall'interfaccia (i modelli esistono già)
- Export PDF/Excel di preventivi e riepiloghi cantiere
- Autenticazione multi-utente

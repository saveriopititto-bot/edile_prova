"""
Interfaccia Streamlit per il gestionale di una piccola impresa edile.

Esegui con:
    streamlit run app.py

Richiede il file gestionale_edile.py nella stessa cartella.
"""

import os
from datetime import date

import streamlit as st
import streamlit.components.v1 as components

from gestionale_edile import (
    Cantiere,
    Fattura,
    GestionaleEdile,
    Operaio,
    OreLavorate,
    Scadenza,
    StatoCantiere,
    TipoCosto,
    VoceCosto,
)

st.set_page_config(page_title="Gestionale Edile", page_icon="🏗️", layout="wide")


def get_gestionale() -> GestionaleEdile:
    if "gestionale" not in st.session_state:
        st.session_state.gestionale = GestionaleEdile()
    return st.session_state.gestionale


def next_id(d: dict) -> int:
    return max(d.keys(), default=0) + 1


def carica_dati_esempio(g: GestionaleEdile) -> None:
    mario = Operaio(id=1, nome="Mario", cognome="Rossi",
                     costo_orario=18.50, data_assunzione=date(2022, 3, 1))
    luigi = Operaio(id=2, nome="Luigi", cognome="Bianchi",
                     costo_orario=16.00, data_assunzione=date(2023, 6, 12))
    g.operai = {1: mario, 2: luigi}

    cantiere = Cantiere(id=1, nome="Ristrutturazione Via Roma 12",
                         cliente="Condominio Via Roma 12",
                         indirizzo="Via Roma 12, Gualdo Tadino (PG)",
                         stato=StatoCantiere.IN_CORSO, preventivo=25000.0,
                         sal_percentuale=40.0)
    g.nuovo_cantiere(cantiere)
    g.registra_ore_operaio(1, OreLavorate(operaio_id=1, data=date(2026, 9, 15), ore=8))
    g.registra_ore_operaio(1, OreLavorate(operaio_id=2, data=date(2026, 9, 15), ore=8))
    cantiere.aggiungi_costo(VoceCosto(tipo=TipoCosto.MATERIALE, descrizione="Cemento e laterizi",
                                       importo=1200.0, data=date(2026, 9, 15)))
    g.scadenze.append(Scadenza(descrizione="DURC", data_scadenza=date(2026, 10, 5)))
    g.emetti_fattura(Fattura(id=1, cantiere_id=1, numero="2026/014",
                              data_emissione=date(2026, 9, 18), importo=10000.0))


gestionale = get_gestionale()

st.title("🏗️ Gestionale Impresa Edile")

with st.sidebar:
    st.markdown("### Dati")
    if st.button("Carica dati di esempio"):
        carica_dati_esempio(gestionale)
        st.rerun()
    if st.button("Svuota tutto"):
        st.session_state.gestionale = GestionaleEdile()
        st.rerun()

tab_dashboard, tab_operai, tab_cantieri, tab_materiali, tab_scadenze, tab_fatture, tab_mobile = st.tabs(
    ["📊 Dashboard", "👷 Operai", "🏠 Cantieri", "🧱 Materiali", "⏰ Scadenze", "🧾 Fatture", "📱 App Mobile"]
)

# ---------------------------------------------------------------------------
# OPERAI
# ---------------------------------------------------------------------------
with tab_operai:
    st.subheader("Operai")

    with st.form("nuovo_operaio", clear_on_submit=True):
        col1, col2, col3 = st.columns(3)
        nome = col1.text_input("Nome")
        cognome = col2.text_input("Cognome")
        costo_orario = col3.number_input("Costo orario (EUR)", min_value=0.0, step=0.5)
        data_assunzione = st.date_input("Data assunzione", value=date.today())
        if st.form_submit_button("Aggiungi operaio") and nome and cognome:
            oid = next_id(gestionale.operai)
            gestionale.operai[oid] = Operaio(
                id=oid, nome=nome, cognome=cognome,
                costo_orario=costo_orario, data_assunzione=data_assunzione,
            )
            st.success(f"Operaio {nome} {cognome} aggiunto (id {oid})")

    if gestionale.operai:
        st.table([
            {"ID": o.id, "Nome": o.nome, "Cognome": o.cognome,
             "Costo orario (EUR)": o.costo_orario, "Assunto il": o.data_assunzione}
            for o in gestionale.operai.values()
        ])
    else:
        st.info("Nessun operaio inserito.")

# ---------------------------------------------------------------------------
# CANTIERI
# ---------------------------------------------------------------------------
with tab_cantieri:
    st.subheader("Cantieri")

    with st.expander("➕ Nuovo cantiere"):
        with st.form("nuovo_cantiere", clear_on_submit=True):
            nome_c = st.text_input("Nome cantiere")
            cliente = st.text_input("Cliente")
            indirizzo = st.text_input("Indirizzo")
            preventivo = st.number_input("Preventivo (EUR)", min_value=0.0, step=100.0)
            if st.form_submit_button("Crea cantiere") and nome_c:
                cid = next_id(gestionale.cantieri)
                gestionale.nuovo_cantiere(Cantiere(
                    id=cid, nome=nome_c, cliente=cliente, indirizzo=indirizzo,
                    stato=StatoCantiere.IN_CORSO, preventivo=preventivo,
                ))
                st.success(f"Cantiere '{nome_c}' creato (id {cid})")

    if not gestionale.cantieri:
        st.info("Nessun cantiere inserito.")
    else:
        cantiere_id = st.selectbox(
            "Seleziona cantiere", options=list(gestionale.cantieri.keys()),
            format_func=lambda cid: gestionale.cantieri[cid].nome,
        )
        cantiere = gestionale.cantieri[cantiere_id]

        col1, col2, col3 = st.columns(3)
        col1.metric("Preventivo", f"{cantiere.preventivo:,.2f} EUR")
        col2.metric("Costo totale", f"{cantiere.costo_totale():,.2f} EUR")
        col3.metric("Margine", f"{cantiere.margine():,.2f} EUR")

        cantiere.sal_percentuale = st.slider(
            "SAL (%)", 0, 100, int(cantiere.sal_percentuale), key=f"sal_{cantiere_id}"
        )

        st.markdown("#### Registra ore lavorate")
        if gestionale.operai:
            with st.form(f"ore_{cantiere_id}", clear_on_submit=True):
                op_id = st.selectbox(
                    "Operaio", options=list(gestionale.operai.keys()),
                    format_func=lambda oid: f"{gestionale.operai[oid].nome} {gestionale.operai[oid].cognome}",
                )
                data_ore = st.date_input("Data", value=date.today(), key=f"data_ore_{cantiere_id}")
                ore_val = st.number_input("Ore", min_value=0.0, max_value=24.0, step=0.5)
                if st.form_submit_button("Registra ore"):
                    gestionale.registra_ore_operaio(
                        cantiere_id, OreLavorate(operaio_id=op_id, data=data_ore, ore=ore_val)
                    )
                    st.success("Ore registrate: costo manodopera calcolato in automatico")
        else:
            st.warning("Aggiungi prima almeno un operaio.")

        st.markdown("#### Aggiungi costo (materiali, noleggi, subappalti...)")
        with st.form(f"costo_{cantiere_id}", clear_on_submit=True):
            tipo = st.selectbox("Tipo", options=list(TipoCosto), format_func=lambda t: t.name.title())
            descrizione = st.text_input("Descrizione")
            importo = st.number_input("Importo (EUR)", min_value=0.0, step=10.0)
            if st.form_submit_button("Aggiungi costo"):
                cantiere.aggiungi_costo(VoceCosto(
                    tipo=tipo, descrizione=descrizione, importo=importo, data=date.today(),
                ))
                st.success("Costo aggiunto")

        if cantiere.costi:
            st.markdown("#### Costi registrati")
            st.table([
                {"Tipo": c.tipo.name, "Descrizione": c.descrizione,
                 "Importo (EUR)": c.importo, "Data": c.data}
                for c in cantiere.costi
            ])

# ---------------------------------------------------------------------------
# MATERIALI ACQUISTATI
# ---------------------------------------------------------------------------
with tab_materiali:
    st.subheader("Materiali Acquistati")

    if gestionale.cantieri:
        with st.form("nuovo_materiale", clear_on_submit=True):
            st.markdown("#### Aggiungi nuovo materiale")
            cid_m = st.selectbox(
                "Cantiere di destinazione", options=list(gestionale.cantieri.keys()),
                format_func=lambda cid: gestionale.cantieri[cid].nome, key="materiale_cantiere",
            )
            descrizione_m = st.text_input("Descrizione materiale")
            importo_m = st.number_input("Importo (EUR)", min_value=0.0, step=10.0)
            data_m = st.date_input("Data acquisto", value=date.today())
            if st.form_submit_button("Registra acquisto") and descrizione_m:
                gestionale.cantieri[cid_m].aggiungi_costo(VoceCosto(
                    tipo=TipoCosto.MATERIALE, descrizione=descrizione_m, importo=importo_m, data=data_m,
                ))
                st.success(f"Acquisto registrato per il cantiere: {gestionale.cantieri[cid_m].nome}")

        st.markdown("#### Elenco materiali acquistati")
        tutti_materiali = []
        for cid, cantiere in gestionale.cantieri.items():
            for costo in cantiere.costi:
                if costo.tipo == TipoCosto.MATERIALE:
                    tutti_materiali.append({
                        "Data": costo.data,
                        "Cantiere": cantiere.nome,
                        "Descrizione": costo.descrizione,
                        "Importo (EUR)": costo.importo,
                    })
        
        if tutti_materiali:
            # Ordiniamo per data decrescente
            tutti_materiali.sort(key=lambda x: x["Data"], reverse=True)
            st.table(tutti_materiali)
        else:
            st.info("Nessun materiale registrato.")
    else:
        st.warning("Aggiungi prima almeno un cantiere per poter registrare i materiali.")

# ---------------------------------------------------------------------------
# SCADENZE
# ---------------------------------------------------------------------------
with tab_scadenze:
    st.subheader("Scadenze")

    with st.form("nuova_scadenza", clear_on_submit=True):
        descr = st.text_input("Descrizione (es. DURC, Cassa Edile, Revisione mezzo)")
        data_scad = st.date_input("Data scadenza")
        if st.form_submit_button("Aggiungi scadenza"):
            gestionale.scadenze.append(Scadenza(descrizione=descr, data_scadenza=data_scad))
            st.success("Scadenza aggiunta")

    entro = st.slider("Mostra scadenze entro (giorni)", 7, 180, 30)
    imminenti = gestionale.scadenze_imminenti(entro)
    if imminenti:
        st.table([{"Descrizione": s.descrizione, "Scadenza": s.data_scadenza} for s in imminenti])
    else:
        st.info("Nessuna scadenza imminente.")

# ---------------------------------------------------------------------------
# FATTURE
# ---------------------------------------------------------------------------
with tab_fatture:
    st.subheader("Fatture")

    if gestionale.cantieri:
        with st.form("nuova_fattura", clear_on_submit=True):
            cid_f = st.selectbox(
                "Cantiere", options=list(gestionale.cantieri.keys()),
                format_func=lambda cid: gestionale.cantieri[cid].nome, key="fattura_cantiere",
            )
            numero = st.text_input("Numero fattura")
            importo_f = st.number_input("Importo (EUR)", min_value=0.0, step=100.0)
            if st.form_submit_button("Emetti fattura"):
                fid = next_id(gestionale.fatture)
                gestionale.emetti_fattura(Fattura(
                    id=fid, cantiere_id=cid_f, numero=numero,
                    data_emissione=date.today(), importo=importo_f,
                ))
                st.success(f"Fattura {numero} emessa")

        if gestionale.fatture:
            st.table([
                {"Numero": f.numero, "Cantiere": gestionale.cantieri[f.cantiere_id].nome,
                 "Importo (EUR)": f.importo, "Emessa il": f.data_emissione,
                 "Stato": "Pagata" if f.pagata else "Da incassare"}
                for f in gestionale.fatture.values()
            ])
    else:
        st.warning("Crea prima almeno un cantiere.")

# ---------------------------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------------------------
with tab_dashboard:
    st.subheader("Dashboard")

    if gestionale.cantieri:
        col1, col2 = st.columns(2)
        col1.metric("Cantieri attivi", len(gestionale.cantieri))
        col2.metric("Scadenze entro 30gg", len(gestionale.scadenze_imminenti(30)))

        st.markdown("#### Margine per cantiere")
        st.table([
            {"Cantiere": gestionale.cantieri[cid].nome, "Margine (EUR)": margine}
            for cid, margine in gestionale.margine_per_cantiere().items()
        ])
    else:
        st.info("Nessun dato ancora. Inizia aggiungendo operai e un cantiere.")

# ---------------------------------------------------------------------------
# APP MOBILE (ANTEPRIMA)
# ---------------------------------------------------------------------------
with tab_mobile:
    st.subheader("Anteprima App Mobile")
    st.markdown("Simulatore dell'interfaccia mobile (Vue.js standalone).")
    
    html_path = "mobile_app.html"
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir, html_path)
    
    if os.path.exists(full_path):
        with open(full_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        
        # Mettiamo l'app in una colonna centrale per simulare la larghezza di uno smartphone
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.markdown(
                """
                <style>
                .mobile-container {
                    border: 12px solid #201e1d;
                    border-radius: 36px;
                    overflow: hidden;
                    box-shadow: 0 10px 20px rgba(0,0,0,0.2);
                    padding: 0;
                    margin: 0 auto;
                }
                </style>
                """, unsafe_allow_html=True
            )
            st.markdown('<div class="mobile-container">', unsafe_allow_html=True)
            components.html(html_content, height=800, scrolling=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning(f"File {html_path} non trovato.")

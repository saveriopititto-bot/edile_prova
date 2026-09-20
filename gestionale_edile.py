"""
Struttura di massima per un gestionale di una piccola impresa edile (2 operai).

Skeleton architetturale: classi, relazioni e metodi principali.
I metodi contrassegnati con TODO vanno implementati in base alle regole
di business specifiche (es. calcolo automatico dei costi manodopera,
regole di fatturazione SAL, ecc.).
"""

from dataclasses import dataclass, field
from datetime import date
from enum import Enum, auto
from typing import Optional


# ---------------------------------------------------------------------------
# ENUM / STATI
# ---------------------------------------------------------------------------

class StatoCantiere(Enum):
    PREVENTIVO = auto()
    IN_CORSO = auto()
    SOSPESO = auto()
    CONCLUSO = auto()
    FATTURATO = auto()


class TipoCosto(Enum):
    MANODOPERA = auto()
    MATERIALE = auto()
    NOLEGGIO = auto()
    SUBAPPALTO = auto()
    ALTRO = auto()


# ---------------------------------------------------------------------------
# ANAGRAFICHE
# ---------------------------------------------------------------------------

@dataclass
class Operaio:
    id: int
    nome: str
    cognome: str
    costo_orario: float                     # costo aziendale, non paga netta
    data_assunzione: date
    idoneita_sanitaria_scadenza: Optional[date] = None
    dpi_consegnati: list[str] = field(default_factory=list)


@dataclass
class Fornitore:
    id: int
    ragione_sociale: str
    piva: str
    referente: Optional[str] = None


@dataclass
class Mezzo:
    id: int
    descrizione: str
    revisione_scadenza: Optional[date] = None


# ---------------------------------------------------------------------------
# CANTIERE / COMMESSA — il cuore del sistema
# ---------------------------------------------------------------------------

@dataclass
class VoceCosto:
    tipo: TipoCosto
    descrizione: str
    importo: float
    data: date


@dataclass
class OreLavorate:
    operaio_id: int
    data: date
    ore: float


@dataclass
class Cantiere:
    id: int
    nome: str
    cliente: str
    indirizzo: str
    stato: StatoCantiere = StatoCantiere.PREVENTIVO
    preventivo: float = 0.0
    costi: list[VoceCosto] = field(default_factory=list)
    ore: list[OreLavorate] = field(default_factory=list)
    sal_percentuale: float = 0.0            # stato avanzamento lavori, 0-100

    def aggiungi_costo(self, voce: VoceCosto) -> None:
        self.costi.append(voce)

    def registra_ore(self, ore: OreLavorate) -> None:
        self.ore.append(ore)

    def costo_totale(self) -> float:
        return sum(v.importo for v in self.costi)

    def margine(self) -> float:
        fatturato_maturato = self.preventivo * (self.sal_percentuale / 100)
        return fatturato_maturato - self.costo_totale()


# ---------------------------------------------------------------------------
# AMMINISTRAZIONE
# ---------------------------------------------------------------------------

@dataclass
class Fattura:
    id: int
    cantiere_id: int
    numero: str
    data_emissione: date
    importo: float
    pagata: bool = False


@dataclass
class Scadenza:
    descrizione: str                        # es. "DURC", "Cassa Edile", "Revisione mezzo"
    data_scadenza: date
    riferimento_id: Optional[int] = None    # es. id operaio o id mezzo
    completata: bool = False


# ---------------------------------------------------------------------------
# GESTIONALE — facciata che orchestra tutto
# ---------------------------------------------------------------------------

class GestionaleEdile:
    def __init__(self) -> None:
        self.operai: dict[int, Operaio] = {}
        self.fornitori: dict[int, Fornitore] = {}
        self.mezzi: dict[int, Mezzo] = {}
        self.cantieri: dict[int, Cantiere] = {}
        self.fatture: dict[int, Fattura] = {}
        self.scadenze: list[Scadenza] = []

    # --- CRUD di base ---
    def nuovo_cantiere(self, cantiere: Cantiere) -> None:
        self.cantieri[cantiere.id] = cantiere

    def registra_ore_operaio(self, cantiere_id: int, ore: OreLavorate) -> None:
        cantiere = self.cantieri[cantiere_id]
        cantiere.registra_ore(ore)

        # Valorizza in automatico il costo manodopera usando il costo
        # orario dell'operaio, e lo aggiunge come VoceCosto al cantiere.
        operaio = self.operai[ore.operaio_id]
        costo = operaio.costo_orario * ore.ore
        cantiere.aggiungi_costo(VoceCosto(
            tipo=TipoCosto.MANODOPERA,
            descrizione=f"Ore {operaio.nome} {operaio.cognome} ({ore.ore}h)",
            importo=costo,
            data=ore.data,
        ))

    def emetti_fattura(self, fattura: Fattura) -> None:
        self.fatture[fattura.id] = fattura

    # --- Query utili ---
    def margine_per_cantiere(self) -> dict[int, float]:
        return {c.id: c.margine() for c in self.cantieri.values()}

    def scadenze_imminenti(self, entro_giorni: int = 30) -> list[Scadenza]:
        oggi = date.today()
        return [
            s for s in self.scadenze
            if not s.completata and (s.data_scadenza - oggi).days <= entro_giorni
        ]


# ---------------------------------------------------------------------------
# DEMO — versione funzionante di prova con dati di esempio
# ---------------------------------------------------------------------------

def demo() -> None:
    gestionale = GestionaleEdile()

    # --- Anagrafica: 2 operai ---
    mario = Operaio(
        id=1, nome="Mario", cognome="Rossi",
        costo_orario=18.50, data_assunzione=date(2022, 3, 1),
        idoneita_sanitaria_scadenza=date(2026, 11, 15),
        dpi_consegnati=["casco", "scarpe antinfortunistiche", "imbracatura"],
    )
    luigi = Operaio(
        id=2, nome="Luigi", cognome="Bianchi",
        costo_orario=16.00, data_assunzione=date(2023, 6, 12),
        idoneita_sanitaria_scadenza=date(2027, 1, 20),
        dpi_consegnati=["casco", "scarpe antinfortunistiche"],
    )
    gestionale.operai[mario.id] = mario
    gestionale.operai[luigi.id] = luigi

    # --- Cantiere ---
    cantiere = Cantiere(
        id=1, nome="Ristrutturazione Via Roma 12", cliente="Condominio Via Roma 12",
        indirizzo="Via Roma 12, Gualdo Tadino (PG)",
        stato=StatoCantiere.IN_CORSO, preventivo=25000.0, sal_percentuale=40.0,
    )
    gestionale.nuovo_cantiere(cantiere)

    # --- Ore lavorate (calcolano automaticamente il costo manodopera) ---
    gestionale.registra_ore_operaio(1, OreLavorate(operaio_id=1, data=date(2026, 9, 15), ore=8))
    gestionale.registra_ore_operaio(1, OreLavorate(operaio_id=2, data=date(2026, 9, 15), ore=8))
    gestionale.registra_ore_operaio(1, OreLavorate(operaio_id=1, data=date(2026, 9, 16), ore=6))

    # --- Costi materiali/noleggi ---
    cantiere.aggiungi_costo(VoceCosto(
        tipo=TipoCosto.MATERIALE, descrizione="Cemento e laterizi",
        importo=1200.0, data=date(2026, 9, 15),
    ))
    cantiere.aggiungi_costo(VoceCosto(
        tipo=TipoCosto.NOLEGGIO, descrizione="Ponteggio (settimana)",
        importo=350.0, data=date(2026, 9, 15),
    ))

    # --- Scadenze ---
    gestionale.scadenze.append(Scadenza(
        descrizione="DURC", data_scadenza=date(2026, 10, 5), riferimento_id=None,
    ))
    gestionale.scadenze.append(Scadenza(
        descrizione="Revisione furgone", data_scadenza=date(2027, 3, 1),
    ))

    # --- Fattura (SAL 40%) ---
    gestionale.emetti_fattura(Fattura(
        id=1, cantiere_id=1, numero="2026/014",
        data_emissione=date(2026, 9, 18), importo=10000.0,
    ))

    # --- Output ---
    print(f"Costo totale cantiere: {cantiere.costo_totale():.2f} EUR")
    for cid, margine in gestionale.margine_per_cantiere().items():
        print(f"Margine cantiere {cid}: {margine:.2f} EUR")

    print("\nScadenze nei prossimi 30 giorni:")
    for s in gestionale.scadenze_imminenti(30):
        print(f"  - {s.descrizione} entro il {s.data_scadenza}")

    print("\nFatture emesse:")
    for f in gestionale.fatture.values():
        stato = "pagata" if f.pagata else "da incassare"
        print(f"  - {f.numero}: {f.importo:.2f} EUR ({stato})")


if __name__ == "__main__":
    demo()

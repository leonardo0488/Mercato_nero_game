import streamlit as st
import threading
import random
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

# ==============================================================================
# CONFIGURAZIONE PAGINA E STILE GRAFICO AD ALTO CONTRASTO
# ==============================================================================
st.set_page_config(
    page_title="Mercato Nero al Rifugio",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

CUSTOM_CSS = """
<style>
    /* Forza sfondo scuro e testo chiaro su TUTTA l'interfaccia Streamlit */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #0f172a !important;
        color: #f8fafc !important;
    }
    
    h1, h2, h3, h4, h5, h6, p, span, label, div, li {
        color: #f8fafc;
    }
    
    input, textarea, select, [data-baseweb="select"] > div, [data-baseweb="input"] > div {
        background-color: #1e293b !important;
        color: #ffffff !important;
        border-color: #475569 !important;
    }
    
    ul[role="listbox"], ul[role="listbox"] li {
        background-color: #1e293b !important;
        color: #ffffff !important;
    }

    [data-testid="stMetricValue"] {
        color: #34d399 !important;
        font-weight: 800 !important;
    }
    [data-testid="stMetricLabel"] {
        color: #cbd5e1 !important;
    }

    button[data-baseweb="tab"] {
        background-color: #1e293b !important;
        color: #cbd5e1 !important;
        border-radius: 8px 8px 0 0;
        margin-right: 4px;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        background-color: #334155 !important;
        color: #fbbf24 !important;
        border-bottom: 3px solid #fbbf24 !important;
    }

    .lot-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-left: 6px solid #fbbf24;
        border-radius: 10px;
        padding: 18px;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    }
    .lot-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #fde047 !important;
        margin-bottom: 6px;
    }
    .lot-cat {
        display: inline-block;
        background-color: #0284c7;
        color: #ffffff !important;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 3px 9px;
        border-radius: 4px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
    }
    .lot-desc {
        color: #e2e8f0 !important;
        font-size: 0.95rem;
    }
    .lot-price {
        font-size: 1.15rem;
        font-weight: 800;
        color: #4ade80 !important;
        margin-top: 10px;
    }

    /* Box Soffiata Segreta */
    .tip-box {
        background-color: #450a0a;
        border: 2px solid #f87171;
        border-radius: 10px;
        padding: 16px;
        margin: 12px 0;
        color: #fef2f2 !important;
    }

    /* Box Perizia Privata Post-Acquisto */
    .appraisal-box {
        background-color: #172554;
        border: 2px solid #38bdf8;
        border-radius: 10px;
        padding: 14px;
        margin: 10px 0;
        color: #e0f2fe !important;
    }

    .status-banner {
        background-color: #1d4ed8;
        color: #ffffff !important;
        border-radius: 8px;
        padding: 12px 16px;
        text-align: center;
        font-weight: 800;
        letter-spacing: 0.05em;
        border: 1px solid #60a5fa;
        margin-bottom: 20px;
    }

    .stButton > button, [data-testid="stFormSubmitButton"] > button {
        width: 100%;
        border-radius: 8px;
        font-weight: 700 !important;
        border: 1px solid #64748b !important;
        background-color: #2563eb !important;
        color: #ffffff !important;
        padding: 0.55rem 1rem !important;
    }
    .stButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover {
        background-color: #1d4ed8 !important;
        border-color: #93c5fd !important;
    }

    [data-testid="stAlert"] {
        background-color: #1e293b !important;
        border: 1px solid #475569 !important;
        color: #f8fafc !important;
    }
    [data-testid="stAlert"] p {
        color: #f8fafc !important;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ==============================================================================
# DATASET DI GIOCO: 7 ROUND (21 LOTTI) & 7 OBIETTIVI SEGRETI
# ==============================================================================
INITIAL_BUDGET = 12000
TOTAL_ROUNDS = 7
ADMIN_PASSWORD = "admin123"

CATALOGO_LOTTI = [
    # --- ROUND 1 ---
    {
        "id": "L01", "round": 1, "category": "Arte",
        "name": "Tela 'Bambina col Palloncino Sgonfio' di Banksy",
        "desc": "Trovata dietro un cassonetto a Bristol. Autenticata su un tovagliolo da pub.",
        "base_price": 1200, "true_base_value": 0, "is_fake": True, "tag": "arte_urbana",
        "tip": "SOFFIATA DAL RESTAURATORE: La vernice è acrilico Ikea del 2022. È un FALSO totale (valore base 0 €)!",
        "flash_news": "🔍 PERIZIA RISERVATA: Un critico svizzero ha analizzato la tua tela: è un FALSO (0 €)! Mantieni la faccia da poker o rivendila a qualche pollo!"
    },
    {
        "id": "L02", "round": 1, "category": "Tech & Biotech",
        "name": "Brevetto 'Caffè Decaffeinato che Sveglia'",
        "desc": "Molecola sperimentale svizzera. Promette zero tachicardia e 12 ore di focus.",
        "base_price": 1500, "true_base_value": 2500, "is_fake": False, "tag": "biotech_caffe",
        "tip": "SOFFIATA DAL LABORATORIO: I test clinici sono un trionfo! A fine asta il valore di questo brevetto RADDOPPIERÀ.",
        "flash_news": "🔍 PERIZIA RISERVATA: Una multinazionale ha appena validato il brevetto! A fine partita varrà il DOPPIO (5.000 €)!"
    },
    {
        "id": "L03", "round": 1, "category": "Lusso & Orologi",
        "name": "Cronografo 'Rolex Sub-Zero' anni '70",
        "desc": "Appartenuto a un famoso istruttore di sci di Cortina. Cinturino leggermente vissuto.",
        "base_price": 1800, "true_base_value": 3000, "is_fake": False, "tag": "orologi_epoca",
        "tip": "SOFFIATA DALL'OROLOGIAIO: Il movimento interno è originale e rarissimo. Vale una fortuna.",
        "flash_news": "🔍 PERIZIA RISERVATA: L'asta di Ginevra conferma il boom degli orologi sportivi vintage: il tuo vale 3.600 €!"
    },

    # --- ROUND 2 ---
    {
        "id": "L04", "round": 2, "category": "Materie Prime",
        "name": "Lingotto d'Oro Elvetico (500g)",
        "desc": "Punzonato Zurigo 999.9. Pesante, freddo al tatto e molto rassicurante.",
        "base_price": 2200, "true_base_value": 3500, "is_fake": False, "tag": "oro_fisico",
        "tip": "SOFFIATA FINANZIARIA: I mercati stanno per crollare: i beni rifugio come l'oro saliranno di un altro +30%!",
        "flash_news": "🔍 PERIZIA RISERVATA: Oro purissimo 24 carati! Con la corsa ai beni rifugio vale ben 4.550 €!"
    },
    {
        "id": "L05", "round": 2, "category": "Finanza & Crypto",
        "name": "Chiavetta USB con 50 'AlpineCoin'",
        "desc": "Criptovaluta minata usando il calore di una stufa a pellet. Password scritta su post-it.",
        "base_price": 1000, "true_base_value": 4000, "is_fake": False, "tag": "crypto_meme",
        "tip": "SOFFIATA DA REDDIT: Elon sta per twittare una foto delle Dolomiti! Questa chiavetta varrà moltissimo.",
        "flash_news": "🔍 PERIZIA RISERVATA: Il wallet è sbloccato e pieno! La tua chiavetta vale 4.000 € reali!"
    },
    {
        "id": "L06", "round": 2, "category": "Arte",
        "name": "Scultura Minimalista 'Aria di Montagna'",
        "desc": "Teca in plexiglass sigillata nel 1998 a Chamonix. Opera concettuale.",
        "base_price": 800, "true_base_value": 2400, "is_fake": False, "tag": "arte_concettuale",
        "tip": "SOFFIATA DA SOTHEBY'S: È un'opera autentica e quotatissima dell'arte povera. Ottimo affare!",
        "flash_news": "🔍 PERIZIA RISERVATA: Certificato autentico! Il MoMA ha acquisito una teca gemella: la tua vale 2.400 €."
    },

    # --- ROUND 3 ---
    {
        "id": "L07", "round": 3, "category": "Tech & Biotech",
        "name": "Algoritmo AI 'Prevedi-Valanghe'",
        "desc": "Software predittivo basato su reti neurali e vecchi proverbi dei montanari.",
        "base_price": 1600, "true_base_value": 0, "is_fake": True, "tag": "ai_truffa",
        "tip": "SOFFIATA DALLO SVILUPPATORE: Il codice è solo un 'random.choice([True, False])'. È una TRUFFA (0 €)!",
        "flash_news": "🔍 PERIZIA RISERVATA: Hai aperto il codice sorgente: è un foglio Excel truccato! Valore reale: 0 € (FALSO)."
    },
    {
        "id": "L08", "round": 3, "category": "Lusso & Orologi",
        "name": "Bottiglia Romanée-Conti 1985 (Ritrovata in Cantina)",
        "desc": "Etichetta macchiata d'umidità, livello del vino perfetto. Da collezione.",
        "base_price": 2000, "true_base_value": 3800, "is_fake": False, "tag": "vino_raro",
        "tip": "SOFFIATA DEL SOMMELIER: Conservata a 11°C costanti per 40 anni. È autentica e rarissima!",
        "flash_news": "🔍 PERIZIA RISERVATA: Tappo e annata 100% originali! Valore di mercato confermato a 3.800 €."
    },
    {
        "id": "L09", "round": 3, "category": "Finanza & Crypto",
        "name": "Azioni 'Funivie del Cervino S.p.A.'",
        "desc": "Pacchetto azionario di minoranza. Bilanci in rosso ma vista panoramica mozzafiato.",
        "base_price": 1400, "true_base_value": 2800, "is_fake": False, "tag": "azioni_turismo",
        "tip": "SOFFIATA ISTITUZIONALE: Approvati fondi europei per i nuovi impianti! Il titolo raddoppia.",
        "flash_news": "🔍 PERIZIA RISERVATA: Sbloccati i fondi europei per gli impianti! Le tue azioni valgono 2.800 €."
    },

    # --- ROUND 4 ---
    {
        "id": "L10", "round": 4, "category": "Materie Prime",
        "name": "Concessione Miniere di Litio 'Val di Fassa'",
        "desc": "Diritti di estrazione in un terreno roccioso dietro un rifugio dismesso.",
        "base_price": 2000, "true_base_value": 4500, "is_fake": False, "tag": "litio_verde",
        "tip": "SOFFIATA GEOLOGICA: Hanno trovato il giacimento di litio più puro d'Europa! Vale una fortuna.",
        "flash_news": "🔍 PERIZIA RISERVATA: Confermato mega-giacimento di litio! La tua concessione vale 4.500 €."
    },
    {
        "id": "L11", "round": 4, "category": "Arte",
        "name": "Schizzo a Carboncino di Picasso (Sul Menù)",
        "desc": "Disegnato nel 1954 dopo tre grappe. Firma leggibile con molta immaginazione.",
        "base_price": 1700, "true_base_value": 3600, "is_fake": False, "tag": "picasso_menu",
        "tip": "SOFFIATA DALL'ARCHIVIO PICASSO: Il maestro era davvero in quel ristorante nel '54! È AUTENTICO.",
        "flash_news": "🔍 PERIZIA RISERVATA: La Fondazione Picasso ha autenticato lo schizzo! Vale 3.600 € reali."
    },
    {
        "id": "L12", "round": 4, "category": "Lusso & Orologi",
        "name": "Diamante Blu 'Cuore delle Dolomiti'",
        "desc": "Taglio brillante, 3 carati. Certificato gemmologico stampato su carta lucida.",
        "base_price": 2100, "true_base_value": 0, "is_fake": True, "tag": "diamante_vetro",
        "tip": "SOFFIATA DEL GIOIELLIERE: È zircone sintetico lucidato! Valore reale 0 € (a meno che tu non sia il Falsario).",
        "flash_news": "🔍 PERIZIA RISERVATA: Il gemmologo conferma che è vetro al piombo di Murano! Valore: 0 € (FALSO)."
    },

    # --- ROUND 5 ---
    {
        "id": "L13", "round": 5, "category": "Finanza & Crypto",
        "name": "Fondo Speculativo 'Offshore Cayman-Lugano'",
        "desc": "Quote al portatore di un fondo anonimo. Nessuna domanda, alti rendimenti.",
        "base_price": 2300, "true_base_value": 4800, "is_fake": False, "tag": "fondo_offshore",
        "tip": "SOFFIATA BANCARIA: Il fondo ha appena chiuso un arbitraggio milionario! Le quote valgono tantissimo.",
        "flash_news": "🔍 PERIZIA RISERVATA: Dividendo straordinario accreditato! Le tue quote valgono 4.800 €."
    },
    {
        "id": "L14", "round": 5, "category": "Materie Prime",
        "name": "Barile di Petrolio Greggio 'Brent Alpino'",
        "desc": "Estratto per errore scavando una piscina riscaldata a St. Moritz.",
        "base_price": 1500, "true_base_value": 0, "is_fake": True, "tag": "petrolio_finto",
        "tip": "SOFFIATA CHIMICA: Non è petrolio, è olio esausto di friggitrice industriale! Vale 0 €.",
        "flash_news": "🔍 PERIZIA RISERVATA: Analisi chimiche confermano che è olio di frittura usato! Valore: 0 € (FALSO)."
    },
    {
        "id": "L15", "round": 5, "category": "Tech & Biotech",
        "name": "Prototipo Batteria a Stato Solido 'Tesla-Alps'",
        "desc": "Cella energetica grande come un libro che ricarica un'auto in 90 secondi.",
        "base_price": 2200, "true_base_value": 4600, "is_fake": False, "tag": "batteria_solida",
        "tip": "SOFFIATA INDUSTRIALE: Funziona davvero! È il santo graal dell'automotive e vale tantissimo.",
        "flash_news": "🔍 PERIZIA RISERVATA: Accordo industriale firmato! La tua batteria prototipo vale 4.600 €."
    },

    # --- ROUND 6 ---
    {
        "id": "L16", "round": 6, "category": "Lusso & Orologi",
        "name": "Patek Philippe 'Nautilus Ghiacciaio' (Senza Scatola)",
        "desc": "Trovato nella tasca di un vecchio giaccone da sci vintage a Zermatt.",
        "base_price": 2400, "true_base_value": 5200, "is_fake": False, "tag": "patek_raro",
        "tip": "SOFFIATA DA CHRISTIE'S: Il numero di serie appartiene a un re esiliato! È autentico e rarissimo.",
        "flash_news": "🔍 PERIZIA RISERVATA: Estratto d'archivio confermato da Ginevra! L'orologio vale 5.200 €."
    },
    {
        "id": "L17", "round": 6, "category": "Finanza & Crypto",
        "name": "Obbligazioni 'Banca Centrale del Principato di Seborga'",
        "desc": "Titoli di Stato sovrani con interessi del 45% annuo garantiti dalla stretta di mano.",
        "base_price": 1400, "true_base_value": 0, "is_fake": True, "tag": "bond_fuffa",
        "tip": "SOFFIATA FINANZIARIA: Il Principato non ha una banca centrale! Carta straccia da 0 €.",
        "flash_news": "🔍 PERIZIA RISERVATA: Default tecnico dei bond di Seborga! Carta straccia da 0 € (FALSO)."
    },
    {
        "id": "L18", "round": 6, "category": "Arte",
        "name": "NFT 'Marmotta Annoiata #001' su chiavetta d'argento",
        "desc": "Il primo crypto-ritratto alpino della storia. Include anche il disegno stampato.",
        "base_price": 1300, "true_base_value": 3200, "is_fake": False, "tag": "nft_marmotta",
        "tip": "SOFFIATA DAL METAVERSO: Un museo digitale di Tokyo sta comprando tutta la collezione! Ottimo valore.",
        "flash_news": "🔍 PERIZIA RISERVATA: Acquisizione record a Tokyo! Il tuo pezzo unico vale 3.200 €."
    },

    # --- ROUND 7 (GRAN FINALE) ---
    {
        "id": "L19", "round": 7, "category": "Materie Prime",
        "name": "Riserva Privata di Tartufo Bianco d'Alba (2 Kg)",
        "desc": "Sigillata sottovuoto in teca refrigerata. Profumo percepibile anche attraverso il vetro.",
        "base_price": 2000, "true_base_value": 4500, "is_fake": False, "tag": "tartufo_alba",
        "tip": "SOFFIATA GASTRONOMICA: È stata una stagione scarsissima: gli chef stellati lo pagheranno oro!",
        "flash_news": "🔍 PERIZIA RISERVATA: Qualità eccelsa certificata! Valore finale: 4.500 €."
    },
    {
        "id": "L20", "round": 7, "category": "Tech & Biotech",
        "name": "Brevetto 'Teletrasporto Quantistico per Bagagli'",
        "desc": "Promette di spedire le valigie direttamente in hotel senza passare dal nastro.",
        "base_price": 1800, "true_base_value": 0, "is_fake": True, "tag": "teletrasporto_fake",
        "tip": "SOFFIATA SCIENTIFICA: Viola le leggi della termodinamica ed è stato bocciato dal CERN. Vale 0 €!",
        "flash_news": "🔍 PERIZIA RISERVATA: Bocciato dal CERN! Il brevetto è una truffa da 0 € (FALSO)."
    },
    {
        "id": "L21", "round": 7, "category": "Finanza & Crypto",
        "name": "Quota Segreta 'Casinò Privato di St. Moritz'",
        "desc": "Partecipazione agli utili del tavolo high-roller più esclusivo delle Alpi.",
        "base_price": 2600, "true_base_value": 5800, "is_fake": False, "tag": "casino_quota",
        "tip": "SOFFIATA DAL CROUPIER: Questa settimana gli sceicchi hanno perso milioni al tavolo! Vale una fortuna.",
        "flash_news": "🔍 PERIZIA RISERVATA: Dividendo record incassato! La tua quota vale 5.800 €."
    },
]

FLASH_MULTIPLIERS = {
    "biotech_caffe": 2.0,
    "orologi_epoca": 1.2,
    "oro_fisico": 1.3,
}

OBIETTIVI_SEGRETI = [
    {
        "id": "OBJ_ARTE",
        "name": "🎨 Collezionista d'Arte",
        "desc": "Ogni opera della categoria 'Arte' AUTENTICA in tuo possesso vale +2.500 € bonus a fine partita."
    },
    {
        "id": "OBJ_SQUALO",
        "name": "🦈 Squalo della Finanza",
        "desc": "Ottieni +4.500 € bonus a fine partita se chiudi con almeno 5.000 € di saldo liquido."
    },
    {
        "id": "OBJ_MONOPOLIO",
        "name": "👑 Monopolista",
        "desc": "Se possiedi almeno 3 asset della STESSA categoria, il valore finale di quegli asset RADDOPPIA."
    },
    {
        "id": "OBJ_FALSARIO",
        "name": "🎭 Il Falsario",
        "desc": "Ribalti il mercato nero: i lotti FALSI che acquisti non valgono 0 €, ma +3.500 € ciascuno!"
    },
    {
        "id": "OBJ_SPECULATORE",
        "name": "🌐 Speculatore Diversificato",
        "desc": "Ottieni +1.500 € bonus per ogni categoria DIVERSA di asset presente nel tuo inventario finale."
    },
    {
        "id": "OBJ_BARONE_RISORSE",
        "name": "⛏️ Barone delle Risorse",
        "desc": "Ogni lotto autentico delle categorie 'Materie Prime' o 'Tech & Biotech' vale +2.000 € bonus a fine partita."
    },
    {
        "id": "OBJ_AVVOLTOIO",
        "name": "🦅 Avvoltoio delle Aste",
        "desc": "Ottieni +1.200 € bonus per OGNI lotto (vero o falso) che ti aggiudichi durante la partita!"
    }
]

# ==============================================================================
# STATO GLOBALE CONDIVISO (THREAD-SAFE TRAMITE @st.cache_resource)
# ==============================================================================
@dataclass
class GameState:
    lock: threading.RLock = field(default_factory=threading.RLock)
    phase: str = "LOBBY"  # LOBBY | CONTRATTAZIONE_E_ASTA | ESITO_ROUND | CLASSIFICA_FINALE
    current_round: int = 1
    players: Dict[str, dict] = field(default_factory=dict)
    current_bids: Dict[str, Dict[str, dict]] = field(default_factory=dict)
    last_round_results: List[dict] = field(default_factory=list)
    transfer_log: List[str] = field(default_factory=list)

@st.cache_resource
def get_game_state() -> GameState:
    return GameState()

state = get_game_state()

# ==============================================================================
# FUNZIONI LOGICA DI GIOCO (PROTETTI DA LOCK)
# ==============================================================================
def get_round_lots(round_num: int) -> List[dict]:
    return [lot for lot in CATALOGO_LOTTI if lot["round"] == round_num]

def compute_lot_real_value(lot: dict) -> int:
    if lot["is_fake"]:
        return 0
    mult = FLASH_MULTIPLIERS.get(lot["tag"], 1.0)
    return int(round(lot["true_base_value"] * mult))

def register_or_login_player(name: str, pin: str) -> tuple[bool, str]:
    clean_name = name.strip()
    clean_pin = pin.strip()
    if not clean_name or len(clean_pin) != 4 or not clean_pin.isdigit():
        return False, "Inserisci un nome valido e un PIN numerico di esattamente 4 cifre."

    with state.lock:
        if clean_name in state.players:
            if state.players[clean_name]["pin"] == clean_pin:
                return True, f"Bentornato al tavolo, {clean_name}!"
            else:
                return False, "Nome già registrato con un altro PIN! Controlla il PIN o usa un altro nome."

        if state.phase != "LOBBY":
            return False, "La partita è già iniziata! Chiedi alla Regia di resettare se devi entrare."
        if len(state.players) >= 12:
            return False, "Tavolo pieno (massimo 12 giocatori)."

        state.players[clean_name] = {
            "pin": clean_pin,
            "balance": INITIAL_BUDGET,
            "objective": None,
            "inventory": [],
            "tips": {},
            "last_won_news": []  # Perizie private dell'ultimo round vinto
        }
        return True, f"Registrazione completata! Ricorda il tuo PIN ({clean_pin})."

def assign_tips_for_round(round_num: int):
    player_names = list(state.players.keys())
    if not player_names:
        return
    lots = get_round_lots(round_num)
    num_tips = min(len(player_names), 3 if len(player_names) >= 6 else 2)
    chosen_players = random.sample(player_names, num_tips)
    chosen_lots = random.sample(lots, min(len(lots), num_tips))

    for p_name, lot in zip(chosen_players, chosen_lots):
        state.players[p_name]["tips"][round_num] = (
            f"**Oggetto:** {lot['name']}\n\n{lot['tip']}"
        )

def start_game():
    with state.lock:
        if len(state.players) < 2:
            return False, "Servono almeno 2 giocatori (consigliati 5-12) per avviare!"
        player_names = list(state.players.keys())
        shuffled_objs = []
        while len(shuffled_objs) < len(player_names):
            pool = OBIETTIVI_SEGRETI.copy()
            random.shuffle(pool)
            shuffled_objs.extend(pool)

        for idx, p_name in enumerate(player_names):
            state.players[p_name]["balance"] = INITIAL_BUDGET
            state.players[p_name]["objective"] = shuffled_objs[idx]
            state.players[p_name]["inventory"] = []
            state.players[p_name]["tips"] = {}
            state.players[p_name]["last_won_news"] = []

        state.current_round = 1
        state.current_bids = {}
        state.last_round_results = []
        state.transfer_log = []
        state.phase = "CONTRATTAZIONE_E_ASTA"
        assign_tips_for_round(1)
        return True, "Partita avviata! 7 Obiettivi e prime soffiate distribuiti."

def execute_trade_or_transfer(
    initiator: str,
    counterparty: str,
    lot_id: Optional[str],
    price: int
) -> tuple[bool, str]:
    """
    Gestisce sia un semplice bonifico (lot_id is None) sia la vendita di un lotto
    dall'inventario di `initiator` a `counterparty` al prezzo `price`.
    """
    if initiator == counterparty:
        return False, "Non puoi fare scambi con te stesso."
    if price < 0:
        return False, "L'importo non può essere negativo."
    if lot_id is None and price <= 0:
        return False, "Per un bonifico senza oggetti l'importo deve essere maggiore di 0 €."

    with state.lock:
        if state.phase not in ("CONTRATTAZIONE_E_ASTA", "ESITO_ROUND"):
            return False, "Gli scambi sono chiusi!"
        if initiator not in state.players or counterparty not in state.players:
            return False, "Giocatore non trovato."

        # Caso A: Bonifico semplice (initiator invia `price` € a counterparty)
        if lot_id is None:
            sender, receiver = initiator, counterparty
            if state.players[sender]["balance"] < price:
                return False, "Fondi insufficienti per questo bonifico."
            committed_bids = sum(
                b.get(sender, {}).get("amount", 0)
                for b in state.current_bids.values()
            )
            if state.players[sender]["balance"] - price < committed_bids:
                return False, f"Hai già {committed_bids:,} € impegnati nell'asta di questo round!"

            state.players[sender]["balance"] -= price
            state.players[receiver]["balance"] += price
            ts = time.strftime("%H:%M:%S")
            state.transfer_log.insert(
                0, f"💸 [{ts}] **{sender}** ha inviato un bonifico segreto a **{receiver}**"
            )
            return True, f"Bonifico di {price:,} € inviato a {receiver}!"

        # Caso B: Vendita / Cessione di un Lotto (initiator cede il lotto a counterparty per `price` €)
        seller, buyer = initiator, counterparty
        seller_inv = state.players[seller]["inventory"]
        lot_obj = next((item for item in seller_inv if item["id"] == lot_id), None)
        if not lot_obj:
            return False, "Non possiedi più questo oggetto!"

        if state.players[buyer]["balance"] < price:
            return False, f"{buyer} non ha abbastanza soldi liquidi ({state.players[buyer]['balance']:,} €)!"

        buyer_committed = sum(
            b.get(buyer, {}).get("amount", 0)
            for b in state.current_bids.values()
        )
        if state.players[buyer]["balance"] - price < buyer_committed:
            return False, f"{buyer} ha troppi soldi già impegnati nelle offerte d'asta di questo round!"

        # Esegui lo scambio atomico
        seller_inv.remove(lot_obj)
        state.players[buyer]["inventory"].append(lot_obj)
        state.players[buyer]["balance"] -= price
        state.players[seller]["balance"] += price

        ts = time.strftime("%H:%M:%S")
        state.transfer_log.insert(
            0, f"🤝 [{ts}] **{seller}** ha ceduto un asset a **{buyer}** (accordo riservato)"
        )
        return True, f"Hai ceduto '{lot_obj['name']}' a {buyer} per {price:,} €!"

def submit_player_bids(player_name: str, bids_dict: Dict[str, int]) -> tuple[bool, str]:
    with state.lock:
        if state.phase != "CONTRATTAZIONE_E_ASTA":
            return False, "L'asta è chiusa!"
        player = state.players.get(player_name)
        if not player:
            return False, "Giocatore non trovato."

        total_bid = sum(bids_dict.values())
        if total_bid > player["balance"]:
            return False, f"La somma delle offerte ({total_bid:,} €) supera il tuo saldo ({player['balance']:,} €)!"

        lots = get_round_lots(state.current_round)
        for lot in lots:
            amt = bids_dict.get(lot["id"], 0)
            if amt > 0 and amt < lot["base_price"]:
                return False, f"Per '{lot['name']}' l'offerta deve essere 0 € oppure almeno {lot['base_price']:,} €."

        now = time.time()
        for lot in lots:
            lid = lot["id"]
            amt = bids_dict.get(lid, 0)
            if lid not in state.current_bids:
                state.current_bids[lid] = {}
            if amt > 0:
                prev = state.current_bids[lid].get(player_name)
                ts = prev["timestamp"] if (prev and prev["amount"] == amt) else now
                state.current_bids[lid][player_name] = {"amount": amt, "timestamp": ts}
            else:
                state.current_bids[lid].pop(player_name, None)

        return True, f"Offerte registrate! Totale impegnato: {total_bid:,} €."

def resolve_current_round():
    with state.lock:
        lots = get_round_lots(state.current_round)
        results = []

        # Pulisci eventuali notifiche perizie del round precedente
        for p_data in state.players.values():
            p_data["last_won_news"] = []

        for lot in lots:
            lid = lot["id"]
            lot_bids = state.current_bids.get(lid, {})
            valid_bids = [
                (p_name, info["amount"], info["timestamp"])
                for p_name, info in lot_bids.items()
                if info["amount"] >= lot["base_price"]
            ]

            if valid_bids:
                valid_bids.sort(key=lambda x: (-x[1], x[2]))
                winner_name, winning_price, _ = valid_bids[0]

                if state.players[winner_name]["balance"] >= winning_price:
                    state.players[winner_name]["balance"] -= winning_price
                    state.players[winner_name]["inventory"].append(lot)
                    # Invia la Notizia Flash / Perizia PRIVATA solo al vincitore!
                    state.players[winner_name]["last_won_news"].append({
                        "lot_name": lot["name"],
                        "news": lot["flash_news"]
                    })
                    results.append({
                        "lot_name": lot["name"],
                        "category": lot["category"],
                        "winner": winner_name,
                        "price": winning_price,
                        "sold": True
                    })
                else:
                    results.append({
                        "lot_name": lot["name"],
                        "category": lot["category"],
                        "winner": None,
                        "price": 0,
                        "sold": False
                    })
            else:
                results.append({
                    "lot_name": lot["name"],
                    "category": lot["category"],
                    "winner": None,
                    "price": 0,
                    "sold": False
                })

        state.last_round_results = results
        state.current_bids = {}
        state.phase = "ESITO_ROUND"

def advance_to_next_round():
    with state.lock:
        if state.current_round < TOTAL_ROUNDS:
            state.current_round += 1
            state.last_round_results = []
            for p_data in state.players.values():
                p_data["last_won_news"] = []
            state.phase = "CONTRATTAZIONE_E_ASTA"
            assign_tips_for_round(state.current_round)
        else:
            state.phase = "CLASSIFICA_FINALE"

def reset_entire_game():
    with state.lock:
        state.phase = "LOBBY"
        state.current_round = 1
        state.players = {}
        state.current_bids = {}
        state.last_round_results = []
        state.transfer_log = []

def calculate_final_standings() -> List[dict]:
    standings = []
    with state.lock:
        for p_name, p_data in state.players.items():
            cash = p_data["balance"]
            inv = p_data["inventory"]
            obj = p_data["objective"]
            obj_id = obj["id"] if obj else ""

            cat_counts: Dict[str, int] = {}
            for item in inv:
                cat_counts[item["category"]] = cat_counts.get(item["category"], 0) + 1

            assets_value = 0
            asset_details = []

            for item in inv:
                val = compute_lot_real_value(item)
                if obj_id == "OBJ_MONOPOLIO" and cat_counts[item["category"]] >= 3:
                    val *= 2
                assets_value += val
                tag_status = "FALSO (0 €)" if item["is_fake"] else f"Reale: {val:,} €"
                asset_details.append(f"{item['name']} [{tag_status}]")

            bonus = 0
            if obj_id == "OBJ_ARTE":
                auth_art = sum(1 for i in inv if i["category"] == "Arte" and not i["is_fake"])
                bonus = auth_art * 2500
            elif obj_id == "OBJ_SQUALO":
                if cash >= 5000:
                    bonus = 4500
            elif obj_id == "OBJ_MONOPOLIO":
                base_sum = sum(compute_lot_real_value(i) for i in inv)
                bonus = assets_value - base_sum
                assets_value = base_sum
            elif obj_id == "OBJ_FALSARIO":
                fakes = sum(1 for i in inv if i["is_fake"])
                bonus = fakes * 3500
            elif obj_id == "OBJ_SPECULATORE":
                unique_cats = len(cat_counts)
                bonus = unique_cats * 1500
            elif obj_id == "OBJ_BARONE_RISORSE":
                res_items = sum(
                    1 for i in inv
                    if i["category"] in ("Materie Prime", "Tech & Biotech") and not i["is_fake"]
                )
                bonus = res_items * 2000
            elif obj_id == "OBJ_AVVOLTOIO":
                bonus = len(inv) * 1200

            total = cash + assets_value + bonus
            standings.append({
                "Giocatore": p_name,
                "Obiettivo Segreto": obj["name"] if obj else "-",
                "Saldo Liquido": cash,
                "Valore Asset": assets_value,
                "Bonus Obiettivo": bonus,
                "PATRIMONIO TOTALE": total,
                "Dettaglio Asset": " • ".join(asset_details) if asset_details else "Nessun asset acquistato"
            })

    standings.sort(key=lambda x: -x["PATRIMONIO TOTALE"])
    return standings

# ==============================================================================
# NAVIGAZIONE TRA LE 3 MODALITÀ (URL PARAM O SELETTORE INIZIALE)
# ==============================================================================
query_params = st.query_params
default_mode = query_params.get("mode", "home")

if "view_mode" not in st.session_state:
    st.session_state.view_mode = default_mode

def set_mode(new_mode: str):
    st.session_state.view_mode = new_mode
    st.query_params["mode"] = new_mode

# ==============================================================================
# VISTA 0: SCHERMATA DI BENVENUTO / SCELTA RUOLO
# ==============================================================================
if st.session_state.view_mode == "home":
    st.title("🏔️ Mercato Nero al Rifugio")
    st.markdown("##### *7 Round di aste al buio, soffiate segrete, mercato secondario e tradimenti.*")
    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 📱 Giocatore")
        st.write("Entra dal tuo smartphone per ricevere soffiate, scambiare lotti e puntare all'asta.")
        if st.button("Entra come Giocatore", type="primary"):
            set_mode("player")
            st.rerun()

    with col2:
        st.markdown("### 📺 Tabellone TV")
        st.write("Proietta questa schermata sul laptop o sulla TV in salotto per tutti i commensali.")
        if st.button("Apri Tabellone Pubblico"):
            set_mode("board")
            st.rerun()

    with col3:
        st.markdown("### 🎛️ Regia Master")
        st.write("Controlla il ritmo della serata senza spoilerarti gli obiettivi altrui (richiede password).")
        if st.button("Apri Pannello Regia"):
            set_mode("admin")
            st.rerun()

# ==============================================================================
# VISTA 1: VISTA GIOCATORE (SMARTPHONE)
# ==============================================================================
elif st.session_state.view_mode == "player":
    top_col1, top_col2 = st.columns([3, 1])
    with top_col1:
        st.markdown("### 📱 Mercato Nero — Telefono")
    with top_col2:
        if st.button("🏠 Home"):
            set_mode("home")
            st.rerun()

    if "player_name" not in st.session_state or st.session_state.player_name not in state.players:
        st.info("Inserisci il tuo **Nome** e un **PIN a 4 cifre**. Se chiudi per sbaglio il browser, reinserisci gli stessi dati per rientrare!")
        with st.form("login_form"):
            p_name_input = st.text_input("Il tuo Nome (es. Marco)", max_chars=20)
            p_pin_input = st.text_input("PIN segreto a 4 cifre (es. 1990)", max_chars=4, type="password")
            submitted = st.form_submit_button("Entra al Tavolo", type="primary")
            if submitted:
                ok, msg = register_or_login_player(p_name_input, p_pin_input)
                if ok:
                    st.session_state.player_name = p_name_input.strip()
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)
    else:
        me = st.session_state.player_name

        @st.fragment(run_every=3)
        def render_player_dashboard():
            with state.lock:
                if me not in state.players:
                    st.warning("La partita è stata resettata dalla Regia.")
                    if st.button("Torna al Login"):
                        del st.session_state.player_name
                        st.rerun()
                    return

                p_data = state.players[me]
                current_phase = state.phase
                cur_round = state.current_round
                balance = p_data["balance"]
                objective = p_data["objective"]
                my_tip = p_data["tips"].get(cur_round)
                my_inv = list(p_data["inventory"])
                my_won_news = list(p_data.get("last_won_news", []))
                other_players = [n for n in state.players.keys() if n != me]

            st.markdown(f"👤 **{me}** | 💰 Saldo Liquido: **<span style='color:#4ade80; font-size:1.15rem;'>{balance:,} €</span>**", unsafe_allow_html=True)

            if objective:
                show_obj = st.toggle("👁️ Mostra Obiettivo Segreto (occhio agli sguardi indiscreti!)", value=False)
                if show_obj:
                    st.warning(f"**{objective['name']}**\n\n{objective['desc']}")

            st.divider()

            # --- LOBBY ---
            if current_phase == "LOBBY":
                st.markdown('<div class="status-banner">⏳ IN ATTESA CHE LA REGIA AVVII LA PARTITA...</div>', unsafe_allow_html=True)
                st.write(f"Giocatori connessi finora: **{len(state.players)}**")
                st.write(f"Budget iniziale: **{INITIAL_BUDGET:,} €** • Durata: **{TOTAL_ROUNDS} Round**")

            # --- CONTRATTAZIONE E ASTA ---
            elif current_phase == "CONTRATTAZIONE_E_ASTA":
                st.markdown(f'<div class="status-banner">🔥 ROUND {cur_round}/{TOTAL_ROUNDS} — CONTRATTAZIONE & ASTA</div>', unsafe_allow_html=True)

                if my_tip:
                    show_tip = st.toggle("🕵️ Hai ricevuto una SOFFIATA SEGRETA! Tocca per leggere", value=True)
                    if show_tip:
                        st.markdown(f'<div class="tip-box"><b>🤫 INFORMAZIONE RISERVATA (Round {cur_round})</b><br><br>{my_tip}</div>', unsafe_allow_html=True)
                else:
                    st.info("🔇 Nessuna soffiata ricevuta in questo round. Ascolta gli altri e cerca di capire chi mente!")

                tab_asta, tab_scambi, tab_inv = st.tabs(["🔨 Asta al Buio", "🤝 Scambi & Bonifici", f"🎒 Inventario ({len(my_inv)})"])

                with tab_asta:
                    st.write("Inserisci la tua offerta segreta per ciascun lotto (`0 €` per passare). Puoi modificarla finché la Regia non chiude l'asta.")
                    lots = get_round_lots(cur_round)

                    with state.lock:
                        existing_bids = {
                            lot["id"]: state.current_bids.get(lot["id"], {}).get(me, {}).get("amount", 0)
                            for lot in lots
                        }

                    with st.form(key=f"bid_form_r{cur_round}"):
                        new_bids = {}
                        for lot in lots:
                            st.markdown(f"**{lot['name']}** *({lot['category']})*")
                            st.write(f"Base d'asta: **{lot['base_price']:,} €** — {lot['desc']}")
                            new_bids[lot["id"]] = st.number_input(
                                f"La tua offerta per {lot['id']} (€)",
                                min_value=0,
                                max_value=balance,
                                value=int(existing_bids[lot["id"]]),
                                step=100,
                                key=f"input_{lot['id']}_{cur_round}"
                            )
                            st.markdown("---")

                        save_bids = st.form_submit_button("✅ Conferma Offerte Segrete", type="primary")
                        if save_bids:
                            ok, msg = submit_player_bids(me, new_bids)
                            if ok:
                                st.success(msg)
                            else:
                                st.error(msg)

                with tab_scambi:
                    st.write("Trasferisci denaro oppure **vendi/cedi un oggetto** del tuo inventario a un altro giocatore:")
                    if not other_players:
                        st.info("Nessun altro giocatore al tavolo.")
                    else:
                        trade_options = {"NONE": "💸 Solo denaro (Bonifico semplice)"}
                        for item in my_inv:
                            trade_options[item["id"]] = f"📦 Cedi lotto: {item['name']} ({item['category']})"

                        with st.form("trade_transfer_form"):
                            selected_lot_key = st.selectbox(
                                "Cosa vuoi inviare / cedere?",
                                options=list(trade_options.keys()),
                                format_func=lambda k: trade_options[k]
                            )
                            target_player = st.selectbox("A quale giocatore?", other_players)
                            amount_val = st.number_input(
                                "Importo in € (se cedi un lotto, è il prezzo che incassi da lui; 0 € = regalo)",
                                min_value=0,
                                max_value=50000,
                                step=100,
                                value=500
                            )
                            confirm_trade = st.form_submit_button("🤝 Conferma Operazione Subito")
                            if confirm_trade:
                                lot_to_send = None if selected_lot_key == "NONE" else selected_lot_key
                                ok, msg = execute_trade_or_transfer(me, target_player, lot_to_send, int(amount_val))
                                if ok:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)

                with tab_inv:
                    if not my_inv:
                        st.info("Non hai ancora nessun lotto in inventario.")
                    else:
                        show_perizie = st.toggle("🔍 Mostra Perizie Riservate sui tuoi oggetti (non farti sbirciare!)", value=False)
                        for item in my_inv:
                            st.markdown(f"**• {item['name']}** *({item['category']})*")
                            if show_perizie:
                                st.markdown(f"<div class='appraisal-box'>{item['flash_news']}</div>", unsafe_allow_html=True)

            # --- ESITO DEL ROUND ---
            elif current_phase == "ESITO_ROUND":
                st.markdown(f'<div class="status-banner">📢 ESITO ROUND {cur_round}/{TOTAL_ROUNDS}</div>', unsafe_allow_html=True)

                if my_won_news:
                    st.success("🎉 Ti sei aggiudicato almeno un lotto in questo round!")
                    show_new_perizia = st.toggle("🕵️ Leggi la PERIZIA RISERVATA sui tuoi nuovi acquisti (Faccia da Poker!)", value=True)
                    if show_new_perizia:
                        for entry in my_won_news:
                            st.markdown(
                                f"<div class='appraisal-box'><b>{entry['lot_name']}</b><br><br>{entry['news']}</div>",
                                unsafe_allow_html=True
                            )
                else:
                    st.info("Non hai vinto lotti in questo round. Guarda il Tabellone TV per vedere chi ha comprato cosa!")

                st.subheader("🎒 Il tuo Inventario completo")
                if not my_inv:
                    st.write("Nessun lotto in portafoglio.")
                else:
                    show_all_inv = st.toggle("👁️ Mostra tutte le perizie dell'inventario", value=False)
                    for item in my_inv:
                        st.markdown(f"- **{item['name']}** (*{item['category']}*)")
                        if show_all_inv:
                            st.markdown(f"<div class='appraisal-box'>{item['flash_news']}</div>", unsafe_allow_html=True)

            # --- CLASSIFICA FINALE ---
            elif current_phase == "CLASSIFICA_FINALE":
                st.markdown('<div class="status-banner">🏆 PARTITA TERMINATA — VALORI SVELATI!</div>', unsafe_allow_html=True)
                standings = calculate_final_standings()
                my_row = next((r for r in standings if r["Giocatore"] == me), None)
                if my_row:
                    rank = standings.index(my_row) + 1
                    st.metric("La tua Posizione Finale", f"#{rank} su {len(standings)}", f"{my_row['PATRIMONIO TOTALE']:,} €")
                    st.write(f"- **Saldo Liquido:** {my_row['Saldo Liquido']:,} €")
                    st.write(f"- **Valore Reale Asset:** {my_row['Valore Asset']:,} €")
                    st.write(f"- **Bonus Obiettivo ({my_row['Obiettivo Segreto']}):** +{my_row['Bonus Obiettivo']:,} €")
                    st.write(f"**Dettaglio Asset:** {my_row['Dettaglio Asset']}")

        render_player_dashboard()

# ==============================================================================
# VISTA 2: TABELLONE PUBBLICO (TV / LAPTOP SUL TAVOLO)
# ==============================================================================
elif st.session_state.view_mode == "board":
    b_col1, b_col2 = st.columns([5, 1])
    with b_col1:
        st.title("🏔️ MERCATO NERO AL RIFUGIO")
    with b_col2:
        if st.button("🏠 Home"):
            set_mode("home")
            st.rerun()

    @st.fragment(run_every=3)
    def render_public_board():
        with state.lock:
            phase = state.phase
            cur_round = state.current_round
            players_snapshot = {
                k: {"balance": v["balance"], "count": len(v["inventory"])}
                for k, v in state.players.items()
            }
            bids_snapshot = {
                lid: len(b_dict) for lid, b_dict in state.current_bids.items()
            }
            results_snapshot = list(state.last_round_results)
            transfers_snapshot = list(state.transfer_log[:5])

        if phase == "LOBBY":
            st.markdown('<div class="status-banner">🥂 TAVOLO APERTO — INQUADRA IL QR CODE E UNISCITI</div>', unsafe_allow_html=True)
            st.subheader(f"Giocatori al tavolo ({len(players_snapshot)}/12):")
            if not players_snapshot:
                st.info("Nessun giocatore ancora connesso. Usa lo smartphone per entrare!")
            else:
                cols = st.columns(4)
                for idx, p_name in enumerate(players_snapshot.keys()):
                    with cols[idx % 4]:
                        st.success(f"🎩 **{p_name}** — {INITIAL_BUDGET:,} €")

        elif phase == "CONTRATTAZIONE_E_ASTA":
            st.markdown(
                f'<div class="status-banner">🔥 ROUND {cur_round} DI {TOTAL_ROUNDS} — CONTRATTAZIONE, SCAMBI & ASTA AL BUIO</div>',
                unsafe_allow_html=True
            )

            lots = get_round_lots(cur_round)
            lot_cols = st.columns(len(lots))
            for idx, lot in enumerate(lots):
                num_bidders = bids_snapshot.get(lot["id"], 0)
                with lot_cols[idx]:
                    st.markdown(f"""
                    <div class="lot-card">
                        <div class="lot-cat">{lot['category']}</div>
                        <div class="lot-title">{lot['name']}</div>
                        <div class="lot-desc">{lot['desc']}</div>
                        <div class="lot-price">Base d'asta: {lot['base_price']:,} €</div>
                        <div style="margin-top:10px; font-size:0.9rem; color:#cbd5e1;">
                            📩 Offerte ricevute: <b>{num_bidders}</b>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            st.divider()
            c_left, c_right = st.columns([2, 1])
            with c_left:
                st.subheader("💼 Situazione Giocatori (Liquidità Pubblica)")
                p_cols = st.columns(3)
                for idx, (p_name, info) in enumerate(players_snapshot.items()):
                    with p_cols[idx % 3]:
                        st.metric(
                            label=f"{p_name} ({info['count']} asset)",
                            value=f"{info['balance']:,} €"
                        )
            with c_right:
                st.subheader("🕵️ Movimenti & Scambi")
                if not transfers_snapshot:
                    st.write("Nessun movimento effettuato finora...")
                else:
                    for t_msg in transfers_snapshot:
                        st.markdown(t_msg)

        elif phase == "ESITO_ROUND":
            st.markdown(
                f'<div class="status-banner">🔨 MARTELLO BATTUTO — ESITO ROUND {cur_round} DI {TOTAL_ROUNDS}</div>',
                unsafe_allow_html=True
            )

            st.subheader("🏆 Aggiudicazioni del Round")
            res_cols = st.columns(len(results_snapshot))
            for idx, res in enumerate(results_snapshot):
                with res_cols[idx]:
                    if res["sold"]:
                        st.markdown(f"""
                        <div class="lot-card">
                            <div class="lot-cat">{res['category']}</div>
                            <div class="lot-title">{res['lot_name']}</div>
                            <div style="font-size:1.1rem; margin-top:8px; color:#f8fafc;">
                                Aggiudicato a: <b style="color:#60a5fa;">{res['winner']}</b>
                            </div>
                            <div class="lot-price">Prezzo battuto: {res['price']:,} €</div>
                            <div style="font-size:0.85rem; color:#fde047; margin-top:8px;">
                                🤫 Perizia inviata in privato al telefono di {res['winner']}!
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="lot-card" style="border-left-color:#94a3b8;">
                            <div class="lot-cat">{res['category']}</div>
                            <div class="lot-title">{res['lot_name']}</div>
                            <div style="color:#cbd5e1; margin-top:8px;">❌ Lotto invenduto (nessuna offerta valida)</div>
                        </div>
                        """, unsafe_allow_html=True)

            st.info("👀 Guardate in faccia chi ha comprato i lotti: hanno appena ricevuto la perizia segreta sul loro telefono!")

        elif phase == "CLASSIFICA_FINALE":
            st.markdown('<div class="status-banner">🏆 CLASSIFICA FINALE — TUTTI I VALORI SVELATI!</div>', unsafe_allow_html=True)
            standings = calculate_final_standings()

            if standings:
                pod_cols = st.columns(min(3, len(standings)))
                medals = ["🥇 1° POSTO", "🥈 2° POSTO", "🥉 3° POSTO"]
                for idx in range(min(3, len(standings))):
                    row = standings[idx]
                    with pod_cols[idx]:
                        st.markdown(f"""
                        <div class="lot-card">
                            <div class="lot-cat">{medals[idx]}</div>
                            <div class="lot-title">{row['Giocatore']}</div>
                            <div class="lot-price" style="font-size:1.45rem;">{row['PATRIMONIO TOTALE']:,} €</div>
                            <div style="font-size:0.95rem; margin-top:6px; color:#f8fafc;">{row['Obiettivo Segreto']}</div>
                        </div>
                        """, unsafe_allow_html=True)

                st.subheader("📊 Dettaglio Patrimoni e Rivelazione Asset")
                st.dataframe(standings, use_container_width=True, hide_index=True)

    render_public_board()

# ==============================================================================
# VISTA 3: PANNELLO REGIA / MASTER (MODALITÀ ANTI-SPOILER PER GIOCARE ANCHE TU!)
# ==============================================================================
elif st.session_state.view_mode == "admin":
    a_col1, a_col2 = st.columns([4, 1])
    with a_col1:
        st.title("🎛️ Pannello Regia — Master")
    with a_col2:
        if st.button("🏠 Home"):
            set_mode("home")
            st.rerun()

    if not st.session_state.get("admin_authenticated", False):
        pwd = st.text_input("Password Regia", type="password")
        if st.button("Sblocca Regia", type="primary"):
            if pwd == ADMIN_PASSWORD:
                st.session_state.admin_authenticated = True
                st.rerun()
            else:
                st.error("Password errata!")
    else:
        @st.fragment(run_every=3)
        def render_admin_panel():
            with state.lock:
                phase = state.phase
                cur_round = state.current_round
                num_players = len(state.players)
                lots = get_round_lots(cur_round)
                bidders_list = sorted({
                    p for lid in [l["id"] for l in lots]
                    for p in state.current_bids.get(lid, {}).keys()
                })
                player_names_list = list(state.players.keys())

            st.info(f"**Stato:** `{phase}` | **Round:** `{cur_round}/{TOTAL_ROUNDS}` | **Giocatori:** `{num_players}`")

            if phase == "LOBBY":
                st.write("Quando tutti (incluso te!) siete entrati dalla vista Giocatore, avvia la partita:")
                if st.button("🚀 AVVIA PARTITA (7 Round, 7 Obiettivi e Soffiate)", type="primary"):
                    ok, msg = start_game()
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

            elif phase == "CONTRATTAZIONE_E_ASTA":
                st.write(f"Hanno già inviato un'offerta: **{len(bidders_list)} / {num_players}**")
                if bidders_list:
                    st.write(f"Offerte confermate da: **{', '.join(bidders_list)}**")
                if st.button("🔨 CHIUDI ASTA E INVIA PERIZIE AI VINCITORI", type="primary"):
                    resolve_current_round()
                    st.rerun()

            elif phase == "ESITO_ROUND":
                if cur_round < TOTAL_ROUNDS:
                    if st.button(f"➡️ PASSA AL ROUND {cur_round + 1}", type="primary"):
                        advance_to_next_round()
                        st.rerun()
                else:
                    if st.button("🏆 MOSTRA CLASSIFICA FINALE E SVELA TUTTI I VALORI", type="primary"):
                        advance_to_next_round()
                        st.rerun()

            elif phase == "CLASSIFICA_FINALE":
                st.success("Partita conclusa! Il podio e i valori reali sono visibili sul Tabellone e sui telefoni.")

            st.divider()
            with st.expander("🔑 Recupero PIN Giocatori (Senza Spoiler sugli Obiettivi)"):
                with state.lock:
                    for p_n in player_names_list:
                        st.write(f"- **{p_n}** → PIN: `{state.players[p_n]['pin']}`")

            with st.expander("⚠️ Zona Pericolo: Reset Partita"):
                if st.button("🔄 RESETTA TUTTA LA PARTITA", type="secondary"):
                    reset_entire_game()
                    st.warning("Partita resettata! Tutti tornano alla Lobby.")
                    st.rerun()

        render_admin_panel()

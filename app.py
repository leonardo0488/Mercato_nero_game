import streamlit as st
import threading
import random
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

# ==============================================================================
# CONFIGURAZIONE PAGINA E STILE GRAFICO ("RIFUGIO NOIR / ALTA FINANZA")
# ==============================================================================
st.set_page_config(
    page_title="Mercato Nero al Rifugio",
    page_icon="🏔️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

CUSTOM_CSS = """
<style>
    /* Tema scuro elegante ad alto contrasto */
    .stApp {
        background-color: #0e1117;
        color: #f0f2f6;
    }
    /* Card dei lotti e box informativi */
    .lot-card {
        background: linear-gradient(145deg, #1a1f2c, #141821);
        border: 1px solid #2e3748;
        border-left: 5px solid #d4af37;
        border-radius: 10px;
        padding: 18px;
        margin-bottom: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    }
    .lot-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #f5d061;
        margin-bottom: 4px;
    }
    .lot-cat {
        display: inline-block;
        background-color: #262f40;
        color: #93c5fd;
        font-size: 0.75rem;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 4px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 8px;
    }
    .lot-price {
        font-size: 1.1rem;
        font-weight: 700;
        color: #34d399;
        margin-top: 8px;
    }
    /* Box Soffiata Segreta */
    .tip-box {
        background: linear-gradient(135deg, #3b0d11, #1f090d);
        border: 1px solid #ef4444;
        border-radius: 10px;
        padding: 16px;
        margin: 12px 0;
        color: #fecaca;
    }
    /* Box Notizia Flash sul Tabellone */
    .flash-news {
        background: linear-gradient(90deg, #1e293b, #0f172a);
        border: 2px solid #f59e0b;
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
        font-size: 1.15rem;
    }
    /* Badge Stato */
    .status-banner {
        background-color: #1e293b;
        border-radius: 8px;
        padding: 10px 16px;
        text-align: center;
        font-weight: 700;
        letter-spacing: 0.05em;
        border: 1px solid #334155;
        margin-bottom: 20px;
    }
    /* Migliora leggibilità bottoni su mobile */
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ==============================================================================
# DATASET DI GIOCO: CATALOGO LOTTI, SOFFIATE, NOTIZIE FLASH E OBIETTIVI
# ==============================================================================
INITIAL_BUDGET = 10000
TOTAL_ROUNDS = 5
ADMIN_PASSWORD = "admin123"

# Struttura Lotti:
# - base_price: prezzo minimo d'asta
# - true_base_value: valore reale intrinseco prima dei moltiplicatori (0 se falso)
# - is_fake: True se è una truffa/falso (rilevante per Falsario e Collezionista)
# - volatility_tag: chiave per applicare i moltiplicatori delle Notizie Flash
CATALOGO_LOTTI = [
    # --- ROUND 1 ---
    {
        "id": "L01", "round": 1, "category": "Arte",
        "name": "Tela 'Bambina col Palloncino Sgonfio' di Banksy",
        "desc": "Trovata dietro un cassonetto a Bristol. Autenticata su un tovagliolo da pub.",
        "base_price": 1200, "true_base_value": 0, "is_fake": True, "tag": "arte_urbana",
        "tip": "SOFFIATA DAL RESTAURATORE: La vernice è acrilico Ikea del 2022. È un FALSO totale (valore base 0 €)!",
        "flash_news": "📰 FLASH ARTE: Un critico svizzero smaschera una serie di falsi Banksy venduti sulle Alpi!"
    },
    {
        "id": "L02", "round": 1, "category": "Tech & Biotech",
        "name": "Brevetto 'Caffè Decaffeinato che Sveglia'",
        "desc": "Molecola sperimentale svizzera. Promette zero tachicardia e 12 ore di focus.",
        "base_price": 1500, "true_base_value": 2500, "is_fake": False, "tag": "biotech_caffe",
        "tip": "SOFFIATA DAL LABORATORIO: I test clinici sono un trionfo! A fine asta il valore di questo brevetto RADDOPPIERÀ.",
        "flash_news": "📰 FLASH BIOTECH: Una multinazionale del caffè lancia un'OPA sul brevetto alpino! Valore x2!"
    },
    {
        "id": "L03", "round": 1, "category": "Lusso & Orologi",
        "name": "Cronografo 'Rolex Sub-Zero' anni '70",
        "desc": "Appartenuto a un famoso istruttore di sci di Cortina. Cinturino leggermente vissuto.",
        "base_price": 1800, "true_base_value": 3000, "is_fake": False, "tag": "orologi_epoca",
        "tip": "SOFFIATA DALL'OROLOGIAIO: Il movimento interno è originale e rarissimo. Vale almeno 3.000 € reali.",
        "flash_news": "📰 FLASH LUSSO: L'asta di Ginevra conferma il boom degli orologi sportivi vintage (+20% valore)!"
    },

    # --- ROUND 2 ---
    {
        "id": "L04", "round": 2, "category": "Materie Prime",
        "name": "Lingotto d'Oro Elvetico (500g)",
        "desc": "Punzonato Zurigo 999.9. Pesante, freddo al tatto e molto rassicurante.",
        "base_price": 2200, "true_base_value": 3500, "is_fake": False, "tag": "oro_fisico",
        "tip": "SOFFIATA FINANZIARIA: I mercati stanno per crollare: i beni rifugio come l'oro saliranno di un altro +30%!",
        "flash_news": "📰 FLASH MERCATI: Tensione sulle valute! Gli investitori corrono sull'Oro fisico (+30% valore)!"
    },
    {
        "id": "L05", "round": 2, "category": "Finanza & Crypto",
        "name": "Chiavetta USB con 50 'AlpineCoin'",
        "desc": "Criptovaluta minata usando il calore di una stufa a pellet. Password scritta su post-it.",
        "base_price": 1000, "true_base_value": 4000, "is_fake": False, "tag": "crypto_meme",
        "tip": "SOFFIATA DA REDDIT: Elon sta per twittare una foto delle Dolomiti! Questa chiavetta varrà una fortuna (4.000 €).",
        "flash_news": "📰 FLASH CRYPTO: Tweet virale di un miliardario tech fa schizzare AlpineCoin alle stelle!"
    },
    {
        "id": "L06", "round": 2, "category": "Arte",
        "name": "Scultura Minimalista 'Aria di Montagna'",
        "desc": "Teca in plexiglass sigillata nel 1998 a Chamonix. Opera concettuale.",
        "base_price": 800, "true_base_value": 2400, "is_fake": False, "tag": "arte_concettuale",
        "tip": "SOFFIATA DA SOTHEBY'S: È un'opera autentica e quotatissima dell'arte povera. Vale ben 2.400 €!",
        "flash_news": "📰 FLASH CULTURA: Il MoMA acquisisce una teca gemella di 'Aria di Montagna'. Quotazioni solide!"
    },

    # --- ROUND 3 ---
    {
        "id": "L07", "round": 3, "category": "Tech & Biotech",
        "name": "Algoritmo AI 'Prevedi-Valanghe'",
        "desc": "Software predittivo basato su reti neurali e vecchi proverbi dei montanari.",
        "base_price": 1600, "true_base_value": 0, "is_fake": True, "tag": "ai_truffa",
        "tip": "SOFFIATA DALLO SVILUPPATORE: Il codice è solo un 'random.choice([True, False])'. È una TRUFFA (0 €)!",
        "flash_news": "📰 FLASH TECH: Audit indipendente scopre che l'AI Prevedi-Valanghe era un foglio Excel truccato!"
    },
    {
        "id": "L08", "round": 3, "category": "Lusso & Orologi",
        "name": "Bottiglia Romanée-Conti 1985 (Ritrovata in Cantina)",
        "desc": "Etichetta macchiata d'umidità, livello del vino perfetto. Da collezione.",
        "base_price": 2000, "true_base_value": 3800, "is_fake": False, "tag": "vino_raro",
        "tip": "SOFFIATA DEL SOMMELIER: Conservata a 11°C costanti per 40 anni. È autentica e vale 3.800 €!",
        "flash_news": "📰 FLASH ENOLOGIA: Record asiatico per i Borgogna d'annata! La bottiglia del 1985 vola a 3.800 €!"
    },
    {
        "id": "L09", "round": 3, "category": "Finanza & Crypto",
        "name": "Azioni 'Funivie del Cervino S.p.A.'",
        "desc": "Pacchetto azionario di minoranza. Bilanci in rosso ma vista panoramica mozzafiato.",
        "base_price": 1400, "true_base_value": 2800, "is_fake": False, "tag": "azioni_turismo",
        "tip": "SOFFIATA ISTITUZIONALE: Approvati fondi europei per i nuovi impianti! Il titolo raddoppia a 2.800 €.",
        "flash_news": "📰 FLASH BORSA: Sbloccati i fondi per le infrastrutture alpine! Funivie del Cervino +100%!"
    },

    # --- ROUND 4 ---
    {
        "id": "L10", "round": 4, "category": "Materie Prime",
        "name": "Concessione Miniere di Litio 'Val di Fassa'",
        "desc": "Diritti di estrazione in un terreno roccioso dietro un rifugio dismesso.",
        "base_price": 2000, "true_base_value": 4500, "is_fake": False, "tag": "litio_verde",
        "tip": "SOFFIATA GEOLOGICA: Hanno trovato il giacimento di litio più puro d'Europa! Vale ben 4.500 €.",
        "flash_news": "📰 FLASH ENERGIA: Confermato mega-giacimento di litio sulle Alpi! Valore della concessione alle stelle!"
    },
    {
        "id": "L11", "round": 4, "category": "Arte",
        "name": "Schizzo a Carboncino di Picasso (Sul Menù)",
        "desc": "Disegnato nel 1954 dopo tre grappe. Firma leggibile con molta immaginazione.",
        "base_price": 1700, "true_base_value": 3600, "is_fake": False, "tag": "picasso_menu",
        "tip": "SOFFIATA DALL'ARCHIVIO PICASSO: Il maestro era davvero in quel ristorante nel '54! È AUTENTICO (3.600 €).",
        "flash_news": "📰 FLASH ARTE: La Fondazione Picasso inserisce lo 'Schizzo sul Menù' nel catalogo ufficiale!"
    },
    {
        "id": "L12", "round": 4, "category": "Lusso & Orologi",
        "name": "Diamante Blu 'Cuore delle Dolomiti'",
        "desc": "Taglio brillante, 3 carati. Certificato gemmologico stampato su carta lucida.",
        "base_price": 2100, "true_base_value": 0, "is_fake": True, "tag": "diamante_vetro",
        "tip": "SOFFIATA DEL GIOIELLIERE: È zircone sintetico lucidato! Valore reale 0 € (a meno che tu non sia il Falsario).",
        "flash_news": "📰 FLASH CRONACA: Il 'Cuore delle Dolomiti' risulta essere vetro al piombo di Murano! Crollo a 0 €!"
    },

    # --- ROUND 5 (GRAN FINALE) ---
    {
        "id": "L13", "round": 5, "category": "Finanza & Crypto",
        "name": "Fondo Speculativo 'Offshore Cayman-Lugano'",
        "desc": "Quote al portatore di un fondo anonimo. Nessuna domanda, alti rendimenti.",
        "base_price": 2500, "true_base_value": 5200, "is_fake": False, "tag": "fondo_offshore",
        "tip": "SOFFIATA BANCARIA: Il fondo ha appena chiuso un arbitraggio milionario! Le quote valgono 5.200 €.",
        "flash_news": "📰 FLASH FINANZA: Dividendo straordinario per il Fondo Cayman-Lugano! Liquidazione a 5.200 €!"
    },
    {
        "id": "L14", "round": 5, "category": "Materie Prime",
        "name": "Barile di Petrolio Greggio 'Brent Alpino'",
        "desc": "Estratto per errore scavando una piscina riscaldata a St. Moritz.",
        "base_price": 1500, "true_base_value": 0, "is_fake": True, "tag": "petrolio_finto",
        "tip": "SOFFIATA CHIMICA: Non è petrolio, è olio esausto di friggitrice industriale! Vale 0 €.",
        "flash_news": "📰 FLASH AMBIENTE: Analisi confermano che il 'Brent Alpino' è olio di frittura usato! Valore 0 €!"
    },
    {
        "id": "L15", "round": 5, "category": "Tech & Biotech",
        "name": "Prototipo Batteria a Stato Solido 'Tesla-Alps'",
        "desc": "Cella energetica grande come un libro che ricarica un'auto in 90 secondi.",
        "base_price": 2400, "true_base_value": 5000, "is_fake": False, "tag": "batteria_solida",
        "tip": "SOFFIATA INDUSTRIALE: Funziona davvero! È il santo graal dell'automotive e vale 5.000 € reali.",
        "flash_news": "📰 FLASH MOTORI: Accordo storico per la batteria 'Tesla-Alps'! Valutazione record a 5.000 €!"
    },
]

# Moltiplicatori applicati dopo la Notizia Flash sul valore base
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
        "desc": "Ottieni +4.000 € bonus a fine partita se chiudi con almeno 4.000 € di saldo liquido."
    },
    {
        "id": "OBJ_MONOPOLIO",
        "name": "👑 Monopolista",
        "desc": "Se possiedi almeno 3 asset della STESSA categoria, il valore finale di quegli asset RADDOPPIA."
    },
    {
        "id": "OBJ_FALSARIO",
        "name": "🎭 Il Falsario",
        "desc": "Ribalti il mercato nero: i lotti FALSI che acquisti non valgono 0 €, ma +3.000 € ciascuno!"
    },
    {
        "id": "OBJ_SPECULATORE",
        "name": "🌐 Speculatore Diversificato",
        "desc": "Ottieni +1.500 € bonus per ogni categoria DIVERSA di asset presente nel tuo inventario finale."
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
    # Struttura players[name]:
    # {
    #   "pin": "1234",
    #   "balance": 10000,
    #   "objective": dict,
    #   "inventory": List[dict], # lotti vinti
    #   "tips": Dict[int, str],   # round -> testo soffiata
    # }
    # Offerte del round corrente: bids[lot_id][player_name] = {"amount": int, "timestamp": float}
    current_bids: Dict[str, Dict[str, dict]] = field(default_factory=dict)
    # Risultati dell'ultimo round risolto
    last_round_results: List[dict] = field(default_factory=list)
    # Log bonifici recenti (pubblico sul tabellone per creare sospetto!)
    transfer_log: List[str] = field(default_factory=list)
    # Eventi/Notizie flash sbloccate
    unlocked_news: List[str] = field(default_factory=list)

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
    """Calcola il valore reale di mercato del lotto dopo le notizie flash."""
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
        # Se il giocatore esiste già, verifica il PIN (utile per rientro dopo refresh/chiusura browser)
        if clean_name in state.players:
            if state.players[clean_name]["pin"] == clean_pin:
                return True, f"Bentornato al tavolo, {clean_name}!"
            else:
                return False, "Nome già registrato con un altro PIN! Controlla il PIN o usa un altro nome."

        # Nuovo giocatore
        if state.phase != "LOBBY":
            return False, "La partita è già iniziata! Chiedi alla Regia di resettare se devi entrare."
        if len(state.players) >= 12:
            return False, "Tavolo pieno (massimo 12 giocatori)."

        state.players[clean_name] = {
            "pin": clean_pin,
            "balance": INITIAL_BUDGET,
            "objective": None,
            "inventory": [],
            "tips": {}
        }
        return True, f"Registrazione completata! Ricorda il tuo PIN ({clean_pin})."

def assign_tips_for_round(round_num: int):
    """Assegna 2 o 3 soffiate segrete a giocatori casuali sui lotti del round."""
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
        # Assegna obiettivi segreti (mescolati, ciclando se > 5 giocatori)
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

        state.current_round = 1
        state.current_bids = {}
        state.last_round_results = []
        state.transfer_log = []
        state.unlocked_news = []
        state.phase = "CONTRATTAZIONE_E_ASTA"
        assign_tips_for_round(1)
        return True, "Partita avviata! Obiettivi e prime soffiate distribuiti."

def execute_transfer(sender: str, recipient: str, amount: int) -> tuple[bool, str]:
    if sender == recipient:
        return False, "Non puoi fare un bonifico a te stesso."
    if amount <= 0:
        return False, "L'importo deve essere maggiore di 0 €."

    with state.lock:
        if state.phase != "CONTRATTAZIONE_E_ASTA":
            return False, "I bonifici sono consentiti solo durante la fase di Contrattazione e Asta."
        if sender not in state.players or recipient not in state.players:
            return False, "Giocatore non trovato."
        if state.players[sender]["balance"] < amount:
            return False, "Fondi insufficienti per questo bonifico."

        # Verifica che il sender abbia comunque abbastanza liquidità per coprire le offerte già piazzate
        committed_bids = sum(
            bids_by_player.get(sender, {}).get("amount", 0)
            for bids_by_player in state.current_bids.values()
        )
        if state.players[sender]["balance"] - amount < committed_bids:
            return False, (
                f"Hai già {committed_bids:,} € impegnati nelle offerte d'asta di questo round! "
                "Riduci prima le tue offerte o trasferisci meno denaro."
            )

        state.players[sender]["balance"] -= amount
        state.players[recipient]["balance"] += amount
        timestamp_str = time.strftime("%H:%M:%S")
        state.transfer_log.insert(
            0, f"💸 [{timestamp_str}] **{sender}** ha inviato un bonifico segreto a **{recipient}**"
        )
        return True, f"Bonifico di {amount:,} € inviato a {recipient}!"

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
                # Preserva il timestamp precedente se l'importo non è cambiato, altrimenti aggiorna
                prev = state.current_bids[lid].get(player_name)
                ts = prev["timestamp"] if (prev and prev["amount"] == amt) else now
                state.current_bids[lid][player_name] = {"amount": amt, "timestamp": ts}
            else:
                state.current_bids[lid].pop(player_name, None)

        return True, f"Offerte registrate! Totale impegnato: {total_bid:,} €."

def resolve_current_round():
    """Chiude l'asta del round corrente, assegna i lotti ai vincitori e pubblica le Notizie Flash."""
    with state.lock:
        lots = get_round_lots(state.current_round)
        results = []
        round_news = []

        for lot in lots:
            lid = lot["id"]
            lot_bids = state.current_bids.get(lid, {})
            valid_bids = [
                (p_name, info["amount"], info["timestamp"])
                for p_name, info in lot_bids.items()
                if info["amount"] >= lot["base_price"]
            ]

            if valid_bids:
                # Ordina per importo decrescente, e a parità per timestamp crescente (chi offre prima vince)
                valid_bids.sort(key=lambda x: (-x[1], x[2]))
                winner_name, winning_price, _ = valid_bids[0]

                # Scala saldo (con sicurezza) e aggiungi all'inventario
                if state.players[winner_name]["balance"] >= winning_price:
                    state.players[winner_name]["balance"] -= winning_price
                    state.players[winner_name]["inventory"].append(lot)
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

            round_news.append(lot["flash_news"])

        state.last_round_results = results
        state.unlocked_news = round_news
        state.current_bids = {}
        state.phase = "ESITO_ROUND"

def advance_to_next_round():
    with state.lock:
        if state.current_round < TOTAL_ROUNDS:
            state.current_round += 1
            state.last_round_results = []
            state.unlocked_news = []
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
        state.unlocked_news = []

def calculate_final_standings() -> List[dict]:
    """Calcola punteggio finale di tutti i giocatori includendo valori reali e obiettivi segreti."""
    standings = []
    with state.lock:
        for p_name, p_data in state.players.items():
            cash = p_data["balance"]
            inv = p_data["inventory"]
            obj = p_data["objective"]
            obj_id = obj["id"] if obj else ""

            # Conta categorie per eventuale Monopolista
            cat_counts: Dict[str, int] = {}
            for item in inv:
                cat_counts[item["category"]] = cat_counts.get(item["category"], 0) + 1

            assets_value = 0
            asset_details = []

            for item in inv:
                val = compute_lot_real_value(item)
                # Regola Monopolista: se >= 3 asset della stessa categoria, valore raddoppia
                if obj_id == "OBJ_MONOPOLIO" and cat_counts[item["category"]] >= 3:
                    val *= 2
                assets_value += val
                tag_status = "FALSO (0 €)" if item["is_fake"] else f"Reale: {val:,} €"
                asset_details.append(f"{item['name']} [{tag_status}]")

            # Calcolo Bonus Obiettivo Segreto
            bonus = 0
            if obj_id == "OBJ_ARTE":
                auth_art = sum(1 for i in inv if i["category"] == "Arte" and not i["is_fake"])
                bonus = auth_art * 2500
            elif obj_id == "OBJ_SQUALO":
                if cash >= 4000:
                    bonus = 4000
            elif obj_id == "OBJ_MONOPOLIO":
                # Il bonus è già integrato nel raddoppio valore asset, calcoliamo la differenza per mostrarla
                base_sum = sum(compute_lot_real_value(i) for i in inv)
                bonus = assets_value - base_sum
                assets_value = base_sum  # separiamo per chiarezza in tabella
            elif obj_id == "OBJ_FALSARIO":
                fakes = sum(1 for i in inv if i["is_fake"])
                bonus = fakes * 3000
            elif obj_id == "OBJ_SPECULATORE":
                unique_cats = len(cat_counts)
                bonus = unique_cats * 1500

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
    st.markdown("##### *Aste al buio, soffiate segrete e tradimenti tra una portata e l'altra.*")
    st.divider()

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 📱 Giocatore")
        st.write("Entra dal tuo smartphone per ricevere soffiate, fare bonifici e puntare all'asta.")
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
        st.write("Controlla il ritmo della serata, avvia i round e chiudi le aste (richiede password).")
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

    # Login / Registrazione Giocatore
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

        # Frammento auto-aggiornante ogni 3 secondi per sincronizzare fasi, saldi e soffiate
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
                other_players = [n for n in state.players.keys() if n != me]

            # Intestazione Profilo & Saldo
            st.markdown(f"👤 **{me}** | 💰 Saldo Liquido: **:green[{balance:,} €]**")

            # Obiettivo Segreto con toggle anti-sbirciata
            if objective:
                show_obj = st.toggle("👁️ Mostra Obiettivo Segreto (occhio agli sguardi indiscreti!)", value=False)
                if show_obj:
                    st.warning(f"**{objective['name']}**\n\n{objective['desc']}")

            st.divider()

            # --- FASE 1: LOBBY ---
            if current_phase == "LOBBY":
                st.markdown('<div class="status-banner">⏳ IN ATTESA CHE LA REGIA AVVII LA PARTITA...</div>', unsafe_allow_html=True)
                st.write(f"Giocatori connessi finora: **{len(state.players)}**")
                st.write("Prepara la tua faccia da poker. Quando tutti sono pronti, il Master avvierà il Round 1.")

            # --- FASE 2: CONTRATTAZIONE E ASTA AL BUIO ---
            elif current_phase == "CONTRATTAZIONE_E_ASTA":
                st.markdown(f'<div class="status-banner">🔥 ROUND {cur_round}/{TOTAL_ROUNDS} — CONTRATTAZIONE & ASTA</div>', unsafe_allow_html=True)

                # Soffiata Segreta del Round
                if my_tip:
                    show_tip = st.toggle("🕵️ Hai ricevuto una SOFFIATA SEGRETA! Tocca per leggere", value=True)
                    if show_tip:
                        st.markdown(f'<div class="tip-box"><b>🤫 INFORMAZIONE RISERVATA (Round {cur_round})</b><br><br>{my_tip}</div>', unsafe_allow_html=True)
                else:
                    st.caption("🔇 Nessuna soffiata ricevuta in questo round. Ascolta gli altri e cerca di capire chi mente!")

                # Tab per separare Asta, Bonifici e Inventario su schermo mobile
                tab_asta, tab_bonifico, tab_inv = st.tabs(["🔨 Asta al Buio", "💸 Bonifico", f"🎒 Inventario ({len(my_inv)})"])

                with tab_asta:
                    st.write("Inserisci la tua offerta segreta per ciascun lotto (`0 €` per passare). Puoi modificarla finché la Regia non chiude l'asta.")
                    lots = get_round_lots(cur_round)

                    # Recupera eventuali offerte già salvate dal giocatore
                    with state.lock:
                        existing_bids = {
                            lot["id"]: state.current_bids.get(lot["id"], {}).get(me, {}).get("amount", 0)
                            for lot in lots
                        }

                    with st.form(key=f"bid_form_r{cur_round}"):
                        new_bids = {}
                        for lot in lots:
                            st.markdown(f"**{lot['name']}** *({lot['category']})*")
                            st.caption(f"Base d'asta: {lot['base_price']:,} € — {lot['desc']}")
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

                with tab_bonifico:
                    st.write("Compra informazioni, stringi alleanze o paga il silenzio di qualcuno:")
                    if not other_players:
                        st.info("Nessun altro giocatore al tavolo.")
                    else:
                        with st.form("transfer_form"):
                            target = st.selectbox("Destinatario", other_players)
                            amt = st.number_input("Importo da trasferire (€)", min_value=100, max_value=max(100, balance), step=100, value=500)
                            send_btn = st.form_submit_button("💸 Invia Denaro Subito")
                            if send_btn:
                                ok, msg = execute_transfer(me, target, int(amt))
                                if ok:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)

                with tab_inv:
                    if not my_inv:
                        st.info("Non hai ancora acquistato nessun lotto.")
                    else:
                        for item in my_inv:
                            st.markdown(f"- **{item['name']}** (*{item['category']}*) — Pagato all'asta")

            # --- FASE 3: ESITO DEL ROUND ---
            elif current_phase == "ESITO_ROUND":
                st.markdown(f'<div class="status-banner">📢 ESITO ROUND {cur_round}/{TOTAL_ROUNDS}</div>', unsafe_allow_html=True)
                st.info("Guarda il Tabellone TV per scoprire chi si è aggiudicato i lotti e leggere le Notizie Flash!")
                st.subheader("🎒 Il tuo Inventario attuale")
                if not my_inv:
                    st.write("Nessun lotto in portafoglio.")
                else:
                    for item in my_inv:
                        st.markdown(f"- **{item['name']}** (*{item['category']}*)")

            # --- FASE 4: CLASSIFICA FINALE ---
            elif current_phase == "CLASSIFICA_FINALE":
                st.markdown('<div class="status-banner">🏆 PARTITA TERMINATA — GUARDA IL PODIO!</div>', unsafe_allow_html=True)
                standings = calculate_final_standings()
                my_row = next((r for r in standings if r["Giocatore"] == me), None)
                if my_row:
                    rank = standings.index(my_row) + 1
                    st.metric("La tua Posizione Finale", f"#{rank} su {len(standings)}", f"{my_row['PATRIMONIO TOTALE']:,} €")
                    st.write(f"- **Saldo Liquido:** {my_row['Saldo Liquido']:,} €")
                    st.write(f"- **Valore Reale Asset:** {my_row['Valore Asset']:,} €")
                    st.write(f"- **Bonus Obiettivo ({my_row['Obiettivo Segreto']}):** +{my_row['Bonus Obiettivo']:,} €")
                    st.caption(f"Asset: {my_row['Dettaglio Asset']}")

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
            news_snapshot = list(state.unlocked_news)
            transfers_snapshot = list(state.transfer_log[:4])

        # --- LOBBY ---
        if phase == "LOBBY":
            st.markdown('<div class="status-banner">🥂 TAVOLO APERTO — INQUADRA IL QR CODE E UNISCITI</div>', unsafe_allow_html=True)
            st.subheader(f"Giocatori al tavolo ({len(players_snapshot)}/12):")
            if not players_snapshot:
                st.info("Nessun giocatore ancora connesso. Usa lo smartphone per entrare!")
            else:
                cols = st.columns(4)
                for idx, p_name in enumerate(players_snapshot.keys()):
                    with cols[idx % 4]:
                        st.success(f"🎩 **{p_name}** — 10.000 €")

        # --- CONTRATTAZIONE E ASTA ---
        elif phase == "CONTRATTAZIONE_E_ASTA":
            st.markdown(
                f'<div class="status-banner">🔥 ROUND {cur_round} DI {TOTAL_ROUNDS} — CONTRATTAZIONE LIBERA & ASTA AL BUIO APERTA</div>',
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
                        <div>{lot['desc']}</div>
                        <div class="lot-price">Base d'asta: {lot['base_price']:,} €</div>
                        <div style="margin-top:10px; font-size:0.85rem; color:#94a3b8;">
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
                st.subheader("🕵️ Movimenti Bancari")
                if not transfers_snapshot:
                    st.caption("Nessun bonifico effettuato finora...")
                else:
                    for t_msg in transfers_snapshot:
                        st.markdown(t_msg)

        # --- ESITO ROUND ---
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
                            <div style="font-size:1.1rem; margin-top:8px;">
                                Aggiudicato a: <b style="color:#60a5fa;">{res['winner']}</b>
                            </div>
                            <div class="lot-price">Prezzo battuto: {res['price']:,} €</div>
                            <div style="font-size:0.8rem; color:#94a3b8; margin-top:6px;">
                                Valore reale coperto fino a fine partita!
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="lot-card" style="border-left-color:#64748b;">
                            <div class="lot-cat">{res['category']}</div>
                            <div class="lot-title">{res['lot_name']}</div>
                            <div style="color:#94a3b8; margin-top:8px;">❌ Lotto invenduto (nessuna offerta valida)</div>
                        </div>
                        """, unsafe_allow_html=True)

            st.subheader("📡 Ultime Notizie Flash dal Mercato")
            for news in news_snapshot:
                st.markdown(f'<div class="flash-news">{news}</div>', unsafe_allow_html=True)

        # --- CLASSIFICA FINALE ---
        elif phase == "CLASSIFICA_FINALE":
            st.markdown('<div class="status-banner">🏆 CLASSIFICA FINALE — LA VERITÀ VIENE A GALLA!</div>', unsafe_allow_html=True)
            standings = calculate_final_standings()

            if standings:
                # Podio Top 3
                pod_cols = st.columns(min(3, len(standings)))
                medals = ["🥇 1° POSTO", "🥈 2° POSTO", "🥉 3° POSTO"]
                for idx in range(min(3, len(standings))):
                    row = standings[idx]
                    with pod_cols[idx]:
                        st.markdown(f"""
                        <div class="lot-card">
                            <div class="lot-cat">{medals[idx]}</div>
                            <div class="lot-title">{row['Giocatore']}</div>
                            <div class="lot-price" style="font-size:1.4rem;">{row['PATRIMONIO TOTALE']:,} €</div>
                            <div style="font-size:0.9rem; margin-top:6px;">{row['Obiettivo Segreto']}</div>
                        </div>
                        """, unsafe_allow_html=True)

                st.subheader("📊 Dettaglio Patrimoni e Rivelazione Asset")
                st.dataframe(standings, use_container_width=True, hide_index=True)

    render_public_board()

# ==============================================================================
# VISTA 3: PANNELLO REGIA / MASTER (PROTETTO DA PASSWORD)
# ==============================================================================
elif st.session_state.view_mode == "admin":
    a_col1, a_col2 = st.columns([4, 1])
    with a_col1:
        st.title("🎛️ Pannello Regia — Master della Serata")
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
        with state.lock:
            phase = state.phase
            cur_round = state.current_round
            num_players = len(state.players)
            lots = get_round_lots(cur_round)
            bidders_count = len({
                p for lid in [l["id"] for l in lots]
                for p in state.current_bids.get(lid, {}).keys()
            })

        st.info(f"**Stato Attuale:** `{phase}` | **Round:** `{cur_round}/{TOTAL_ROUNDS}` | **Giocatori:** `{num_players}`")

        # Controlli di avanzamento flusso
        if phase == "LOBBY":
            st.write("Quando tutti gli amici sono entrati dal telefono, avvia la partita:")
            if st.button("🚀 AVVIA PARTITA (Distribuisci Obiettivi e Soffiate Round 1)", type="primary"):
                ok, msg = start_game()
                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

        elif phase == "CONTRATTAZIONE_E_ASTA":
            st.write(f"Giocatori che hanno già inviato almeno un'offerta in questo round: **{bidders_count} / {num_players}**")
            if st.button("🔨 CHIUDI ASTA E RIVELA ESITO ROUND", type="primary"):
                resolve_current_round()
                st.rerun()

        elif phase == "ESITO_ROUND":
            if cur_round < TOTAL_ROUNDS:
                if st.button(f"➡️ PASSA AL ROUND {cur_round + 1} (Nuovi Lotti & Nuove Soffiate)", type="primary"):
                    advance_to_next_round()
                    st.rerun()
            else:
                if st.button("🏆 MOSTRA CLASSIFICA FINALE E RIVELA TUTTI I VALORI", type="primary"):
                    advance_to_next_round()
                    st.rerun()

        elif phase == "CLASSIFICA_FINALE":
            st.success("Partita conclusa! Il podio è visibile sul Tabellone e sui telefoni.")

        st.divider()
        # Monitoraggio rapido per il Master
        with st.expander("📋 Lista Giocatori e PIN (in caso qualcuno dimentichi il PIN)"):
            with state.lock:
                for p_n, p_d in state.players.items():
                    obj_name = p_d["objective"]["name"] if p_d["objective"] else "Non assegnato"
                    st.write(f"- **{p_n}** | PIN: `{p_d['pin']}` | Saldo: `{p_d['balance']:,} €` | Obiettivo: *{obj_name}*")

        st.divider()
        with st.expander("⚠️ Zona Pericolo: Reset Partita"):
            if st.button("🔄 RESETTA TUTTA LA PARTITA", type="secondary"):
                reset_entire_game()
                st.warning("Partita resettata! Tutti tornano alla Lobby.")
                st.rerun()

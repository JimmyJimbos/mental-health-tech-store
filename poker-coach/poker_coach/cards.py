"""Carte e mazzo. Una carta e' una tupla (rank, suit) con rank 2..14 e suit in 'cdhs'."""

RANKS = "23456789TJQKA"
SUITS = "cdhs"
RANK_VALUE = {r: i + 2 for i, r in enumerate(RANKS)}
VALUE_RANK = {v: r for r, v in RANK_VALUE.items()}

FULL_DECK = [(RANK_VALUE[r], s) for r in RANKS for s in SUITS]


def parse_card(text):
    text = text.strip()
    if len(text) != 2:
        raise ValueError(f"Carta non valida: {text!r}")
    rank, suit = text[0].upper(), text[1].lower()
    if rank not in RANK_VALUE or suit not in SUITS:
        raise ValueError(f"Carta non valida: {text!r}")
    return (RANK_VALUE[rank], suit)


def parse_cards(text):
    """Accetta 'AhKd', 'Ah Kd', 'Ah,Kd' o '[Ah Kd]'."""
    cleaned = "".join(ch for ch in text if ch.isalnum())
    if len(cleaned) % 2:
        raise ValueError(f"Carte non valide: {text!r}")
    cards = [parse_card(cleaned[i:i + 2]) for i in range(0, len(cleaned), 2)]
    if len(set(cards)) != len(cards):
        raise ValueError(f"Carte duplicate: {text!r}")
    return cards


def card_str(card):
    return VALUE_RANK[card[0]] + card[1]


def cards_str(cards):
    return " ".join(card_str(c) for c in cards)


def remaining_deck(dead):
    dead = set(dead)
    return [c for c in FULL_DECK if c not in dead]


def hand_class(hole):
    """'AKs', 'AKo', 'TT' per due carte."""
    (r1, s1), (r2, s2) = sorted(hole, reverse=True)
    if r1 == r2:
        return VALUE_RANK[r1] * 2
    return VALUE_RANK[r1] + VALUE_RANK[r2] + ("s" if s1 == s2 else "o")

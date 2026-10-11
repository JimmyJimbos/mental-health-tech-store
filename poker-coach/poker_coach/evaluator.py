"""Valutazione del punto migliore da 5 a 7 carte.

evaluate() restituisce una tupla confrontabile: piu' alta = punto migliore.
"""

from collections import Counter

CATEGORY_NAMES = [
    "Carta alta",
    "Coppia",
    "Doppia coppia",
    "Tris",
    "Scala",
    "Colore",
    "Full",
    "Poker",
    "Scala colore",
]


def _straight_high(ranks):
    """Carta piu' alta della scala migliore, oppure None. ranks: set di valori."""
    if 14 in ranks:
        ranks = ranks | {1}
    for high in range(14, 4, -1):
        if all(r in ranks for r in range(high - 4, high + 1)):
            return high
    return None


def evaluate(cards):
    suits = Counter(s for _, s in cards)
    flush_suit = next((s for s, n in suits.items() if n >= 5), None)

    if flush_suit:
        flush_ranks = sorted((r for r, s in cards if s == flush_suit), reverse=True)
        sf = _straight_high(set(flush_ranks))
        if sf:
            return (8, sf)

    counts = Counter(r for r, _ in cards)
    # Ordina per (molteplicita', rank) decrescente
    groups = sorted(counts.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)

    if groups[0][1] == 4:
        quad = groups[0][0]
        kicker = max(r for r in counts if r != quad)
        return (7, quad, kicker)

    trips = [r for r, n in groups if n >= 3]
    pairs = [r for r, n in groups if n == 2]
    if trips and (len(trips) > 1 or pairs):
        top = trips[0]
        second = max([t for t in trips[1:]] + pairs)
        return (6, top, second)

    if flush_suit:
        return (5, *flush_ranks[:5])

    st = _straight_high(set(counts))
    if st:
        return (4, st)

    if trips:
        kickers = sorted((r for r in counts if r != trips[0]), reverse=True)[:2]
        return (3, trips[0], *kickers)

    if len(pairs) >= 2:
        p1, p2 = sorted(pairs, reverse=True)[:2]
        kicker = max(r for r in counts if r not in (p1, p2))
        return (2, p1, p2, kicker)

    if pairs:
        kickers = sorted((r for r in counts if r != pairs[0]), reverse=True)[:3]
        return (1, pairs[0], *kickers)

    return (0, *sorted(counts, reverse=True)[:5])


def describe(cards):
    return CATEGORY_NAMES[evaluate(cards)[0]]

"""Notazione dei range: 'TT+, AQs+, KQo, A5s-A2s, 76s, AK'."""

from itertools import combinations

from .cards import FULL_DECK, RANK_VALUE, RANKS


def _combos_for_class(r1, r2, kind):
    """kind: 'p' coppia, 's' suited, 'o' offsuit, '' entrambi."""
    v1, v2 = RANK_VALUE[r1], RANK_VALUE[r2]
    result = []
    for a, b in combinations(FULL_DECK, 2):
        ranks = {a[0], b[0]} if a[0] != b[0] else {a[0]}
        if v1 == v2:
            if a[0] == b[0] == v1:
                result.append((a, b))
            continue
        if ranks != {v1, v2}:
            continue
        suited = a[1] == b[1]
        if kind == "s" and not suited or kind == "o" and suited:
            continue
        result.append((a, b))
    return result


def _expand_token(token):
    token = token.strip()
    if not token:
        return []
    if "-" in token:
        start, end = (t.strip() for t in token.split("-"))
        # es. A5s-A2s oppure 99-66
        kind = start[2:] if len(start) > 2 else ""
        if start[0] == start[1]:
            hi, lo = RANK_VALUE[start[0]], RANK_VALUE[end[0]]
            lo, hi = sorted((lo, hi))
            return [RANKS[v - 2] * 2 for v in range(lo, hi + 1)]
        top = start[0]
        hi, lo = RANK_VALUE[start[1]], RANK_VALUE[end[1]]
        lo, hi = sorted((lo, hi))
        return [top + RANKS[v - 2] + kind for v in range(lo, hi + 1)]
    if token.endswith("+"):
        base = token[:-1]
        kind = base[2:] if len(base) > 2 else ""
        if base[0] == base[1]:
            return [RANKS[v - 2] * 2 for v in range(RANK_VALUE[base[0]], 15)]
        top = RANK_VALUE[base[0]]
        return [base[0] + RANKS[v - 2] + kind for v in range(RANK_VALUE[base[1]], top)]
    return [token]


def parse_range(text):
    """Restituisce la lista di combinazioni (carta, carta) del range."""
    classes = []
    for token in text.replace(" ", "").split(","):
        classes.extend(_expand_token(token))
    combos = set()
    for cls in classes:
        if len(cls) < 2 or cls[0].upper() not in RANK_VALUE or cls[1].upper() not in RANK_VALUE:
            raise ValueError(f"Mano non valida nel range: {cls!r}")
        r1, r2 = cls[0].upper(), cls[1].upper()
        kind = cls[2:].lower()
        if kind not in ("", "s", "o"):
            raise ValueError(f"Mano non valida nel range: {cls!r}")
        combos.update(_combos_for_class(r1, r2, kind))
    if not combos:
        raise ValueError("Range vuoto")
    return sorted(combos)

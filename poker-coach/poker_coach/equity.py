"""Calcolo dell'equity con simulazione Monte Carlo."""

import random
from dataclasses import dataclass

from .cards import remaining_deck
from .evaluator import CATEGORY_NAMES, evaluate


@dataclass
class EquityResult:
    equity: float  # quota del piatto attesa (pareggi divisi)
    win: float
    tie: float
    iterations: int
    hero_hand_odds: dict  # distribuzione del punto finale dell'hero


def calculate_equity(hero, board=(), opponents=1, opp_range=None, iterations=5000, rng=None):
    """hero: 2 carte; board: 0-5 carte; opp_range: lista di combo o None (mani casuali)."""
    rng = rng or random.Random()
    board = list(board)
    dead = set(hero) | set(board)
    if len(dead) != len(hero) + len(board):
        raise ValueError("Carte duplicate tra mano e board")
    if opp_range is not None:
        opp_range = [c for c in opp_range if not (set(c) & dead)]
        if not opp_range:
            raise ValueError("Il range avversario e' incompatibile con le carte note")

    deck = remaining_deck(dead)
    missing = 5 - len(board)
    share_total = wins = ties = 0.0
    done = 0
    categories = [0] * len(CATEGORY_NAMES)

    attempts = 0
    while done < iterations:
        attempts += 1
        if attempts > iterations * 50:
            break
        used = set()
        opp_hands = []
        if opp_range is not None:
            ok = True
            for _ in range(opponents):
                for _try in range(100):
                    combo = rng.choice(opp_range)
                    if not (set(combo) & used):
                        break
                else:
                    ok = False
                    break
                used.update(combo)
                opp_hands.append(list(combo))
            if not ok:
                continue
            pool = [c for c in deck if c not in used]
            runout = rng.sample(pool, missing)
        else:
            drawn = rng.sample(deck, missing + 2 * opponents)
            runout = drawn[:missing]
            opp_hands = [drawn[missing + 2 * i: missing + 2 * i + 2] for i in range(opponents)]

        full_board = board + runout
        hero_val = evaluate(hero + full_board)
        categories[hero_val[0]] += 1
        best_opp = max(evaluate(h + full_board) for h in opp_hands)
        if hero_val > best_opp:
            wins += 1
            share_total += 1
        elif hero_val == best_opp:
            n_tied = 1 + sum(1 for h in opp_hands if evaluate(h + full_board) == hero_val)
            ties += 1
            share_total += 1 / n_tied
        done += 1

    if done == 0:
        raise ValueError("Impossibile simulare con questi parametri")
    odds = {CATEGORY_NAMES[i]: n / done for i, n in enumerate(categories) if n}
    return EquityResult(share_total / done, wins / done, ties / done, done, odds)


def pot_odds(to_call, pot):
    """Equity minima per un call in pareggio: to_call / (pot + to_call)."""
    if to_call <= 0:
        return 0.0
    return to_call / (pot + to_call)

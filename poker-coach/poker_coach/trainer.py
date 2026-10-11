"""Trainer: situazioni casuali, tu decidi e stimi l'equity, poi vedi la risposta."""

import random

from .cards import FULL_DECK, cards_str
from .equity import calculate_equity, pot_odds
from .evaluator import describe

BET_SIZES = [0.33, 0.5, 0.75, 1.0]


def random_spot(rng):
    deck = FULL_DECK[:]
    rng.shuffle(deck)
    hero = deck[:2]
    board = deck[2:2 + rng.choice([3, 4, 5])]
    pot = rng.choice([4, 6, 10, 15, 20, 30])
    bet = round(pot * rng.choice(BET_SIZES), 1)
    return hero, board, pot, bet


def run(rounds=10, iterations=3000, seed=None, ask=input, say=print):
    rng = random.Random(seed)
    score = 0
    say("Trainer: l'avversario ha una mano casuale. Rispondi c (call) o f (fold).\n")
    for i in range(1, rounds + 1):
        hero, board, pot, bet = random_spot(rng)
        say(f"[{i}/{rounds}] Mano: {cards_str(hero)}   Board: {cards_str(board)}")
        say(f"        Piatto {pot} bb, l'avversario punta {bet} bb.")
        guess = ask("        La tua equity stimata (%)? ").strip().rstrip("%")
        choice = ask("        Call o fold? [c/f] ").strip().lower()[:1]

        res = calculate_equity(hero, board, iterations=iterations, rng=rng)
        need = pot_odds(bet, pot + bet)
        right = "c" if res.equity >= need else "f"
        say(f"        Hai {describe(hero + board).lower()}. Equity {res.equity:.0%}, "
            f"te ne serve {need:.0%} -> {'CALL' if right == 'c' else 'FOLD'}")
        if guess.replace(".", "", 1).isdigit():
            say(f"        La tua stima era sbagliata di {abs(float(guess) / 100 - res.equity):.0%}")
        if choice == right:
            score += 1
            say("        Corretto!\n")
        else:
            say("        Sbagliato.\n")
    say(f"Punteggio: {score}/{rounds}")
    return score

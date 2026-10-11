"""Analisi a fine sessione: statistiche e revisione delle decisioni postflop."""

import random
from collections import defaultdict
from dataclasses import dataclass

from .cards import cards_str, hand_class
from .equity import calculate_equity, pot_odds
from .evaluator import describe

STREET_IT = {"preflop": "Preflop", "flop": "Flop", "turn": "Turn", "river": "River"}
ACTION_IT = {"folds": "fold", "checks": "check", "calls": "call", "bets": "bet", "raises": "raise"}


@dataclass
class Review:
    hand_id: str
    street: str
    hero_cards: list
    board: list
    action: str
    pot: float
    to_call: float
    equity: float
    needed: float
    verdict: str


def summarize(hands):
    n = len(hands)
    if not n:
        return {}
    by_pos = defaultdict(lambda: [0, 0.0])
    by_class = defaultdict(lambda: [0, 0.0])
    for h in hands:
        by_pos[h.hero_position][0] += 1
        by_pos[h.hero_position][1] += h.hero_net
        cls = hand_class(h.hero_cards)
        by_class[cls][0] += 1
        by_class[cls][1] += h.hero_net

    net = sum(h.hero_net for h in hands)
    bbs = [h.big_blind for h in hands if h.big_blind]
    net_bb = sum(h.hero_net / h.big_blind for h in hands if h.big_blind)
    aggr = sum(h.postflop_aggr for h in hands)
    calls = sum(h.postflop_calls for h in hands)
    flops = sum(h.saw_flop for h in hands)
    return {
        "hands": n,
        "net": net,
        "bb_per_100": (net_bb / len(bbs) * 100) if bbs else None,
        "vpip": sum(h.vpip for h in hands) / n,
        "pfr": sum(h.pfr for h in hands) / n,
        "saw_flop": flops / n,
        "wtsd": (sum(h.went_to_showdown for h in hands) / flops) if flops else 0.0,
        "af": (aggr / calls) if calls else float(aggr),
        "by_position": dict(by_pos),
        "by_class": dict(by_class),
    }


def review_decisions(hands, opp_range=None, iterations=1500, margin=0.08, seed=None):
    """Confronta ogni decisione postflop con equity e pot odds.

    Senza opp_range l'avversario ha mani casuali: e' una stima ottimistica,
    perche' chi punta o rilancia di solito ha un range piu' forte.
    """
    rng = random.Random(seed)
    reviews = []
    for h in hands:
        for d in h.decisions:
            if d.street == "preflop" or d.action not in ACTION_IT:
                continue
            res = calculate_equity(h.hero_cards, d.board, opponents=d.opponents,
                                   opp_range=opp_range, iterations=iterations, rng=rng)
            eq = res.equity
            need = pot_odds(d.to_call, d.pot)
            verdict = ""
            if d.to_call > 0:
                if d.action == "folds" and eq > need + margin:
                    verdict = "Fold discutibile: l'equity superava il prezzo del call"
                elif d.action == "calls" and eq < need - margin:
                    verdict = "Call costoso: l'equity non bastava per il prezzo"
                elif d.action == "raises" and eq < need - margin and d.street == "river":
                    verdict = "Raise al river con poca equity: era un bluff voluto?"
            else:
                if d.action == "checks" and eq > 0.75 and d.street != "river":
                    verdict = "Mano forte giocata check: valuta una puntata per valore"
                elif d.action == "checks" and eq > 0.8 and d.street == "river":
                    verdict = "Check al river con mano molto forte: valore perso?"
                elif d.action == "bets" and eq < 0.25 and d.street == "river":
                    verdict = "Bluff al river: verifica che la storia fosse credibile"
            reviews.append(Review(h.hand_id, d.street, h.hero_cards, d.board, d.action,
                                  d.pot, d.to_call, eq, need, verdict))
    return reviews


def _fmt_money(x):
    return f"{x:+.2f}"


def format_report(hands, reviews, top=10):
    s = summarize(hands)
    if not s:
        return "Nessuna mano trovata. Controlla il file o il nome dell'hero (--hero)."
    out = []
    out.append("=" * 60)
    out.append(f"  REPORT SESSIONE  -  {s['hands']} mani di {hands[0].hero}")
    out.append("=" * 60)
    out.append(f"Risultato netto:   {_fmt_money(s['net'])}")
    if s["bb_per_100"] is not None:
        out.append(f"Winrate:           {s['bb_per_100']:+.1f} bb/100")
    out.append(f"VPIP / PFR:        {s['vpip']:.0%} / {s['pfr']:.0%}")
    out.append(f"Flop visti:        {s['saw_flop']:.0%}   Showdown dopo il flop: {s['wtsd']:.0%}")
    out.append(f"Aggressivita' (AF): {s['af']:.2f}")

    out.append("\nRisultato per posizione:")
    for pos, (cnt, net) in sorted(s["by_position"].items(), key=lambda kv: kv[1][1]):
        out.append(f"  {pos:<7} {cnt:>4} mani   {_fmt_money(net)}")

    worst = sorted(s["by_class"].items(), key=lambda kv: kv[1][1])[:5]
    out.append("\nMani iniziali che ti costano di piu':")
    for cls, (cnt, net) in worst:
        out.append(f"  {cls:<4} {cnt:>3} volte   {_fmt_money(net)}")

    out.append("\nConsigli generali:")
    out.extend("  - " + tip for tip in style_tips(s))

    flagged = [r for r in reviews if r.verdict]
    out.append(f"\nDecisioni postflop analizzate: {len(reviews)}   da rivedere: {len(flagged)}")
    flagged.sort(key=lambda r: abs(r.equity - r.needed) * (r.pot + r.to_call), reverse=True)
    for r in flagged[:top]:
        out.append("-" * 60)
        out.append(f"Mano #{r.hand_id}  {STREET_IT[r.street]}  [{cards_str(r.hero_cards)}]  "
                   f"board [{cards_str(r.board)}]  ({describe(r.hero_cards + r.board)})")
        price = f"call {r.to_call:.2f} su piatto {r.pot:.2f}" if r.to_call else f"piatto {r.pot:.2f}"
        out.append(f"  Hai fatto: {ACTION_IT[r.action]}   ({price})")
        out.append(f"  Equity stimata {r.equity:.0%}   equity richiesta {r.needed:.0%}")
        out.append(f"  -> {r.verdict}")

    worst_hands = sorted(hands, key=lambda h: h.hero_net)[:5]
    out.append("-" * 60)
    out.append("Le 5 mani in cui hai perso di piu' (rivedile nel replayer):")
    for h in worst_hands:
        out.append(f"  #{h.hand_id}  [{cards_str(h.hero_cards)}]  board [{cards_str(h.board)}]  "
                   f"{_fmt_money(h.hero_net)}")
    return "\n".join(out)


def style_tips(s):
    tips = []
    if s["vpip"] > 0.32:
        tips.append(f"VPIP al {s['vpip']:.0%}: giochi troppe mani. In 6-max si sta di solito tra il 20 e il 28%.")
    elif s["vpip"] < 0.15:
        tips.append(f"VPIP al {s['vpip']:.0%}: sei molto stretto, perdi occasioni da bottone e cutoff.")
    if s["vpip"] and s["pfr"] / s["vpip"] < 0.6:
        tips.append("Fai molto limp/call preflop: entra rilanciando invece di chiamare.")
    if s["af"] < 1.5:
        tips.append("Postflop chiami molto e punti poco: chi chiama troppo raramente vince.")
    if s["wtsd"] > 0.35:
        tips.append("Vai spesso allo showdown: forse paghi troppo con mani medie.")
    if not tips:
        tips.append("Statistiche equilibrate: concentrati sulle singole mani segnalate.")
    return tips

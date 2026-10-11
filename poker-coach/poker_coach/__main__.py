"""Uso:
  python -m poker_coach analizza  CARTELLA_O_FILE [--hero NOME] [--range "TT+,AQs+"]
  python -m poker_coach equity    AhKd [--board 2c7dTs] [--avversari 1] [--range ...]
  python -m poker_coach trainer   [--mani 10]
"""

import argparse
import sys
from pathlib import Path

from . import analyzer, trainer
from .cards import cards_str, parse_cards
from .equity import calculate_equity, pot_odds
from .parser import parse_file
from .ranges import parse_range


def cmd_analyze(args):
    path = Path(args.path)
    files = sorted(path.rglob("*.txt")) if path.is_dir() else [path]
    hands = []
    for f in files:
        hands.extend(parse_file(f, args.hero))
    opp_range = parse_range(args.range) if args.range else None
    print(f"Lette {len(hands)} mani da {len(files)} file. Analizzo...", file=sys.stderr)
    reviews = analyzer.review_decisions(hands, opp_range=opp_range, iterations=args.iterazioni)
    print(analyzer.format_report(hands, reviews, top=args.top))
    if not args.range:
        print("\nNota: l'equity e' calcolata contro mani casuali e quindi e' ottimistica. "
              "Per un'analisi piu' realistica usa --range (es. --range \"88+,ATs+,KQs,AJo+\").")


def cmd_equity(args):
    hero = parse_cards(args.mano)
    board = parse_cards(args.board) if args.board else []
    if len(hero) != 2 or len(board) > 5:
        sys.exit("Servono 2 carte in mano e al massimo 5 sul board.")
    opp_range = parse_range(args.range) if args.range else None
    res = calculate_equity(hero, board, opponents=args.avversari,
                           opp_range=opp_range, iterations=args.iterazioni)
    print(f"Mano [{cards_str(hero)}]  board [{cards_str(board)}]  vs {args.avversari} avversari "
          f"({'range ' + args.range if args.range else 'mani casuali'})")
    print(f"Equity: {res.equity:.1%}   (vinci {res.win:.1%}, pareggi {res.tie:.1%})")
    print("Punto finale dell'hero:")
    for name, p in sorted(res.hero_hand_odds.items(), key=lambda kv: -kv[1]):
        print(f"  {name:<14} {p:6.1%}")
    if args.piatto is not None and args.puntata is not None:
        need = pot_odds(args.puntata, args.piatto + args.puntata)
        verdict = "il call e' profittevole" if res.equity >= need else "il call non e' profittevole"
        print(f"Pot odds: ti serve il {need:.1%} di equity -> {verdict} (solo matematica, senza implied odds)")


def main(argv=None):
    p = argparse.ArgumentParser(prog="poker_coach", description="Studio del poker fuori dal tavolo.")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("analizza", help="Report da hand history di PokerStars")
    a.add_argument("path", help="File .txt o cartella con le hand history")
    a.add_argument("--hero", help="Il tuo nickname (default: chi riceve le carte)")
    a.add_argument("--range", help="Range ipotetico degli avversari")
    a.add_argument("--top", type=int, default=10, help="Quante decisioni mostrare")
    a.add_argument("--iterazioni", type=int, default=1500)
    a.set_defaults(func=cmd_analyze)

    e = sub.add_parser("equity", help="Calcolatore di equity per studiare una situazione")
    e.add_argument("mano", help="Es. AhKd")
    e.add_argument("--board", help="Es. 2c7dTs")
    e.add_argument("--avversari", type=int, default=1)
    e.add_argument("--range", help="Es. \"TT+,AQs+,AKo\"")
    e.add_argument("--piatto", type=float, help="Piatto prima della puntata avversaria")
    e.add_argument("--puntata", type=float, help="Puntata da chiamare")
    e.add_argument("--iterazioni", type=int, default=20000)
    e.set_defaults(func=cmd_equity)

    t = sub.add_parser("trainer", help="Quiz su situazioni casuali")
    t.add_argument("--mani", type=int, default=10)
    t.set_defaults(func=lambda args: trainer.run(rounds=args.mani))

    args = p.parse_args(argv)
    try:
        args.func(args)
    except ValueError as exc:
        sys.exit(f"Errore: {exc}")


if __name__ == "__main__":
    main()

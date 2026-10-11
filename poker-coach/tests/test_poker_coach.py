import random
import unittest
from pathlib import Path

from poker_coach.cards import parse_cards
from poker_coach.equity import calculate_equity, pot_odds
from poker_coach.evaluator import evaluate
from poker_coach.parser import parse_file, position_of
from poker_coach.ranges import parse_range
from poker_coach import trainer

SAMPLE = Path(__file__).parent.parent / "samples" / "esempio.txt"


def ev(text):
    return evaluate(parse_cards(text))


class EvaluatorTest(unittest.TestCase):
    def test_categories(self):
        self.assertEqual(ev("AhKhQhJhTh2c3d")[0], 8)
        self.assertEqual(ev("9c9d9h9s2c3d4h")[0], 7)
        self.assertEqual(ev("9c9d9hKsKc3d4h")[0], 6)
        self.assertEqual(ev("2h5h9hJhKh3d4c")[0], 5)
        self.assertEqual(ev("Ah2c3d4s5h9cKd")[0], 4)  # scala alla 5
        self.assertEqual(ev("7c7d7hAsKc3d2h")[0], 3)
        self.assertEqual(ev("7c7dKhKsAc3d2h")[0], 2)
        self.assertEqual(ev("7c7dJhKsAc3d2h")[0], 1)
        self.assertEqual(ev("7c9dJhKsAc3d2h")[0], 0)

    def test_comparisons(self):
        self.assertGreater(ev("AhAdKc7s2d"), ev("AhAdQc7s2d"))       # kicker
        self.assertGreater(ev("6h2c3d4s5h"), ev("Ah2c3d4s5c"))       # scala al 6 > alla 5
        self.assertGreater(ev("9c9d9hKsKc"), ev("8c8d8hAsAc"))
        self.assertEqual(ev("AhKdQc7s2d"), ev("AsKcQd7h2c"))
        self.assertGreater(ev("9c9d9h8s8c8d2h"), ev("9c9d9h7s7c2d3h"))  # due tris


class RangeTest(unittest.TestCase):
    def test_counts(self):
        self.assertEqual(len(parse_range("AA")), 6)
        self.assertEqual(len(parse_range("AKs")), 4)
        self.assertEqual(len(parse_range("AKo")), 12)
        self.assertEqual(len(parse_range("AK")), 16)
        self.assertEqual(len(parse_range("TT+")), 30)
        self.assertEqual(len(parse_range("ATs+")), 16)
        self.assertEqual(len(parse_range("A5s-A2s")), 16)
        self.assertEqual(len(parse_range("99-66")), 24)

    def test_invalid(self):
        with self.assertRaises(ValueError):
            parse_range("ZZ")


class EquityTest(unittest.TestCase):
    def test_aa_vs_kk(self):
        res = calculate_equity(parse_cards("AhAd"), opp_range=parse_range("KK"),
                               iterations=4000, rng=random.Random(1))
        self.assertAlmostEqual(res.equity, 0.82, delta=0.03)

    def test_made_nuts_on_river(self):
        res = calculate_equity(parse_cards("AhKh"), parse_cards("QhJhTh2c3d"), iterations=200)
        self.assertEqual(res.equity, 1.0)

    def test_pot_odds(self):
        self.assertAlmostEqual(pot_odds(50, 150), 0.25)
        self.assertEqual(pot_odds(0, 100), 0.0)


class ParserTest(unittest.TestCase):
    def setUp(self):
        self.hands = parse_file(SAMPLE)

    def test_hands_and_results(self):
        self.assertEqual(len(self.hands), 3)
        nets = [round(h.hero_net, 2) for h in self.hands]
        self.assertEqual(nets, [-1.80, -0.85, 0.72])
        self.assertEqual(self.hands[0].big_blind, 0.05)

    def test_positions(self):
        self.assertEqual([h.hero_position for h in self.hands], ["BB", "SB", "BTN"])
        self.assertEqual(position_of(4, 1, [1, 2, 3, 4, 5, 6]), "UTG")
        self.assertEqual(position_of(2, 1, [1, 2]), "BB")

    def test_river_decision(self):
        river_fold = self.hands[0].decisions[-1]
        self.assertEqual(river_fold.action, "folds")
        self.assertAlmostEqual(river_fold.pot, 5.12)
        self.assertAlmostEqual(river_fold.to_call, 1.50)
        self.assertEqual(len(river_fold.board), 5)

    def test_stats_flags(self):
        h = self.hands[2]
        self.assertTrue(h.vpip and h.pfr and h.saw_flop)
        self.assertEqual(h.postflop_aggr, 2)
        self.assertTrue(self.hands[1].went_to_showdown)


class TrainerTest(unittest.TestCase):
    def test_runs_scripted(self):
        answers = iter(["50", "c"] * 3)
        out = []
        score = trainer.run(rounds=3, iterations=300, seed=7,
                            ask=lambda _: next(answers), say=out.append)
        self.assertIn(score, range(4))
        self.assertTrue(out[-1].startswith("Punteggio"))


if __name__ == "__main__":
    unittest.main()

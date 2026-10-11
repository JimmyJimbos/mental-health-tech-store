"""Parser delle hand history di PokerStars (Hold'em, cash e torneo).

Si usa sui file .txt che il client salva a fine mano, non durante il gioco.
"""

import re
from dataclasses import dataclass, field

from .cards import parse_cards

NUM = r"[$€£]?([\d,]+(?:\.\d+)?)"

RE_HEADER = re.compile(r"^PokerStars (?:Zoom |Home Game )?Hand #(\d+)")
RE_BLINDS = re.compile(r"\(" + NUM + r"/" + NUM)
RE_LEVEL_BLINDS = re.compile(r"Level [IVXLC\d]+ \((\d[\d,]*)/(\d[\d,]*)\)")
RE_BUTTON = re.compile(r"Seat #(\d+) is the button")
RE_SEAT = re.compile(r"^Seat (\d+): (.+?) \(" + NUM + r" in chips")
RE_DEALT = re.compile(r"^Dealt to (.+?) \[(.+?)\]")
RE_STREET = re.compile(r"^\*\*\* (FLOP|TURN|RIVER) \*\*\* (.*)$")
RE_ACTION = re.compile(r"^(.+?): (folds|checks|calls|bets|raises|posts)(.*)$")
RE_COLLECTED = re.compile(r"^(.+?) collected " + NUM)
RE_UNCALLED = re.compile(r"^Uncalled bet \(" + NUM + r"\) returned to (.+)$")
RE_SHOWS = re.compile(r"^(.+?): shows \[(.+?)\]")

STREETS = ["preflop", "flop", "turn", "river"]


def _num(text):
    return float(text.replace(",", ""))


def _amounts(text):
    return [_num(m) for m in re.findall(r"[$€£]?(\d[\d,]*(?:\.\d+)?)", text)]


@dataclass
class Decision:
    """Una decisione dell'hero: cosa sapeva in quel momento e cosa ha fatto."""
    street: str
    board: list
    pot: float          # piatto prima dell'azione dell'hero
    to_call: float      # quanto doveva mettere per vedere
    action: str         # folds/checks/calls/bets/raises
    amount: float       # quanto ha aggiunto con questa azione
    opponents: int      # avversari ancora in mano


@dataclass
class Hand:
    hand_id: str
    big_blind: float = 0.0
    button_seat: int = 0
    seats: dict = field(default_factory=dict)       # seat -> nome
    hero: str = ""
    hero_cards: list = field(default_factory=list)
    board: list = field(default_factory=list)
    decisions: list = field(default_factory=list)
    invested: dict = field(default_factory=dict)    # giocatore -> totale messo nel piatto
    collected: dict = field(default_factory=dict)
    shown: dict = field(default_factory=dict)
    vpip: bool = False
    pfr: bool = False
    saw_flop: bool = False
    went_to_showdown: bool = False
    postflop_aggr: int = 0
    postflop_calls: int = 0

    @property
    def hero_net(self):
        return self.collected.get(self.hero, 0.0) - self.invested.get(self.hero, 0.0)

    @property
    def hero_position(self):
        return position_of(self.hero_seat, self.button_seat, sorted(self.seats))

    @property
    def hero_seat(self):
        return next((s for s, n in self.seats.items() if n == self.hero), None)


def position_of(seat, button, seats):
    if seat is None or button not in seats:
        return "?"
    n = len(seats)
    i = seats.index(button)
    order = seats[i:] + seats[:i]  # bottone, SB, BB, ...
    idx = order.index(seat)
    if n == 2:
        return "BTN/SB" if idx == 0 else "BB"
    if idx == 0:
        return "BTN"
    if idx == 1:
        return "SB"
    if idx == 2:
        return "BB"
    k = n - 3
    names = {1: ["CO"], 2: ["HJ", "CO"], 3: ["UTG", "HJ", "CO"]}.get(k)
    if names is None:
        names = ["UTG"] + [f"UTG+{j}" for j in range(1, k - 3)] + ["MP", "HJ", "CO"]
    return names[idx - 3]


def split_hands(text):
    chunks, current = [], []
    for line in text.splitlines():
        line = line.lstrip("﻿").rstrip()
        if RE_HEADER.match(line) and current:
            chunks.append(current)
            current = []
        if line or current:
            current.append(line)
    if current:
        chunks.append(current)
    return [c for c in chunks if c and RE_HEADER.match(c[0])]


def parse_hand(lines, hero_name=None):
    m = RE_HEADER.match(lines[0])
    hand = Hand(hand_id=m.group(1))
    bl = RE_LEVEL_BLINDS.search(lines[0]) or RE_BLINDS.search(lines[0])
    if bl:
        hand.big_blind = _num(bl.group(2))

    street = "preflop"
    pot = 0.0
    street_contrib = {}
    current_bet = 0.0
    active = set()
    in_summary = False

    def put(player, amount):
        nonlocal pot
        pot += amount
        hand.invested[player] = hand.invested.get(player, 0.0) + amount

    for line in lines[1:]:
        if line.startswith("*** SUMMARY"):
            in_summary = True
            continue
        if in_summary:
            continue
        if line.startswith("*** SHOW DOWN"):
            if hand.hero in active:
                hand.went_to_showdown = True
            continue

        if mb := RE_BUTTON.search(line):
            hand.button_seat = int(mb.group(1))
            continue
        if ms := RE_SEAT.match(line):
            if "sitting out" not in line:
                hand.seats[int(ms.group(1))] = ms.group(2)
                active.add(ms.group(2))
            continue
        if md := RE_DEALT.match(line):
            if hero_name is None or md.group(1) == hero_name:
                hand.hero = md.group(1)
                hand.hero_cards = parse_cards(md.group(2))
            continue
        if mst := RE_STREET.match(line):
            street = mst.group(1).lower()
            # La riga del turn e' "[Ah Kd 2c] [7s]": l'ultima parentesi e' la carta nuova
            groups = re.findall(r"\[(.+?)\]", mst.group(2))
            hand.board += parse_cards(groups[-1])
            street_contrib, current_bet = {}, 0.0
            if street == "flop" and hand.hero in active:
                hand.saw_flop = True
            continue
        if mu := RE_UNCALLED.match(line):
            amount, player = _num(mu.group(1)), mu.group(2).strip()
            hand.invested[player] = hand.invested.get(player, 0.0) - amount
            pot -= amount
            continue
        if mc := RE_COLLECTED.match(line):
            player = mc.group(1).strip()
            hand.collected[player] = hand.collected.get(player, 0.0) + _num(mc.group(2))
            continue
        if msh := RE_SHOWS.match(line):
            try:
                hand.shown[msh.group(1)] = parse_cards(msh.group(2))
            except ValueError:
                pass
            continue

        ma = RE_ACTION.match(line)
        if not ma:
            continue
        player, verb, rest = ma.group(1), ma.group(2), ma.group(3)
        nums = _amounts(rest)
        already = street_contrib.get(player, 0.0)

        if verb == "posts":
            amount = nums[-1] if nums else 0.0
            if "ante" in rest:
                put(player, amount)  # l'ante e' morto, non conta come puntata del giro
                continue
            street_contrib[player] = already + amount
            current_bet = max(current_bet, street_contrib[player])
            put(player, amount)
            continue

        is_hero = player == hand.hero
        to_call = max(0.0, current_bet - already)
        pot_before = pot

        if verb == "folds":
            added = 0.0
            active.discard(player)
        elif verb == "checks":
            added = 0.0
        elif verb == "calls":
            added = nums[0] if nums else to_call
        elif verb == "bets":
            added = nums[0] if nums else 0.0
            current_bet = already + added
        else:  # raises X to Y
            target = nums[-1] if nums else current_bet
            added = target - already
            current_bet = target

        if added:
            street_contrib[player] = already + added
            put(player, added)

        if is_hero:
            hand.decisions.append(Decision(
                street=street,
                board=list(hand.board),
                pot=pot_before,
                to_call=to_call,
                action=verb,
                amount=added,
                opponents=max(1, len(active - {player})),
            ))
            if street == "preflop":
                if verb in ("calls", "raises", "bets"):
                    hand.vpip = True
                if verb == "raises":
                    hand.pfr = True
            else:
                if verb in ("bets", "raises"):
                    hand.postflop_aggr += 1
                elif verb == "calls":
                    hand.postflop_calls += 1

    return hand


def parse_file(path, hero_name=None):
    with open(path, encoding="utf-8-sig", errors="replace") as f:
        text = f.read()
    return parse_text(text, hero_name)


def parse_text(text, hero_name=None):
    hands = []
    for chunk in split_hands(text):
        try:
            hand = parse_hand(chunk, hero_name)
        except (ValueError, IndexError):
            continue  # mano in un formato non supportato: la saltiamo
        if hand.hero and len(hand.hero_cards) == 2:
            hands.append(hand)
    return hands

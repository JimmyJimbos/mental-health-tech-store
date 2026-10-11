# Poker Coach

Strumenti per studiare il proprio gioco di Texas Hold'em **fuori dal tavolo**:

- **analizza**: legge le hand history di PokerStars a fine sessione e prepara un report con statistiche, risultato per posizione, mani iniziali in perdita e le decisioni postflop da rivedere (equity contro pot odds).
- **equity**: calcolatore di equity per studiare una situazione (mano, board, numero di avversari, range).
- **trainer**: quiz su situazioni casuali per allenare la stima dell'equity e le decisioni call/fold.

Non legge lo schermo e non si collega al client: lavora solo su file e input scritti da te. Non usarlo durante le partite. L'assistenza in tempo reale è vietata dai termini di PokerStars.

Serve solo Python 3.9 o superiore, senza librerie esterne.

## Come ottenere le hand history

1. Nel client PokerStars apri *Impostazioni → Cronologia mani* (Hand History) e attiva il salvataggio su disco.
2. Imposta la **lingua delle hand history su inglese**: il parser riconosce solo il formato inglese.
3. I file `.txt` vengono salvati nella cartella indicata nelle impostazioni (su Windows di solito `C:\Users\<nome>\AppData\Local\PokerStars.IT\HandHistory\<nickname>`).

## Uso

Dalla cartella `poker-coach`:

```bash
# Report di una sessione (file singolo o intera cartella)
python -m poker_coach analizza "C:\percorso\HandHistory\MioNick" --hero MioNick

# Analisi più realistica: ipotizza il range con cui gli avversari continuano
python -m poker_coach analizza samples/esempio.txt --range "88+,ATs+,KQs,AJo+"

# Studio di uno spot: AhKh su Qh7h2c contro un range, con pot odds
python -m poker_coach equity AhKh --board Qh7h2c --range "TT+,AQs+,AKo" --piatto 10 --puntata 7

# Quiz
python -m poker_coach trainer --mani 15
```

Notazione dei range: `TT+` (coppie da TT in su), `ATs+` (AT-AK suited), `A5s-A2s`, `99-66`, `KQo`, `AK` (suited e offsuit).

## Come leggere il report

- **VPIP/PFR**: percentuale di mani in cui metti soldi volontariamente o rilanci preflop.
- **AF**: puntate+rilanci diviso call, postflop.
- **Decisioni da rivedere**: confronta l'equity stimata in quel momento con quella richiesta dal prezzo del call (`call / (piatto + call)`). Senza `--range` gli avversari hanno mani casuali, quindi l'equity è ottimistica: chi punta forte al river raramente ha una mano a caso. Usa le segnalazioni come spunto per rivedere la mano, non come verità.

## Test

```bash
python -m unittest discover -s tests
```

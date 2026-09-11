# Flip Assistant

Strumento personale per il flipping su eBay e Vinted, con due strategie coperte:

- **Nerd/gaming**: videogiochi & console retro, carte collezionabili (Pokémon/Magic/Yu-Gi-Oh),
  Funko Pop & action figure, fumetti & manga, giochi da tavolo fuori produzione, controller con
  drift da riparare e rivendere.
- **Export vintage italiano** (arbitraggio geografico): macchine da scrivere & design industriale
  italiano, vetro di Murano & design/ceramica di metà '900, abbigliamento sportivo/streetwear
  vintage italiano — categorie dove l'Italia sottovaluta oggetti che all'estero (soprattutto USA)
  hanno un mercato collezionistico consolidato.

Non è un prodotto da vendere ad altri: è un tool ad uso personale per chi compra su
marketplace (Vinted/Subito/mercatini) per rivendere su eBay a un pubblico più ampio, anche estero.

## Cosa fa (ed è tutto reale, testato)

1. **`/comps`** — genera link di ricerca già filtrati (venduti eBay, annunci Vinted, annunci
   Subito) per un oggetto. Per il lato vendita, confronta lo **stesso oggetto su 4 eBay diversi in
   parallelo** (Italia, USA, Germania, Regno Unito): è così che si vede a colpo d'occhio se un
   oggetto vale multipli all'estero rispetto al prezzo domestico. Nessuno scraping: apri tu il
   link e guardi i prezzi reali sul sito ufficiale, così resti nei termini di servizio di
   eBay/Vinted invece di rischiare il ban dell'account con l'estrazione automatica dei dati.
2. **`/margin`** — calcola il profitto netto dato prezzo d'acquisto, prezzo di vendita atteso,
   spedizione e fee di piattaforma. Modella correttamente la differenza tra eBay (commissione +
   fee fissa trattenute dal venditore) e Vinted (il venditore incassa il prezzo pieno, è il
   compratore a pagare la fee di protezione a parte). Per le vendite su eBay estero, ricorda di
   mettere in conto spedizione internazionale più cara e imballo più robusto per oggetti fragili.
3. **`/listing`** — genera titolo e descrizione per l'annuncio. Usa l'API di Anthropic se
   `ANTHROPIC_API_KEY` è configurata, altrimenti un template locale (sempre funzionante, solo
   più semplice).
4. **`/inventory`** — magazzino personale (localStorage, nessun account/server) per tracciare
   acquisti, vendite e il profitto del mese rispetto a un obiettivo che imposti tu.

## Cosa NON fa (di proposito)

- Non fa scraping di eBay/Vinted/Subito: violerebbe i loro termini di servizio e rischierebbe il
  blocco dell'account. Le stime di prezzo/fee sono un punto di partenza da verificare a mano.
- Non garantisce alcun guadagno: è un aiuto per decidere più in fretta e con meno errori,
  l'attività di compravendita resta un vero lavoro (tempo per cercare, fotografare, spedire) con
  capitale reale a rischio (quello che spendi per comprare la merce).
- Le percentuali di fee eBay in `data/categories.ts` sono stime approssimative: **verifica sempre
  le tariffe correnti sulla pagina ufficiale eBay** prima di fare i conti definitivi — cambiano nel
  tempo e variano per categoria/venditore.

## Sviluppo locale

```bash
npm install
npm run dev     # http://localhost:3100
npm run build
```

Il magazzino vive solo nel browser in cui lo usi (localStorage): se vuoi accedervi da più
dispositivi, andrebbe aggiunta una persistenza server-side — non implementata qui perché per un
uso personale in singolo browser è complessità non necessaria.

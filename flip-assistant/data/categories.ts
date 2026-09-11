export type Category = {
  slug: string;
  name: string;
  /** Rough eBay Italy final-value-fee estimate for this category, as a starting point — always editable in the calculator. */
  defaultEbayFeePct: number;
  /** Extra keywords appended to "sell" comps searches (assumes working condition) to sharpen results. */
  searchHint: string;
  /** For repair-flip categories: keywords that surface cheap broken/faulty stock to buy instead of comps. */
  buyHint?: string;
  tip: string;
};

export const CATEGORIES: Category[] = [
  {
    slug: 'retro-games',
    name: 'Videogiochi & console retro',
    defaultEbayFeePct: 12.35,
    searchHint: 'PAL completo',
    tip: 'Controlla se è PAL, se è completo in scatola (CIB) e se la console si accende davvero prima di comprare: sono i tre fattori che spostano di più il prezzo.',
  },
  {
    slug: 'trading-cards',
    name: 'Carte collezionabili (Pokémon, Magic, Yu-Gi-Oh)',
    defaultEbayFeePct: 13.25,
    searchHint: 'NM',
    tip: "Lo stato di conservazione (NM/LP/MP) e l'edizione (prima stampa vs ristampa) cambiano il valore anche di 5-10x sulla stessa carta.",
  },
  {
    slug: 'funko-figures',
    name: 'Funko Pop & action figure',
    defaultEbayFeePct: 13.25,
    searchHint: 'box condition',
    tip: 'I pezzi "chase", le esclusive convention e le scatole intonse valgono molto di più — controlla sempre il numero stampato sulla confezione.',
  },
  {
    slug: 'comics-manga',
    name: 'Fumetti & manga',
    defaultEbayFeePct: 13.25,
    searchHint: 'prima edizione',
    tip: 'Prime edizioni, variant cover e albi fuori catalogo valgono molto di più di una ristampa recente — verifica sempre edizione e anno.',
  },
  {
    slug: 'board-games',
    name: 'Giochi da tavolo fuori produzione',
    defaultEbayFeePct: 12.35,
    searchHint: 'completo',
    tip: 'Verifica che tutti i componenti (miniature, carte, dadi, regolamento) siano presenti: un pezzo mancante può dimezzare il valore di rivendita.',
  },
  {
    slug: 'controller-repair',
    name: 'Controller & accessori (drift/riparazione)',
    defaultEbayFeePct: 13.25,
    searchHint: 'funzionante',
    buyHint: 'drift rotto',
    tip: 'Il drift è il guasto più diffuso su Joy-Con e DualSense: chi vende "rotto" spesso non sa che basta sostituire lo stick. Un upgrade a sensore Hall Effect/TMR (niente più drift) giustifica un prezzo di rivendita più alto di un semplice usato funzionante.',
  },
];

export function getCategory(slug: string): Category | undefined {
  return CATEGORIES.find((c) => c.slug === slug);
}

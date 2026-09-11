export type EbaySite = {
  code: string;
  domain: string;
  label: string;
  currencyNote: string;
};

/**
 * eBay markets worth checking for cross-border arbitrage: Italian goods with design/collector
 * cachet abroad often sell for multiples of the domestic price on these sites.
 */
export const EBAY_SITES: EbaySite[] = [
  { code: 'it', domain: 'www.ebay.it', label: 'Italia', currencyNote: '€' },
  { code: 'com', domain: 'www.ebay.com', label: 'USA', currencyNote: '$' },
  { code: 'de', domain: 'www.ebay.de', label: 'Germania', currencyNote: '€' },
  { code: 'co.uk', domain: 'www.ebay.co.uk', label: 'Regno Unito', currencyNote: '£' },
];

export function ebaySoldSearchUrl(query: string, searchHint: string, domain = 'www.ebay.it'): string {
  const q = [query, searchHint].filter(Boolean).join(' ');
  const params = new URLSearchParams({
    _nkw: q,
    LH_Sold: '1',
    LH_Complete: '1',
    _sop: '13', // sort: recently ended first
  });
  return `https://${domain}/sch/i.html?${params.toString()}`;
}

export function vintedSearchUrl(query: string): string {
  const params = new URLSearchParams({ search_text: query, order: 'price_low_to_high' });
  return `https://www.vinted.it/catalog?${params.toString()}`;
}

export function subitoSearchUrl(query: string): string {
  const params = new URLSearchParams({ q: query });
  return `https://www.subito.it/annunci-italia/vendita/usato/?${params.toString()}`;
}

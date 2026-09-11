export function ebaySoldSearchUrl(query: string, searchHint: string): string {
  const q = [query, searchHint].filter(Boolean).join(' ');
  const params = new URLSearchParams({
    _nkw: q,
    LH_Sold: '1',
    LH_Complete: '1',
    _sop: '13', // sort: recently ended first
  });
  return `https://www.ebay.it/sch/i.html?${params.toString()}`;
}

export function vintedSearchUrl(query: string): string {
  const params = new URLSearchParams({ search_text: query, order: 'price_low_to_high' });
  return `https://www.vinted.it/catalog?${params.toString()}`;
}

export function subitoSearchUrl(query: string): string {
  const params = new URLSearchParams({ q: query });
  return `https://www.subito.it/annunci-italia/vendita/usato/?${params.toString()}`;
}

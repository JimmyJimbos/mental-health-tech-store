export type ListingRequest = {
  itemName: string;
  category: string;
  condition: string;
  details: string;
};

export type ListingCopy = {
  title: string;
  description: string;
  source: 'live' | 'fallback';
};

function fallbackListing({ itemName, category, condition, details }: ListingRequest): ListingCopy {
  const title = `${itemName} - ${condition} - ${category}`.slice(0, 80);
  const description = [
    `${itemName}`,
    '',
    `Categoria: ${category}`,
    `Condizioni: ${condition}`,
    details ? `Dettagli: ${details}` : '',
    '',
    'Spedizione tracciata, imballo con cura. Scrivimi per altre foto o domande prima di acquistare.',
  ]
    .filter(Boolean)
    .join('\n');

  return { title, description, source: 'fallback' };
}

export async function generateListingCopy(req: ListingRequest): Promise<ListingCopy> {
  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) return fallbackListing(req);

  try {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify({
        model: 'claude-haiku-4-5-20251001',
        max_tokens: 400,
        system:
          'Sei un copywriter esperto di annunci per eBay e Vinted nella nicchia collezionismo/retrogaming. ' +
          'Scrivi in italiano. Rispondi SOLO con un oggetto JSON valido, senza markdown, con due campi: ' +
          '"title" (max 80 caratteri, con le parole chiave più cercate all\'inizio) e "description" ' +
          '(150-250 parole, onesta sulle condizioni, che invoglia all\'acquisto senza esagerare).',
        messages: [
          {
            role: 'user',
            content: `Oggetto: ${req.itemName}\nCategoria: ${req.category}\nCondizioni: ${req.condition}\nDettagli aggiuntivi: ${req.details || 'nessuno'}`,
          },
        ],
      }),
    });

    if (!response.ok) return fallbackListing(req);

    const data = await response.json();
    const text = data?.content?.[0]?.text;
    if (typeof text !== 'string') return fallbackListing(req);

    const parsed = JSON.parse(text);
    if (typeof parsed.title !== 'string' || typeof parsed.description !== 'string') {
      return fallbackListing(req);
    }

    return { title: parsed.title, description: parsed.description, source: 'live' };
  } catch {
    return fallbackListing(req);
  }
}

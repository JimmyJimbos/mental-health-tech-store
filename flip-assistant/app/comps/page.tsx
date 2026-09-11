'use client';

import { useState } from 'react';
import { CATEGORIES } from '@/data/categories';
import { ebaySoldSearchUrl, vintedSearchUrl, subitoSearchUrl } from '@/lib/comps';

export default function CompsPage() {
  const [query, setQuery] = useState('');
  const [categorySlug, setCategorySlug] = useState(CATEGORIES[0].slug);

  const category = CATEGORIES.find((c) => c.slug === categorySlug) ?? CATEGORIES[0];
  const canSearch = query.trim().length > 0;

  return (
    <div className="mx-auto max-w-2xl px-6 py-16">
      <h1 className="text-3xl font-bold text-ink-900">Controlla il prezzo di mercato</h1>
      <p className="mt-2 text-ink-600">
        Prima di comprare un annuncio, verifica sempre a quanto si è venduto davvero un oggetto
        simile. Questi link aprono la ricerca già filtrata — nessun dato viene scaricato o
        salvato qui, guardi direttamente sul sito.
      </p>

      <div className="mt-8 space-y-4">
        <div>
          <label className="block text-sm font-medium text-ink-700">Cosa vuoi cercare</label>
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder='Es. "Pokemon Platino Nintendo DS"'
            className="mt-1 w-full rounded-lg border border-amber-300 p-3 focus:border-amber-500 focus:outline-none"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-ink-700">Categoria</label>
          <select
            value={categorySlug}
            onChange={(e) => setCategorySlug(e.target.value)}
            className="mt-1 w-full rounded-lg border border-amber-300 p-3 focus:border-amber-500 focus:outline-none"
          >
            {CATEGORIES.map((c) => (
              <option key={c.slug} value={c.slug}>
                {c.name}
              </option>
            ))}
          </select>
          <p className="mt-1 text-xs text-ink-400">{category.tip}</p>
        </div>
      </div>

      {canSearch && (
        <div className="mt-8 space-y-3">
          <ResultLink
            href={ebaySoldSearchUrl(query, category.searchHint)}
            label="eBay — venduti/completati (prezzo di mercato reale)"
            highlight
          />
          <ResultLink href={vintedSearchUrl(query)} label="Vinted — annunci attivi (per trovare occasioni da comprare)" />
          <ResultLink href={subitoSearchUrl(query)} label="Subito.it — annunci attivi (mercato locale)" />
        </div>
      )}

      <p className="mt-10 text-xs text-ink-400">
        Nota: la ricerca "venduti" di eBay mostra uno storico più ampio se sei loggato al sito.
        Confronta sempre più risultati recenti, non un singolo annuncio: un solo prezzo alto o
        basso non è rappresentativo.
      </p>
    </div>
  );
}

function ResultLink({ href, label, highlight }: { href: string; label: string; highlight?: boolean }) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className={`block rounded-lg border p-4 text-sm font-medium transition hover:shadow-md ${
        highlight
          ? 'border-amber-500 bg-amber-50 text-amber-900'
          : 'border-amber-200 bg-white text-ink-700'
      }`}
    >
      {label} ↗
    </a>
  );
}

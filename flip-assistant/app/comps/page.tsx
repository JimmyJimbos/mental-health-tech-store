'use client';

import { useState } from 'react';
import { CATEGORIES } from '@/data/categories';
import { ebaySoldSearchUrl, vintedSearchUrl, subitoSearchUrl, EBAY_SITES } from '@/lib/comps';

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
        <div className="mt-8 space-y-6">
          <div>
            <h2 className="text-sm font-semibold uppercase tracking-wide text-ink-400">
              Prezzo di mercato per paese (venduto) — cerca lo scarto
            </h2>
            <p className="mt-1 text-xs text-ink-400">
              Confronta gli stessi risultati su più eBay: se un oggetto vende molto di più
              all&apos;estero che in Italia, è lì che sta il margine.
            </p>
            <div className="mt-2 grid gap-3 sm:grid-cols-2">
              {EBAY_SITES.map((site) => (
                <ResultLink
                  key={site.code}
                  href={ebaySoldSearchUrl(query, category.searchHint, site.domain)}
                  label={`eBay ${site.label} (${site.currencyNote}) — venduti`}
                  highlight={site.code === 'it'}
                />
              ))}
            </div>
          </div>

          <div>
            <h2 className="text-sm font-semibold uppercase tracking-wide text-ink-400">
              Annunci attivi (per confrontare la concorrenza)
            </h2>
            <div className="mt-2 space-y-3">
              <ResultLink href={vintedSearchUrl(query)} label="Vinted — annunci attivi" />
              <ResultLink href={subitoSearchUrl(query)} label="Subito.it — annunci attivi (mercato locale)" />
            </div>
          </div>

          {category.buyHint && (
            <div>
              <h2 className="text-sm font-semibold uppercase tracking-wide text-amber-700">
                Occasioni da riparare (rotto/drift, di solito svenduto)
              </h2>
              <div className="mt-2 space-y-3">
                <ResultLink
                  href={vintedSearchUrl(`${query} ${category.buyHint}`)}
                  label={`Vinted — cerca "${category.buyHint}"`}
                />
                <ResultLink
                  href={subitoSearchUrl(`${query} ${category.buyHint}`)}
                  label={`Subito.it — cerca "${category.buyHint}"`}
                />
              </div>
            </div>
          )}
        </div>
      )}

      <div className="mt-10 rounded-xl border border-amber-200 bg-white p-4 text-xs text-ink-500">
        <p className="font-semibold text-ink-700">Se i risultati sono troppo larghi o troppo stretti:</p>
        <ul className="mt-2 list-disc space-y-1 pl-4">
          <li>
            Usa le virgolette per una frase esatta, es. <code>&quot;Nintendo 64&quot; console</code> invece di
            lasciare che eBay interpreti le parole separatamente.
          </li>
          <li>
            Escludi parole con il segno meno, es. <code>Nintendo 64 console -gioco -Mario -Kart</code> per
            togliere di mezzo le cartucce quando cerchi la console da sola.
          </li>
          <li>
            La ricerca &quot;venduti&quot; di eBay mostra uno storico più ampio se sei loggato al sito.
            Confronta sempre più risultati recenti, non un singolo annuncio.
          </li>
        </ul>
      </div>
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

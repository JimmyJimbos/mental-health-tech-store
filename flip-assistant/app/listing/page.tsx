'use client';

import { FormEvent, useState } from 'react';
import { CATEGORIES } from '@/data/categories';

const CONDITIONS = ['Nuovo/sigillato', 'Come nuovo', 'Buono', 'Usato con segni', 'Da riparare'];

type Copy = { title: string; description: string; source: 'live' | 'fallback' };

export default function ListingPage() {
  const [itemName, setItemName] = useState('');
  const [categorySlug, setCategorySlug] = useState(CATEGORIES[0].slug);
  const [condition, setCondition] = useState(CONDITIONS[1]);
  const [details, setDetails] = useState('');
  const [copy, setCopy] = useState<Copy | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!itemName.trim() || loading) return;

    setLoading(true);
    setError(null);
    setCopy(null);

    const category = CATEGORIES.find((c) => c.slug === categorySlug)?.name ?? categorySlug;

    try {
      const res = await fetch('/api/listing', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ itemName, category, condition, details }),
      });
      const data = await res.json();

      if (!res.ok) {
        setError(data.error ?? 'Qualcosa è andato storto.');
        return;
      }

      setCopy(data);
    } catch {
      setError('Impossibile contattare il servizio.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-2xl px-6 py-16">
      <h1 className="text-3xl font-bold text-ink-900">Genera l&apos;annuncio</h1>
      <p className="mt-2 text-ink-600">
        Titolo e descrizione pronti da incollare su eBay o Vinted. Rileggili sempre prima di
        pubblicare: verifica che ogni dettaglio corrisponda davvero all&apos;oggetto che vendi.
      </p>

      <form onSubmit={handleSubmit} className="mt-8 space-y-4">
        <div>
          <label className="block text-sm font-medium text-ink-700">Nome oggetto</label>
          <input
            value={itemName}
            onChange={(e) => setItemName(e.target.value)}
            placeholder='Es. "Charizard Base Set Unlimited"'
            className="input mt-1"
          />
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="block text-sm font-medium text-ink-700">Categoria</label>
            <select value={categorySlug} onChange={(e) => setCategorySlug(e.target.value)} className="input mt-1">
              {CATEGORIES.map((c) => (
                <option key={c.slug} value={c.slug}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-ink-700">Condizioni</label>
            <select value={condition} onChange={(e) => setCondition(e.target.value)} className="input mt-1">
              {CONDITIONS.map((c) => (
                <option key={c} value={c}>
                  {c}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-ink-700">Dettagli aggiuntivi (opzionale)</label>
          <textarea
            value={details}
            onChange={(e) => setDetails(e.target.value)}
            rows={3}
            placeholder="Es. manca scatola originale, piccolo segno sul retro..."
            className="input mt-1"
          />
        </div>

        <button
          type="submit"
          disabled={loading || !itemName.trim()}
          className="rounded-lg bg-amber-600 px-6 py-2 text-sm font-semibold text-white hover:bg-amber-700 disabled:cursor-not-allowed disabled:bg-amber-300"
        >
          {loading ? 'Sto scrivendo...' : 'Genera annuncio'}
        </button>
      </form>

      {error && <p className="mt-6 text-sm text-red-600">{error}</p>}

      {copy && (
        <div className="mt-8 space-y-4">
          <CopyBlock label="Titolo" text={copy.title} />
          <CopyBlock label="Descrizione" text={copy.description} multiline />
          {copy.source === 'fallback' && (
            <p className="text-xs text-ink-400">
              Generato con un template locale di riserva (nessuna chiave API configurata) — è più
              basilare di quanto farebbe il modello, ma resta un buon punto di partenza.
            </p>
          )}
        </div>
      )}
    </div>
  );
}

function CopyBlock({ label, text, multiline }: { label: string; text: string; multiline?: boolean }) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      // clipboard access denied — the text is still selectable/visible below
    }
  }

  return (
    <div className="rounded-xl border border-amber-200 bg-white p-4">
      <div className="flex items-center justify-between">
        <span className="text-xs font-semibold uppercase tracking-wide text-ink-400">{label}</span>
        <button onClick={handleCopy} className="text-xs font-medium text-amber-700 hover:underline">
          {copied ? 'Copiato!' : 'Copia'}
        </button>
      </div>
      <p className={`mt-2 text-ink-800 ${multiline ? 'whitespace-pre-line' : ''}`}>{text}</p>
    </div>
  );
}

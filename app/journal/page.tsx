'use client';

import { FormEvent, useState } from 'react';

type Reflection = { text: string; source: 'live' | 'fallback' };

export default function JournalPage() {
  const [entry, setEntry] = useState('');
  const [reflection, setReflection] = useState<Reflection | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!entry.trim() || loading) return;

    setLoading(true);
    setError(null);
    setReflection(null);

    try {
      const res = await fetch('/api/journal', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ entry }),
      });
      const data = await res.json();

      if (!res.ok) {
        setError(data.error ?? 'Qualcosa è andato storto.');
        return;
      }

      setReflection(data);
    } catch {
      setError('Impossibile contattare il servizio. Riprova.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-2xl px-6 py-16">
      <h1 className="text-3xl font-bold text-sage-900">Demo: AI Mood Journal</h1>
      <p className="mt-2 text-sage-600">
        Scrivi liberamente come stai oggi. Riceverai una breve riflessione generata da un modello
        linguistico — non una diagnosi, solo uno spunto per guardare le cose da un altro angolo.
      </p>

      <form onSubmit={handleSubmit} className="mt-8">
        <textarea
          value={entry}
          onChange={(e) => setEntry(e.target.value)}
          maxLength={2000}
          rows={6}
          placeholder="Oggi mi sento..."
          className="w-full rounded-xl border border-sage-300 p-4 text-sage-900 focus:border-sage-500 focus:outline-none"
        />
        <div className="mt-3 flex items-center justify-between">
          <span className="text-xs text-sage-400">{entry.length}/2000</span>
          <button
            type="submit"
            disabled={loading || !entry.trim()}
            className="rounded-lg bg-sage-600 px-6 py-2 text-sm font-semibold text-white hover:bg-sage-700 disabled:cursor-not-allowed disabled:bg-sage-300"
          >
            {loading ? 'Sto riflettendo...' : 'Invia'}
          </button>
        </div>
      </form>

      {error && <p className="mt-6 text-sm text-red-600">{error}</p>}

      {reflection && (
        <div className="mt-8 rounded-2xl border border-sage-200 bg-white p-6">
          <p className="text-sage-800">{reflection.text}</p>
          {reflection.source === 'fallback' && (
            <p className="mt-4 text-xs text-sage-400">
              Risposta generata da un modello locale di riserva (nessuna chiave API configurata).
            </p>
          )}
        </div>
      )}

      <p className="mt-10 text-xs text-sage-400">
        Questa demo non memorizza le tue voci. Se stai attraversando un momento di crisi, contatta
        un professionista o un numero di emergenza: questo strumento non è un sostituto della
        terapia.
      </p>
    </div>
  );
}

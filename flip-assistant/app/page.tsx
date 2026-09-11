import Link from 'next/link';
import { CATEGORIES } from '@/data/categories';

export default function HomePage() {
  return (
    <div className="mx-auto max-w-5xl px-6 py-16">
      <span className="rounded-full bg-amber-100 px-4 py-1 text-sm font-medium text-amber-800">
        Compra basso, rivendi alto, tu tieni sempre il controllo del costo
      </span>
      <h1 className="mt-6 text-4xl font-bold tracking-tight text-ink-900">Flip Assistant</h1>
      <p className="mt-4 max-w-2xl text-lg text-ink-600">
        Strumento per il flipping di collezionabili nerd su eBay e Vinted. Niente scraping, niente
        promesse di guadagno garantito: solo tre aiuti concreti — trovare in fretta il prezzo di
        mercato reale, calcolare il margine netto dopo le commissioni, e scrivere annunci migliori.
      </p>

      <div className="mt-10 grid gap-4 sm:grid-cols-3">
        <ToolCard
          href="/comps"
          title="1. Controlla il prezzo"
          desc="Genera al volo i link di ricerca (venduti eBay, Vinted, Subito) prima di comprare qualcosa."
        />
        <ToolCard
          href="/margin"
          title="2. Calcola il margine"
          desc="Quanto ti resta davvero dopo le fee di eBay o Vinted e la spedizione."
        />
        <ToolCard
          href="/listing"
          title="3. Scrivi l'annuncio"
          desc="Titolo e descrizione generati dall'AI, pronti da incollare su eBay/Vinted."
        />
      </div>

      <h2 className="mt-16 text-xl font-semibold text-ink-900">Categorie coperte</h2>
      <div className="mt-4 grid gap-4 sm:grid-cols-2">
        {CATEGORIES.map((c) => (
          <div key={c.slug} className="rounded-xl border border-amber-200 bg-white p-5">
            <h3 className="font-semibold text-ink-800">{c.name}</h3>
            <p className="mt-1 text-sm text-ink-500">{c.tip}</p>
          </div>
        ))}
      </div>

      <div className="mt-16 rounded-2xl border border-amber-200 bg-white p-6">
        <h2 className="text-lg font-semibold text-ink-900">Tieni traccia dei guadagni</h2>
        <p className="mt-2 text-ink-600">
          Ogni acquisto/vendita registrato nel{' '}
          <Link href="/inventory" className="font-medium text-amber-700 underline">
            Magazzino
          </Link>{' '}
          concorre al totale del mese, così vedi subito se sei sopra o sotto il tuo obiettivo.
        </p>
      </div>
    </div>
  );
}

function ToolCard({ href, title, desc }: { href: string; title: string; desc: string }) {
  return (
    <Link
      href={href}
      className="block rounded-xl border border-amber-200 bg-white p-5 transition hover:shadow-md"
    >
      <h3 className="font-semibold text-ink-800">{title}</h3>
      <p className="mt-1 text-sm text-ink-500">{desc}</p>
    </Link>
  );
}

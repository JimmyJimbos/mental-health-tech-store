import Link from 'next/link';
import ProductCard from '@/components/ProductCard';
import { products } from '@/data/products';

export default function HomePage() {
  const featured = products.find((p) => p.featured) ?? products[0];

  return (
    <div>
      <section className="mx-auto max-w-5xl px-6 pb-16 pt-20 text-center">
        <span className="rounded-full bg-sage-100 px-4 py-1 text-sm font-medium text-sage-700">
          Piccoli strumenti, usati ogni giorno
        </span>
        <h1 className="mt-6 text-4xl font-bold tracking-tight text-sage-900 sm:text-5xl">
          Tecnologia semplice per prendersi cura della propria mente
        </h1>
        <p className="mx-auto mt-4 max-w-2xl text-lg text-sage-600">
          App, ebook e strumenti guidati da AI per il benessere quotidiano: journaling, gestione
          dell&apos;ansia, sonno e preparazione alle sedute di terapia. Non sostituiamo un
          professionista: costruiamo strumenti che riempiono lo spazio tra una seduta e l&apos;altra.
        </p>
        <div className="mt-8 flex justify-center gap-4">
          <Link
            href="/journal"
            className="rounded-lg bg-sage-600 px-6 py-3 text-sm font-semibold text-white hover:bg-sage-700"
          >
            Prova la demo AI Journal
          </Link>
          <Link
            href="/products"
            className="rounded-lg border border-sage-300 px-6 py-3 text-sm font-semibold text-sage-800 hover:bg-sage-50"
          >
            Vedi tutti i prodotti
          </Link>
        </div>
      </section>

      <section className="mx-auto max-w-5xl px-6 pb-24">
        <h2 className="mb-6 text-xl font-semibold text-sage-900">Prodotto in evidenza</h2>
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {products.map((product) => (
            <ProductCard key={product.slug} product={product} />
          ))}
        </div>
      </section>

      <section className="border-t border-sage-200 bg-white py-16">
        <div className="mx-auto max-w-3xl px-6 text-center">
          <h2 className="text-2xl font-semibold text-sage-900">
            Perché &quot;{featured.name}&quot; è il nostro prodotto principale
          </h2>
          <p className="mt-3 text-sage-600">{featured.description}</p>
        </div>
      </section>
    </div>
  );
}

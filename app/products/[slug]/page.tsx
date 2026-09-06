import { notFound } from 'next/navigation';
import Link from 'next/link';
import { getProduct, products } from '@/data/products';

export function generateStaticParams() {
  return products.map((p) => ({ slug: p.slug }));
}

export function generateMetadata({ params }: { params: { slug: string } }) {
  const product = getProduct(params.slug);
  return { title: product ? `${product.name} — MindTech Store` : 'Prodotto non trovato' };
}

export default function ProductPage({ params }: { params: { slug: string } }) {
  const product = getProduct(params.slug);
  if (!product) notFound();

  return (
    <div className="mx-auto max-w-2xl px-6 py-16">
      <Link href="/products" className="text-sm text-sage-600 hover:underline">
        ← Tutti i prodotti
      </Link>
      <h1 className="mt-4 text-3xl font-bold text-sage-900">{product.name}</h1>
      <p className="mt-2 text-lg text-sage-600">{product.tagline}</p>
      <p className="mt-6 text-sage-700">{product.description}</p>

      <div className="mt-8 flex items-center justify-between rounded-2xl border border-sage-200 bg-white p-6">
        <div>
          <p className="text-2xl font-semibold text-sage-900">
            {product.price}
            {product.billing === 'monthly' && (
              <span className="text-base font-normal text-sage-500">/mese</span>
            )}
          </p>
          <p className="text-sm text-sage-500">
            {product.billing === 'monthly' ? 'Annullabile in ogni momento' : 'Pagamento unico'}
          </p>
        </div>
        {/* Checkout stub: in produzione, questo bottone crea una Stripe Checkout Session
            lato server (app/api/checkout/route.ts) con il price id corrispondente. */}
        <button
          disabled
          title="Collega Stripe per abilitare l'acquisto"
          className="cursor-not-allowed rounded-lg bg-sage-300 px-6 py-3 text-sm font-semibold text-white"
        >
          Acquista (demo)
        </button>
      </div>

      {product.slug === 'ai-mood-journal' && (
        <p className="mt-6 text-sm text-sage-600">
          Vuoi provarlo prima di abbonarti?{' '}
          <Link href="/journal" className="font-medium text-sage-800 underline">
            Prova la demo gratuita
          </Link>
          .
        </p>
      )}
    </div>
  );
}

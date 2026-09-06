import ProductCard from '@/components/ProductCard';
import { products } from '@/data/products';

export const metadata = {
  title: 'Prodotti — MindTech Store',
};

export default function ProductsPage() {
  return (
    <div className="mx-auto max-w-5xl px-6 py-16">
      <h1 className="text-3xl font-bold text-sage-900">Tutti i prodotti</h1>
      <p className="mt-2 text-sage-600">
        Strumenti digitali pensati per il benessere quotidiano. Abbonamenti mensili per i tool
        d&apos;uso continuativo, acquisto singolo per le guide.
      </p>
      <div className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {products.map((product) => (
          <ProductCard key={product.slug} product={product} />
        ))}
      </div>
    </div>
  );
}

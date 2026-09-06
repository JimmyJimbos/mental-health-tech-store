import Link from 'next/link';
import { Product } from '@/data/products';

const CATEGORY_LABEL: Record<Product['category'], string> = {
  app: 'App',
  ebook: 'Ebook',
  tool: 'Tool web',
};

export default function ProductCard({ product }: { product: Product }) {
  return (
    <div className="flex flex-col rounded-2xl border border-sage-200 bg-white p-6 shadow-sm transition hover:shadow-md">
      <span className="mb-3 w-fit rounded-full bg-sage-100 px-3 py-1 text-xs font-medium text-sage-700">
        {CATEGORY_LABEL[product.category]}
      </span>
      <h3 className="text-lg font-semibold text-sage-900">{product.name}</h3>
      <p className="mt-1 text-sm text-sage-600">{product.tagline}</p>
      <div className="mt-4 flex items-center justify-between">
        <span className="text-base font-semibold text-sage-800">
          {product.price}
          {product.billing === 'monthly' && <span className="text-sm font-normal text-sage-500">/mese</span>}
        </span>
        <Link
          href={`/products/${product.slug}`}
          className="rounded-lg bg-sage-600 px-4 py-2 text-sm font-medium text-white hover:bg-sage-700"
        >
          Scopri
        </Link>
      </div>
    </div>
  );
}

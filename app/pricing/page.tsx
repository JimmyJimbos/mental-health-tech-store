import Link from 'next/link';
import { PRICING_TIERS } from '@/lib/pricing';
import CheckoutButton from '@/components/CheckoutButton';

export const metadata = { title: 'Prezzi — MindTech Store' };

export default function PricingPage() {
  return (
    <div className="mx-auto max-w-5xl px-6 py-16">
      <h1 className="text-center text-3xl font-bold text-sage-900">Prezzi semplici</h1>
      <p className="mx-auto mt-2 max-w-xl text-center text-sage-600">
        Inizia gratis, passa a un piano a pagamento quando il journal ti è già utile.
      </p>

      <div className="mt-12 grid gap-6 sm:grid-cols-3">
        {PRICING_TIERS.map((tier) => (
          <div
            key={tier.id}
            className={`rounded-2xl border p-6 ${
              tier.highlight ? 'border-sage-600 bg-white shadow-lg' : 'border-sage-200 bg-white'
            }`}
          >
            <h2 className="text-lg font-semibold text-sage-900">{tier.name}</h2>
            <p className="mt-2 text-3xl font-bold text-sage-900">
              {tier.price}
              <span className="text-base font-normal text-sage-500">{tier.period}</span>
            </p>
            <ul className="mt-6 space-y-2 text-sm text-sage-600">
              {tier.features.map((f) => (
                <li key={f} className="flex gap-2">
                  <span aria-hidden>✓</span>
                  {f}
                </li>
              ))}
            </ul>
            <div className="mt-8">
              {tier.mode === 'free' ? (
                <Link
                  href="/journal"
                  className="block w-full rounded-lg bg-sage-400 px-4 py-2 text-center text-sm font-semibold text-white hover:bg-sage-500"
                >
                  {tier.cta}
                </Link>
              ) : (
                <CheckoutButton
                  priceEnv={tier.stripePriceEnv as string}
                  mode={tier.mode}
                  label={tier.cta}
                  className={`w-full rounded-lg px-4 py-2 text-sm font-semibold text-white disabled:cursor-not-allowed disabled:opacity-70 ${
                    tier.highlight ? 'bg-sage-600 hover:bg-sage-700' : 'bg-sage-400 hover:bg-sage-500'
                  }`}
                />
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

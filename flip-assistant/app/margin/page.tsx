'use client';

import { useMemo, useState } from 'react';
import { CATEGORIES } from '@/data/categories';
import { calculateMargin, Platform } from '@/lib/margin';

export default function MarginPage() {
  const [platform, setPlatform] = useState<Platform>('ebay');
  const [categorySlug, setCategorySlug] = useState(CATEGORIES[0].slug);
  const [buyPrice, setBuyPrice] = useState('');
  const [sellPrice, setSellPrice] = useState('');
  const [shippingCost, setShippingCost] = useState('0');
  const [ebayFeePct, setEbayFeePct] = useState(String(CATEGORIES[0].defaultEbayFeePct));
  const [ebayFixedFee, setEbayFixedFee] = useState('0.35');

  function onCategoryChange(slug: string) {
    setCategorySlug(slug);
    const cat = CATEGORIES.find((c) => c.slug === slug);
    if (cat) setEbayFeePct(String(cat.defaultEbayFeePct));
  }

  const result = useMemo(() => {
    const buy = parseFloat(buyPrice) || 0;
    const sell = parseFloat(sellPrice) || 0;
    const shipping = parseFloat(shippingCost) || 0;
    const feePct = parseFloat(ebayFeePct) || 0;
    const fixedFee = parseFloat(ebayFixedFee) || 0;

    return calculateMargin({
      platform,
      buyPrice: buy,
      sellPrice: sell,
      shippingCost: shipping,
      ebayFeePct: feePct,
      ebayFixedFee: fixedFee,
    });
  }, [platform, buyPrice, sellPrice, shippingCost, ebayFeePct, ebayFixedFee]);

  const hasInput = buyPrice.trim() !== '' && sellPrice.trim() !== '';

  return (
    <div className="mx-auto max-w-2xl px-6 py-16">
      <h1 className="text-3xl font-bold text-ink-900">Calcola il margine netto</h1>
      <p className="mt-2 text-ink-600">
        Le fee sono stime di partenza, sempre modificabili: verifica i valori attuali sulla pagina
        ufficiale tariffe di eBay prima di fidarti al 100%.
      </p>

      <div className="mt-8 grid gap-4 sm:grid-cols-2">
        <Field label="Piattaforma">
          <select
            value={platform}
            onChange={(e) => setPlatform(e.target.value as Platform)}
            className="input"
          >
            <option value="ebay">eBay</option>
            <option value="vinted">Vinted</option>
          </select>
        </Field>

        <Field label="Categoria">
          <select value={categorySlug} onChange={(e) => onCategoryChange(e.target.value)} className="input">
            {CATEGORIES.map((c) => (
              <option key={c.slug} value={c.slug}>
                {c.name}
              </option>
            ))}
          </select>
        </Field>

        <Field label="Prezzo d'acquisto (€)">
          <input value={buyPrice} onChange={(e) => setBuyPrice(e.target.value)} type="number" min="0" step="0.01" className="input" />
        </Field>

        <Field label="Prezzo di vendita previsto (€)">
          <input value={sellPrice} onChange={(e) => setSellPrice(e.target.value)} type="number" min="0" step="0.01" className="input" />
        </Field>

        <Field label="Costo spedizione a tuo carico (€)">
          <input value={shippingCost} onChange={(e) => setShippingCost(e.target.value)} type="number" min="0" step="0.01" className="input" />
        </Field>

        {platform === 'ebay' && (
          <>
            <Field label="Fee eBay (%)">
              <input value={ebayFeePct} onChange={(e) => setEbayFeePct(e.target.value)} type="number" min="0" step="0.01" className="input" />
            </Field>
            <Field label="Fee fissa per ordine (€)">
              <input value={ebayFixedFee} onChange={(e) => setEbayFixedFee(e.target.value)} type="number" min="0" step="0.01" className="input" />
            </Field>
          </>
        )}
      </div>

      {platform === 'vinted' && (
        <p className="mt-4 text-xs text-ink-400">
          Su Vinted la fee di protezione acquisti la paga il compratore in aggiunta al prezzo: tu
          come venditore incassi l&apos;intero prezzo che imposti, meno l&apos;eventuale spedizione a tuo
          carico.
        </p>
      )}

      {hasInput && (
        <div className="mt-8 rounded-2xl border border-amber-200 bg-white p-6">
          <Row label="Fee trattenute" value={`${result.fees.toFixed(2)}€`} />
          <Row label="Incasso netto" value={`${result.netProceeds.toFixed(2)}€`} />
          <Row
            label="Profitto"
            value={`${result.profit.toFixed(2)}€`}
            emphasize={result.profit >= 0 ? 'positive' : 'negative'}
          />
          <Row label="Margine sul capitale investito" value={`${result.marginPct.toFixed(1)}%`} />
        </div>
      )}
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="block text-sm font-medium text-ink-700">
      {label}
      <div className="mt-1">{children}</div>
    </label>
  );
}

function Row({
  label,
  value,
  emphasize,
}: {
  label: string;
  value: string;
  emphasize?: 'positive' | 'negative';
}) {
  return (
    <div className="flex items-center justify-between border-b border-amber-100 py-2 last:border-0">
      <span className="text-sm text-ink-600">{label}</span>
      <span
        className={`text-base font-semibold ${
          emphasize === 'positive' ? 'text-green-700' : emphasize === 'negative' ? 'text-red-600' : 'text-ink-900'
        }`}
      >
        {value}
      </span>
    </div>
  );
}

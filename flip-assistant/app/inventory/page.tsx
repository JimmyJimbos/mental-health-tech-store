'use client';

import { FormEvent, useEffect, useMemo, useState } from 'react';
import { CATEGORIES } from '@/data/categories';
import { InventoryItem, isSameMonth, loadInventory, saveInventory } from '@/lib/inventory';

const GOAL_STORAGE_KEY = 'flip-assistant.goal.v1';
const DEFAULT_GOAL = 109;

export default function InventoryPage() {
  const [items, setItems] = useState<InventoryItem[]>([]);
  const [goal, setGoal] = useState(DEFAULT_GOAL);
  const [name, setName] = useState('');
  const [category, setCategory] = useState(CATEGORIES[0].slug);
  const [buyPrice, setBuyPrice] = useState('');
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    setItems(loadInventory());
    const storedGoal = typeof window !== 'undefined' ? window.localStorage.getItem(GOAL_STORAGE_KEY) : null;
    if (storedGoal) setGoal(parseFloat(storedGoal));
    setLoaded(true);
  }, []);

  useEffect(() => {
    if (loaded) saveInventory(items);
  }, [items, loaded]);

  useEffect(() => {
    if (loaded && typeof window !== 'undefined') window.localStorage.setItem(GOAL_STORAGE_KEY, String(goal));
  }, [goal, loaded]);

  function addItem(e: FormEvent) {
    e.preventDefault();
    const price = parseFloat(buyPrice);
    if (!name.trim() || Number.isNaN(price)) return;

    const item: InventoryItem = {
      id: crypto.randomUUID(),
      name: name.trim(),
      category,
      buyPrice: price,
      sellPrice: null,
      status: 'in_stock',
      buyDate: new Date().toISOString(),
      soldDate: null,
    };

    setItems((prev) => [item, ...prev]);
    setName('');
    setBuyPrice('');
  }

  function updateItem(id: string, patch: Partial<InventoryItem>) {
    setItems((prev) => prev.map((it) => (it.id === id ? { ...it, ...patch } : it)));
  }

  function markSold(id: string, sellPrice: number) {
    updateItem(id, { status: 'sold', sellPrice, soldDate: new Date().toISOString() });
  }

  function removeItem(id: string) {
    setItems((prev) => prev.filter((it) => it.id !== id));
  }

  const now = new Date();
  const monthlyProfit = useMemo(() => {
    return items
      .filter((it) => it.status === 'sold' && it.sellPrice !== null && it.soldDate && isSameMonth(it.soldDate, now))
      .reduce((sum, it) => sum + ((it.sellPrice as number) - it.buyPrice), 0);
  }, [items, now]);

  const progressPct = goal > 0 ? Math.min(100, (monthlyProfit / goal) * 100) : 0;

  return (
    <div className="mx-auto max-w-4xl px-6 py-16">
      <h1 className="text-3xl font-bold text-ink-900">Magazzino</h1>
      <p className="mt-2 text-ink-600">
        Dati salvati solo su questo browser (localStorage) — nessun server, nessun account. Se
        cambi dispositivo o browser, il magazzino non ti segue.
      </p>

      <div className="mt-8 rounded-2xl border border-amber-200 bg-white p-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="text-sm text-ink-500">Profitto questo mese</p>
            <p className={`text-2xl font-bold ${monthlyProfit >= goal ? 'text-green-700' : 'text-ink-900'}`}>
              {monthlyProfit.toFixed(2)}€
            </p>
          </div>
          <label className="text-sm text-ink-600">
            Obiettivo (€)
            <input
              type="number"
              value={goal}
              onChange={(e) => setGoal(parseFloat(e.target.value) || 0)}
              className="input mt-1 w-32"
            />
          </label>
        </div>
        <div className="mt-4 h-3 w-full overflow-hidden rounded-full bg-amber-100">
          <div className="h-full bg-amber-500 transition-all" style={{ width: `${progressPct}%` }} />
        </div>
        <p className="mt-2 text-xs text-ink-400">{progressPct.toFixed(0)}% dell&apos;obiettivo mensile</p>
      </div>

      <form onSubmit={addItem} className="mt-8 grid gap-4 rounded-2xl border border-amber-200 bg-white p-6 sm:grid-cols-4">
        <div className="sm:col-span-2">
          <label className="block text-sm font-medium text-ink-700">Nome oggetto</label>
          <input value={name} onChange={(e) => setName(e.target.value)} className="input mt-1" placeholder="Es. Game Boy Color Viola" />
        </div>
        <div>
          <label className="block text-sm font-medium text-ink-700">Categoria</label>
          <select value={category} onChange={(e) => setCategory(e.target.value)} className="input mt-1">
            {CATEGORIES.map((c) => (
              <option key={c.slug} value={c.slug}>
                {c.name}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-ink-700">Prezzo d&apos;acquisto (€)</label>
          <input value={buyPrice} onChange={(e) => setBuyPrice(e.target.value)} type="number" min="0" step="0.01" className="input mt-1" />
        </div>
        <div className="sm:col-span-4">
          <button type="submit" className="rounded-lg bg-amber-600 px-6 py-2 text-sm font-semibold text-white hover:bg-amber-700">
            Aggiungi al magazzino
          </button>
        </div>
      </form>

      <div className="mt-8 space-y-3">
        {items.length === 0 && <p className="text-sm text-ink-400">Nessun oggetto ancora. Aggiungine uno sopra.</p>}
        {items.map((item) => (
          <ItemRow key={item.id} item={item} onMarkSold={markSold} onRemove={removeItem} />
        ))}
      </div>
    </div>
  );
}

function ItemRow({
  item,
  onMarkSold,
  onRemove,
}: {
  item: InventoryItem;
  onMarkSold: (id: string, sellPrice: number) => void;
  onRemove: (id: string) => void;
}) {
  const [sellPriceInput, setSellPriceInput] = useState('');
  const categoryName = CATEGORIES.find((c) => c.slug === item.category)?.name ?? item.category;

  return (
    <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-amber-200 bg-white p-4">
      <div>
        <p className="font-medium text-ink-800">{item.name}</p>
        <p className="text-xs text-ink-400">
          {categoryName} · comprato a {item.buyPrice.toFixed(2)}€
          {item.status === 'sold' && item.sellPrice !== null && (
            <>
              {' '}
              · venduto a {item.sellPrice.toFixed(2)}€ · profitto{' '}
              <span className={item.sellPrice - item.buyPrice >= 0 ? 'text-green-700' : 'text-red-600'}>
                {(item.sellPrice - item.buyPrice).toFixed(2)}€
              </span>
            </>
          )}
        </p>
      </div>

      {item.status !== 'sold' ? (
        <div className="flex items-center gap-2">
          <input
            value={sellPriceInput}
            onChange={(e) => setSellPriceInput(e.target.value)}
            type="number"
            min="0"
            step="0.01"
            placeholder="Prezzo venduto"
            className="input w-32 py-1.5 text-sm"
          />
          <button
            onClick={() => {
              const price = parseFloat(sellPriceInput);
              if (!Number.isNaN(price)) onMarkSold(item.id, price);
            }}
            className="rounded-lg bg-green-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-green-700"
          >
            Segna venduto
          </button>
          <button onClick={() => onRemove(item.id)} className="text-xs text-ink-400 hover:text-red-600">
            Rimuovi
          </button>
        </div>
      ) : (
        <button onClick={() => onRemove(item.id)} className="text-xs text-ink-400 hover:text-red-600">
          Rimuovi
        </button>
      )}
    </div>
  );
}

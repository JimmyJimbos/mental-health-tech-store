'use client';

import { useState } from 'react';

export default function CheckoutButton({
  priceEnv,
  mode,
  label,
  className,
}: {
  priceEnv: string;
  mode: 'payment' | 'subscription';
  label: string;
  className?: string;
}) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleClick() {
    setLoading(true);
    setError(null);

    try {
      const res = await fetch('/api/checkout', {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ priceEnv, mode }),
      });
      const data = await res.json();

      if (!res.ok) {
        setError(data.error ?? 'Impossibile avviare il pagamento.');
        return;
      }

      window.location.href = data.url;
    } catch {
      setError('Impossibile contattare il servizio di pagamento.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <button onClick={handleClick} disabled={loading} className={className}>
        {loading ? 'Un momento...' : label}
      </button>
      {error && <p className="mt-2 text-xs text-red-600">{error}</p>}
    </div>
  );
}

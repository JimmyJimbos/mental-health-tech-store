import { NextRequest, NextResponse } from 'next/server';
import { getStripe } from '@/lib/stripe';
import { products } from '@/data/products';
import { PRICING_TIERS } from '@/lib/pricing';

const ALLOWED_PRICE_ENVS = new Set<string>([
  ...products.map((p) => p.stripePriceEnv),
  ...PRICING_TIERS.filter((t) => t.stripePriceEnv).map((t) => t.stripePriceEnv as string),
]);

export async function POST(req: NextRequest) {
  let body: unknown;
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: 'Corpo della richiesta non valido.' }, { status: 400 });
  }

  const { priceEnv, mode } = (body as { priceEnv?: unknown; mode?: unknown }) ?? {};

  if (typeof priceEnv !== 'string' || !ALLOWED_PRICE_ENVS.has(priceEnv)) {
    return NextResponse.json({ error: 'Prodotto non riconosciuto.' }, { status: 400 });
  }
  if (mode !== 'payment' && mode !== 'subscription') {
    return NextResponse.json({ error: 'Modalità di pagamento non valida.' }, { status: 400 });
  }

  const stripe = getStripe();
  if (!stripe) {
    return NextResponse.json(
      { error: 'I pagamenti non sono ancora configurati su questo store (manca STRIPE_SECRET_KEY).' },
      { status: 503 },
    );
  }

  const priceId = process.env[priceEnv];
  if (!priceId) {
    return NextResponse.json(
      { error: `Manca la variabile d'ambiente ${priceEnv} con l'ID prezzo Stripe.` },
      { status: 503 },
    );
  }

  const baseUrl = process.env.NEXT_PUBLIC_BASE_URL ?? req.nextUrl.origin;

  try {
    const session = await stripe.checkout.sessions.create({
      mode,
      line_items: [{ price: priceId, quantity: 1 }],
      success_url: `${baseUrl}/checkout/success`,
      cancel_url: `${baseUrl}/checkout/cancel`,
    });

    return NextResponse.json({ url: session.url });
  } catch (err) {
    console.error('Stripe checkout error', err);
    return NextResponse.json({ error: 'Impossibile creare la sessione di pagamento.' }, { status: 500 });
  }
}

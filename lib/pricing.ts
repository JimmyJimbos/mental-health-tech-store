export type PricingTier = {
  id: string;
  name: string;
  price: string;
  period: string;
  features: string[];
  cta: string;
  highlight?: boolean;
  mode: 'payment' | 'subscription' | 'free';
  /** Name of the env var holding the real Stripe Price ID. Absent for the free tier. */
  stripePriceEnv?: string;
};

export const PRICING_TIERS: PricingTier[] = [
  {
    id: 'free',
    name: 'Free',
    price: '0€',
    period: '',
    features: ['3 voci di journal al mese', 'Riflessioni AI di base', 'Nessuna esportazione dati'],
    cta: 'Inizia gratis',
    mode: 'free',
  },
  {
    id: 'plus',
    name: 'Plus',
    price: '6,99€',
    period: '/mese',
    features: [
      'Journal illimitato',
      'Riflessioni AI complete',
      'Storico e ricerca nelle voci',
      'Esportazione PDF',
    ],
    cta: 'Passa a Plus',
    highlight: true,
    mode: 'subscription',
    stripePriceEnv: 'STRIPE_PRICE_PLUS_MONTHLY',
  },
  {
    id: 'annual',
    name: 'Annuale',
    price: '59€',
    period: '/anno',
    features: ['Tutto di Plus', "2 mesi gratis rispetto al mensile", 'Supporto prioritario'],
    cta: 'Passa ad Annuale',
    mode: 'subscription',
    stripePriceEnv: 'STRIPE_PRICE_ANNUAL',
  },
];

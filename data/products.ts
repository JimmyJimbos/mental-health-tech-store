export type Product = {
  slug: string;
  name: string;
  tagline: string;
  description: string;
  price: string;
  billing: 'one-time' | 'monthly';
  category: 'app' | 'ebook' | 'tool';
  featured?: boolean;
  /** Name of the env var holding the real Stripe Price ID for this product. */
  stripePriceEnv: string;
};

export const products: Product[] = [
  {
    slug: 'ai-mood-journal',
    name: 'AI Mood Journal',
    tagline: 'Scrivi come ti senti, ricevi una riflessione guidata sul momento.',
    description:
      'Un diario guidato dove ogni voce riceve una riflessione generata da un modello linguistico, pensata per aiutarti a notare pattern nel tuo umore e a scegliere una micro-azione concreta. Non sostituisce una terapia: è uno strumento di auto-osservazione quotidiana.',
    price: '6,99€',
    billing: 'monthly',
    category: 'tool',
    featured: true,
    stripePriceEnv: 'STRIPE_PRICE_AI_MOOD_JOURNAL',
  },
  {
    slug: 'anxiety-toolkit-ebook',
    name: 'Anxiety Toolkit',
    tagline: 'Guida pratica con 20 tecniche da usare nei momenti di ansia acuta.',
    description:
      'Ebook di 60 pagine con tecniche di respirazione, grounding e ristrutturazione cognitiva, organizzate per "quanto tempo hai" (2 minuti, 10 minuti, mezz\'ora). Include schede stampabili.',
    price: '9,90€',
    billing: 'one-time',
    category: 'ebook',
    stripePriceEnv: 'STRIPE_PRICE_ANXIETY_TOOLKIT',
  },
  {
    slug: 'calm-sleep-sounds',
    name: 'Calm Sleep Sounds',
    tagline: "App per l'addormentamento con paesaggi sonori adattivi.",
    description:
      'App mobile con suoni generativi che si adattano al tuo respiro rilevato dal microfono, pensata per chi fatica a staccare la mente la sera.',
    price: '4,99€',
    billing: 'monthly',
    category: 'app',
    stripePriceEnv: 'STRIPE_PRICE_CALM_SLEEP_SOUNDS',
  },
  {
    slug: 'therapy-session-prep',
    name: 'Therapy Session Prep',
    tagline: 'Prepara la tua prossima seduta in 5 minuti.',
    description:
      "Strumento che ti aiuta a mettere in ordine le idee prima di una seduta di terapia: cosa è successo questa settimana, cosa vuoi portare, cosa vuoi ricordarti di dire. Pensato per chi arriva in seduta e si dimentica tutto.",
    price: '3,99€',
    billing: 'monthly',
    category: 'tool',
    stripePriceEnv: 'STRIPE_PRICE_THERAPY_SESSION_PREP',
  },
];

export function getProduct(slug: string): Product | undefined {
  return products.find((p) => p.slug === slug);
}

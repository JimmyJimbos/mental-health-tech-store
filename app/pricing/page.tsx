const TIERS = [
  {
    name: 'Free',
    price: '0€',
    period: '',
    features: ['3 voci di journal al mese', 'Riflessioni AI di base', 'Nessuna esportazione dati'],
    cta: 'Inizia gratis',
  },
  {
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
  },
  {
    name: 'Annuale',
    price: '59€',
    period: '/anno',
    features: ['Tutto di Plus', "2 mesi gratis rispetto al mensile", 'Supporto prioritario'],
    cta: 'Passa ad Annuale',
  },
];

export const metadata = { title: 'Prezzi — MindTech Store' };

export default function PricingPage() {
  return (
    <div className="mx-auto max-w-5xl px-6 py-16">
      <h1 className="text-center text-3xl font-bold text-sage-900">Prezzi semplici</h1>
      <p className="mx-auto mt-2 max-w-xl text-center text-sage-600">
        Inizia gratis, passa a un piano a pagamento quando il journal ti è già utile.
      </p>

      <div className="mt-12 grid gap-6 sm:grid-cols-3">
        {TIERS.map((tier) => (
          <div
            key={tier.name}
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
            <button
              disabled
              title="Collega Stripe per abilitare i pagamenti"
              className={`mt-8 w-full cursor-not-allowed rounded-lg px-4 py-2 text-sm font-semibold text-white ${
                tier.highlight ? 'bg-sage-600' : 'bg-sage-400'
              }`}
            >
              {tier.cta} (demo)
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

import Link from 'next/link';

export const metadata = { title: 'Pagamento annullato — MindTech Store' };

export default function CheckoutCancelPage() {
  return (
    <div className="mx-auto max-w-lg px-6 py-24 text-center">
      <h1 className="text-3xl font-bold text-sage-900">Pagamento annullato</h1>
      <p className="mt-4 text-sage-600">
        Nessun addebito è stato effettuato. Puoi riprovare quando vuoi.
      </p>
      <Link
        href="/pricing"
        className="mt-8 inline-block rounded-lg bg-sage-600 px-6 py-3 text-sm font-semibold text-white hover:bg-sage-700"
      >
        Torna ai prezzi
      </Link>
    </div>
  );
}

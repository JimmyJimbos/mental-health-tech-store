import Link from 'next/link';

export const metadata = { title: 'Pagamento completato — MindTech Store' };

export default function CheckoutSuccessPage() {
  return (
    <div className="mx-auto max-w-lg px-6 py-24 text-center">
      <h1 className="text-3xl font-bold text-sage-900">Grazie!</h1>
      <p className="mt-4 text-sage-600">
        Il pagamento è andato a buon fine. Riceverai a breve un&apos;email di conferma con i
        dettagli di accesso.
      </p>
      <Link
        href="/"
        className="mt-8 inline-block rounded-lg bg-sage-600 px-6 py-3 text-sm font-semibold text-white hover:bg-sage-700"
      >
        Torna alla home
      </Link>
    </div>
  );
}

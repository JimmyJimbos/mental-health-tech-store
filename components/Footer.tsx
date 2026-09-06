export default function Footer() {
  return (
    <footer className="mt-24 border-t border-sage-200 bg-white">
      <div className="mx-auto max-w-5xl px-6 py-8 text-sm text-sage-600">
        <p>
          MindTech Store non fornisce diagnosi né trattamento medico. Se sei in una crisi o pensi di
          essere in pericolo, contatta i servizi di emergenza del tuo paese o un professionista
          della salute mentale.
        </p>
        <p className="mt-2">© {new Date().getFullYear()} MindTech Store.</p>
      </div>
    </footer>
  );
}

import Link from 'next/link';

const LINKS = [
  { href: '/comps', label: 'Comps' },
  { href: '/margin', label: 'Margine' },
  { href: '/listing', label: 'Annuncio AI' },
  { href: '/inventory', label: 'Magazzino' },
];

export default function Header() {
  return (
    <header className="border-b border-amber-200 bg-white/80 backdrop-blur sticky top-0 z-10">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
        <Link href="/" className="text-lg font-semibold text-ink-800">
          Flip Assistant
        </Link>
        <nav className="flex gap-6 text-sm font-medium text-ink-600">
          {LINKS.map((l) => (
            <Link key={l.href} href={l.href} className="hover:text-ink-900">
              {l.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}

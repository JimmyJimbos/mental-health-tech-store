import Link from 'next/link';

export default function Header() {
  return (
    <header className="border-b border-sage-200 bg-white/80 backdrop-blur sticky top-0 z-10">
      <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
        <Link href="/" className="text-lg font-semibold text-sage-800">
          MindTech Store
        </Link>
        <nav className="flex gap-6 text-sm font-medium text-sage-700">
          <Link href="/products" className="hover:text-sage-900">
            Prodotti
          </Link>
          <Link href="/journal" className="hover:text-sage-900">
            Demo AI Journal
          </Link>
          <Link href="/pricing" className="hover:text-sage-900">
            Prezzi
          </Link>
        </nav>
      </div>
    </header>
  );
}

import type { Metadata } from 'next';
import './globals.css';
import Header from '@/components/Header';
import Footer from '@/components/Footer';

export const metadata: Metadata = {
  title: 'Flip Assistant — retro games, carte, Funko, fumetti, board game',
  description:
    'Strumento personale per il flipping di collezionabili nerd su eBay e Vinted: comps di mercato, calcolo margine, annunci generati con AI, magazzino.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="it">
      <body className="flex min-h-screen flex-col text-ink-900 antialiased">
        <Header />
        <main className="flex-1">{children}</main>
        <Footer />
      </body>
    </html>
  );
}

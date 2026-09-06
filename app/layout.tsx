import type { Metadata } from 'next';
import './globals.css';
import Header from '@/components/Header';
import Footer from '@/components/Footer';

export const metadata: Metadata = {
  title: 'MindTech Store — strumenti digitali per il benessere mentale',
  description:
    'App, ebook e strumenti AI per il benessere mentale quotidiano: journaling guidato, gestione dell\'ansia, sonno e preparazione alle sedute di terapia.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="it">
      <body className="flex min-h-screen flex-col text-sage-900 antialiased">
        <Header />
        <main className="flex-1">{children}</main>
        <Footer />
      </body>
    </html>
  );
}

import { NextRequest, NextResponse } from 'next/server';
import { generateListingCopy } from '@/lib/ai';

export async function POST(req: NextRequest) {
  let body: unknown;
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: 'Corpo della richiesta non valido.' }, { status: 400 });
  }

  const { itemName, category, condition, details } = (body as Record<string, unknown>) ?? {};

  if (typeof itemName !== 'string' || !itemName.trim()) {
    return NextResponse.json({ error: "Inserisci il nome dell'oggetto." }, { status: 400 });
  }
  if (typeof category !== 'string' || typeof condition !== 'string') {
    return NextResponse.json({ error: 'Categoria o condizione mancanti.' }, { status: 400 });
  }

  const copy = await generateListingCopy({
    itemName: itemName.trim(),
    category,
    condition,
    details: typeof details === 'string' ? details.trim() : '',
  });

  return NextResponse.json(copy);
}

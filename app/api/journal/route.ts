import { NextRequest, NextResponse } from 'next/server';
import { getReflection } from '@/lib/ai';

const MAX_ENTRY_LENGTH = 2000;

export async function POST(req: NextRequest) {
  let body: unknown;
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: 'Corpo della richiesta non valido.' }, { status: 400 });
  }

  const entry = (body as { entry?: unknown })?.entry;

  if (typeof entry !== 'string' || !entry.trim()) {
    return NextResponse.json({ error: 'Scrivi qualcosa prima di inviare.' }, { status: 400 });
  }

  if (entry.length > MAX_ENTRY_LENGTH) {
    return NextResponse.json(
      { error: `Il testo è troppo lungo (max ${MAX_ENTRY_LENGTH} caratteri).` },
      { status: 400 },
    );
  }

  const reflection = await getReflection(entry.trim());
  return NextResponse.json(reflection);
}

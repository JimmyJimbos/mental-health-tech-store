const FALLBACK_REFLECTIONS = [
  'Quello che descrivi suona pesante da portare da solo/a. Prova a nominare, con una parola sola, l\'emozione più forte che senti adesso: a volte dare un nome a una sensazione ne riduce l\'intensità.',
  'Noto che parli molto di quello che "dovrebbe" succedere. Cosa cambierebbe, oggi, se ti concentrassi solo su quello che è realmente in tuo controllo in questo momento?',
  'Hai scritto qualcosa di importante. Prima di continuare la giornata, prova 4 respiri lenti (4 secondi inspirando, 6 espirando): non risolve il problema, ma può abbassare l\'attivazione fisica di qualche grado.',
  'Sembra una giornata in cui hai dato molto agli altri. Una domanda semplice: oggi, cosa hai fatto solo per te, anche piccolo?',
  'Quello che racconti ha più strati. Se dovessi scegliere UN solo pensiero su cui lavorare oggi, quale sceglieresti?',
];

function fallbackReflection(entry: string): string {
  const seed = entry.length % FALLBACK_REFLECTIONS.length;
  return FALLBACK_REFLECTIONS[seed];
}

export async function getReflection(entry: string): Promise<{ text: string; source: 'live' | 'fallback' }> {
  const apiKey = process.env.ANTHROPIC_API_KEY;

  if (!apiKey) {
    return { text: fallbackReflection(entry), source: 'fallback' };
  }

  try {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'content-type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify({
        model: 'claude-haiku-4-5-20251001',
        max_tokens: 200,
        system:
          'Sei un assistente di journaling per il benessere mentale, non uno psicoterapeuta. ' +
          'Rispondi in italiano, in massimo 3 frasi, con tono caldo e non giudicante. ' +
          'Offri una riflessione o una domanda aperta, mai una diagnosi o un consiglio medico. ' +
          'Se il testo suggerisce rischio immediato per la persona, invitala con chiarezza a contattare un numero di emergenza o un professionista.',
        messages: [{ role: 'user', content: entry }],
      }),
    });

    if (!response.ok) {
      return { text: fallbackReflection(entry), source: 'fallback' };
    }

    const data = await response.json();
    const text = data?.content?.[0]?.text;
    if (typeof text !== 'string' || !text.trim()) {
      return { text: fallbackReflection(entry), source: 'fallback' };
    }

    return { text: text.trim(), source: 'live' };
  } catch {
    return { text: fallbackReflection(entry), source: 'fallback' };
  }
}

# MindTech Store

Store digitale per prodotti di benessere mentale (app, ebook, tool AI), con una **feature AI
funzionante dal vivo**: `/journal`, un mini diario che restituisce una riflessione generata da un
modello linguistico (Claude) o, in assenza di una chiave API, da un set di risposte di riserva
locali — l'app funziona comunque, end-to-end, senza configurazione.

## Perché questo progetto

È il prototipo minimo per validare due delle idee di monetizzazione discusse: un **wrapper AI a
valore aggiunto** (non la chat generica, ma uno strumento verticale su un problema specifico) più
un piccolo **catalogo di prodotti digitali** (ebook + app + tool) attorno allo stesso pubblico.
Il flusso pensato per generare ricavi:

1. Il visitatore prova la demo gratuita (`/journal`) senza registrarsi.
2. Se la trova utile, si converte su un piano a pagamento (`/pricing`): free → 6,99€/mese → 59€/anno.
3. Il catalogo (`/products`) vende in cross-sell prodotti complementari (ebook, altre app) allo
   stesso pubblico già interessato al benessere mentale.

## Cosa è reale e cosa è uno stub

- ✅ Il sito è una vera app Next.js 14 (App Router + TypeScript + Tailwind), builda ed è stata
  testata end-to-end (build di produzione + smoke test su tutte le route).
- ✅ `/journal` chiama davvero `POST /api/journal`, che a sua volta chiama l'API di Anthropic se
  `ANTHROPIC_API_KEY` è impostata in `.env.local` (vedi `.env.example`). Senza chiave, risponde con
  un fallback locale realistico — quindi la demo è sempre presentabile, anche a costo zero.
- ✅ I bottoni "Acquista" (pagina prodotto) e i piani a pagamento (`/pricing`) chiamano davvero
  `POST /api/checkout`, che crea una vera Stripe Checkout Session e reindirizza l'utente a Stripe.
  Senza `STRIPE_SECRET_KEY` configurata, il bottone mostra un messaggio d'errore chiaro invece di
  fingere un pagamento riuscito — testato sia senza chiave (errore 503) sia con una chiave non
  valida (errore 500 pulito, nessun crash). Gli ID prezzo Stripe passano per un allowlist lato
  server: il client non può far leggere all'API variabili d'ambiente arbitrarie.
- ⛔ Non c'è ancora un webhook Stripe che aggiorna lo stato dell'ordine/abbonamento nel tuo
  database, né autenticazione utente: al momento un pagamento riuscito porta solo a una pagina di
  ringraziamento statica.

## Come continuare da qui

1. **Attivare i pagamenti veri**: creare i prodotti/prezzi nella Stripe Dashboard, copiare i
   `price_...` id nelle variabili corrispondenti in `.env.local` (vedi `.env.example`) insieme a
   `STRIPE_SECRET_KEY`. Non serve altro codice: i bottoni sono già collegati.
2. **Attivare le risposte AI live**: copiare `.env.example` in `.env.local` e impostare
   `ANTHROPIC_API_KEY`. Nessun'altra modifica necessaria.
3. **Webhook + persistenza**: aggiungere `app/api/webhooks/stripe/route.ts` per ricevere
   `checkout.session.completed` e salvare l'acquisto/abbonamento in un database, più
   autenticazione utente per far corrispondere ordini e account.
4. **Persistenza del journal**: al momento `/journal` non salva nulla (voluto, per la demo
   pubblica). Per il prodotto vero servirà storage delle voci legato all'utente autenticato.
5. **Contenuti reali**: gli ebook e le app in `data/products.ts` sono placeholder — vanno scritti/
   sviluppati per davvero prima di vendere qualcosa.

## Sviluppo locale

```bash
npm install
npm run dev       # http://localhost:3000
npm run build     # build di produzione
```

## Nota etica/legale

Questo non è un dispositivo medico né un servizio di terapia. I testi nel prodotto includono
disclaimer visibili (footer, pagina journal) e il prompt di sistema per il modello istruisce a non
fornire diagnosi e a indirizzare a servizi di emergenza in caso di rischio. Prima di un lancio
reale, far rivedere claim e disclaimer a un legale, in particolare se si opera in UE (GDPR, dati
sanitari come categoria speciale) o si vuole vendere negli USA/UK.

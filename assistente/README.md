# Assistente personale (stile J.A.R.V.I.S.)

Gira sul PC Windows. Gli parli dicendo **"Hey Jarvis"**, oppure gli scrivi nell'HUD del browser. Dal telefono gli scrivi o gli mandi vocali su **Telegram**.

**Cosa sa fare:** leggere e segnare impegni su Google Calendar, gestire le cose da fare su Google Tasks, impostare promemoria che ti dice a voce e ti scrive su Telegram, cercare sul web, avviare un **agente di ricerca** in background che ti manda un rapporto, aprire programmi e siti, fare screenshot, eseguire azioni sul PC (solo quelle che autorizzi in `config.yaml`) e ricordare cose su di te.

**Costi:** voce e ascolto sono gratuiti (voci Microsoft e Whisper sul tuo PC). Si paga solo il cervello, cioè l'API di Claude. Con un uso normale (circa 50 richieste al giorno più qualche ricerca) si stimano **5-10 $ al mese**, con un blocco automatico a 30 $ (modificabile in `config.yaml`). Il comando `/consumi` su Telegram ti dice quanto hai speso.

---

## Installazione (una volta, ~30 minuti)

### 1. Python 3.11
Scaricalo da python.org (versione 3.11.x, Windows installer 64-bit) e durante l'installazione spunta **"Add python.exe to PATH"**.
Usa proprio la 3.11: la libreria della parola d'attivazione non funziona bene con le versioni più nuove.

### 2. Installa il progetto
Fai doppio clic su **`installa.bat`**. Scarica tutto da solo e crea il file `.env`.

### 3. Chiave di Claude
1. Vai su **platform.claude.com**, registrati e ricarica il credito (ne bastano 5-10 $).
2. Apri **API Keys → Create Key** e copia la chiave.
3. Apri il file `.env` con Blocco note e incollala in `ANTHROPIC_API_KEY=`.

### 4. Bot Telegram
1. Su Telegram cerca **@BotFather**, scrivi `/newbot`, scegli un nome e copia il token che ti dà.
2. Incolla il token in `TELEGRAM_BOT_TOKEN=` nel file `.env`.
3. Avvia l'assistente (passo 6), poi scrivi al tuo bot: ti risponde con il tuo ID.
4. Incolla l'ID in `TELEGRAM_ALLOWED_USER_ID=` e riavvia. Da quel momento il bot risponde **solo a te**.

### 5. Google Calendar e Tasks
1. Vai su **console.cloud.google.com** e crea un progetto (es. "assistente").
2. In **API e servizi → Libreria** attiva **Google Calendar API** e **Google Tasks API**.
3. In **Schermata consenso OAuth** scegli Esterno, compila nome ed email e, in **Utenti di test**, aggiungi `after.jymmy@gmail.com`.
4. In **Credenziali → Crea credenziali → ID client OAuth** scegli il tipo **App desktop**, poi scarica il JSON.
5. Rinomina il file in **`credentials.json`** e mettilo nella cartella del progetto.
6. Apri un terminale nella cartella e lancia:
   ```
   .venv\Scripts\activate
   python autorizza_google.py
   ```
   Si apre il browser: accetta (compare un avviso "app non verificata": è la tua, clicca Avanzate → Continua).
   L'autorizzazione con l'app in modalità test scade dopo circa 7 giorni. Per non doverla rifare, nella schermata consenso clicca **"Pubblica app"**: per uso personale non serve nessuna verifica.

### 6. Avvio
Doppio clic su **`avvia.bat`**. Si apre l'HUD nel browser e dopo qualche secondo senti "Jarvis online".
Il primo avvio è più lento perché scarica il modello Whisper (~500 MB).

**Per farlo partire all'accensione del PC:** premi Win+R, scrivi `shell:startup` e mettici un collegamento ad `avvia.bat`.

---

## Uso
- **A voce sul PC:** "Hey Jarvis" (senti un bip) → "Cosa ho domani?". Dopo la risposta resta in ascolto ancora qualche secondo, così puoi continuare senza ripetere il nome.
- **HUD** (http://127.0.0.1:8765): scrivi i comandi, clicca il reattore per parlare, premi Esc per zittirlo.
- **Telegram:** testo o vocali. Ai vocali risponde anche a voce. Comandi: `/voce`, `/consumi`, `/reset`.

Esempi:
- "Segnami il dentista giovedì alle 15, avvisami mezz'ora prima"
- "Aggiungi alle cose da fare: spedire il pacco Loot Drop entro venerdì"
- "Ricordami alle 18:30 di chiamare Ruben"
- "Fammi una ricerca approfondita sui prezzi del Game Boy Advance SP usato su eBay e Vinted"
- "Apri Chrome", "Mandami uno screenshot", "Blocca il PC"
- "Ricorda che il mio fornitore di joystick è …"

## Cambiare nome all'assistente
In `config.yaml` modifica `nome_assistente` (es. "Friday", "Edith", "Alfred"): cambiano il modo in cui si presenta e il titolo dell'HUD.
La **parola d'attivazione** è un'altra cosa: quella pronta all'uso è solo "hey jarvis". Per un nome diverso:
1. Addestra un modello gratis con il notebook Colab ufficiale di openWakeWord ("Training Custom Models"): scrivi la frase, ad esempio "hey friday", e dopo circa un'ora ottieni un file `.onnx`.
2. Metti il file nella cartella del progetto e scrivi in `config.yaml`: `wake_word: "hey_friday.onnx"`.

## Personalizzare
- **Voce:** `python main.py --voci` elenca le voci disponibili; poi cambia `voce_tts` in `config.yaml`.
- **Microfono:** `python main.py --microfoni` elenca i microfoni; poi metti il numero in `microfono:`.
- **Programmi e azioni sul PC:** aggiungili in `config.yaml` sotto `pc:`. L'assistente può eseguire **solo** quelli, nessun altro comando.
- **Prova senza microfono:** `python main.py --prova` apre una chat nel terminale.

## Se qualcosa non va
- **Non sente "Hey Jarvis":** abbassa `soglia_wake` a 0.3. Se si attiva da solo, alzala a 0.7.
- **La scheda video non viene usata:** va bene lo stesso, Whisper gira sul processore (un po' più lento). Puoi anche mettere `whisper_modello: "base"`.
- **Errore Google "token":** rilancia `python autorizza_google.py`.

## Struttura
```
main.py                 avvio
config.yaml             impostazioni
.env                    chiavi segrete
jarvis/agent.py         cervello: Claude + strumenti + agente di ricerca
jarvis/voice.py         parola d'attivazione, Whisper, voce
jarvis/telegram_bot.py  bot Telegram
jarvis/google_services.py  Calendar e Tasks
jarvis/hud.py + web/hud.html  interfaccia stile Iron Man
jarvis/store.py         memoria, promemoria, consumi (cartella data/)
```

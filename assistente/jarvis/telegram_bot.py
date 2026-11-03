"""Bot Telegram: scrivi o manda vocali dal telefono."""
import io
import tempfile
import traceback
from pathlib import Path

from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from .agent import testo_per_voce


class TelegramBot:
    def __init__(self, cfg, agent, stt, tts):
        self.cfg, self.agent, self.stt, self.tts = cfg, agent, stt, tts
        self.token = cfg["secrets"]["telegram_token"]
        u = cfg["secrets"]["telegram_user"]
        self.utente = int(u) if u.isdigit() else None
        self.app = None
        self.voce_sempre = False

    def _autorizzato(self, update: Update):
        return self.utente is not None and update.effective_user and update.effective_user.id == self.utente

    async def _non_autorizzato(self, update: Update):
        uid = update.effective_user.id if update.effective_user else "?"
        if self.utente is None:
            await update.message.reply_text(
                f"Il tuo ID Telegram è {uid}.\nScrivilo in TELEGRAM_ALLOWED_USER_ID nel file .env e riavvia.")
        # agli sconosciuti non rispondiamo nulla

    async def _rispondi(self, update: Update, testo: str, con_voce: bool):
        for i in range(0, len(testo), 4000):
            await update.message.reply_text(testo[i:i + 4000])
        if con_voce:
            try:
                ogg = await self.tts.vocale_telegram(testo_per_voce(testo)[:1500])
                await update.message.reply_voice(voice=io.BytesIO(ogg))
            except Exception as e:
                print(f"[telegram] vocale non inviato: {e}")

    async def on_testo(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if not self._autorizzato(update):
            return await self._non_autorizzato(update)
        await ctx.bot.send_chat_action(update.effective_chat.id, ChatAction.TYPING)
        risposta = await self.agent.chat(update.message.text, "telegram")
        await self._rispondi(update, risposta, self.voce_sempre)

    async def on_vocale(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if not self._autorizzato(update):
            return await self._non_autorizzato(update)
        await ctx.bot.send_chat_action(update.effective_chat.id, ChatAction.RECORD_VOICE)
        try:
            f = await (update.message.voice or update.message.audio).get_file()
            with tempfile.TemporaryDirectory() as d:
                p = Path(d) / "vocale.ogg"
                await f.download_to_drive(p)
                import asyncio
                testo = await asyncio.to_thread(self.stt.trascrivi, str(p))
        except Exception as e:
            traceback.print_exc()
            return await update.message.reply_text(f"Non sono riuscito a capire il vocale: {e}")
        if not testo:
            return await update.message.reply_text("Non ho sentito nulla nel vocale.")
        await update.message.reply_text(f"🎙️ «{testo}»")
        risposta = await self.agent.chat(testo, "telegram")
        await self._rispondi(update, risposta, self.cfg.get_path("telegram.rispondi_con_voce_ai_vocali", True))

    async def cmd_start(self, update: Update, ctx):
        if not self._autorizzato(update):
            return await self._non_autorizzato(update)
        await update.message.reply_text(
            f"{self.agent.nome} operativo, {self.cfg.get('appellativo')}.\n"
            "Scrivimi o mandami un vocale.\n/voce – rispondo sempre anche a voce (on/off)\n"
            "/consumi – spesa API del mese\n/reset – azzera la conversazione")

    async def cmd_voce(self, update: Update, ctx):
        if not self._autorizzato(update):
            return
        self.voce_sempre = not self.voce_sempre
        await update.message.reply_text(f"Risposte vocali sempre: {'attive' if self.voce_sempre else 'disattivate'}")

    async def cmd_consumi(self, update: Update, ctx):
        if not self._autorizzato(update):
            return
        from . import store
        m = store.consumi_mese()
        await update.message.reply_text(
            f"Questo mese: {m['usd']:.2f} $ su {self.cfg.get_path('budget.limite_mensile_usd')} $\n"
            f"Richieste: {m['richieste']} · Ricerche web: {m['ricerche_web']}")

    async def cmd_reset(self, update: Update, ctx):
        if not self._autorizzato(update):
            return
        self.agent.storie["telegram"] = []
        await update.message.reply_text("Conversazione azzerata.")

    # ------------- invii proattivi (promemoria, rapporti)
    async def invia(self, testo):
        if self.app and self.utente:
            for i in range(0, len(testo), 4000):
                await self.app.bot.send_message(self.utente, testo[i:i + 4000])

    async def invia_file(self, percorso):
        if self.app and self.utente:
            with open(percorso, "rb") as f:
                await self.app.bot.send_document(self.utente, f, filename=Path(percorso).name)

    async def invia_foto(self, percorso, didascalia=""):
        if self.app and self.utente:
            with open(percorso, "rb") as f:
                await self.app.bot.send_photo(self.utente, f, caption=didascalia)

    async def avvia(self):
        self.app = Application.builder().token(self.token).build()
        self.app.add_handler(CommandHandler("start", self.cmd_start))
        self.app.add_handler(CommandHandler("voce", self.cmd_voce))
        self.app.add_handler(CommandHandler("consumi", self.cmd_consumi))
        self.app.add_handler(CommandHandler("reset", self.cmd_reset))
        self.app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, self.on_vocale))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.on_testo))
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling(drop_pending_updates=True)
        print("[telegram] Bot attivo.")

    async def ferma(self):
        if self.app:
            await self.app.updater.stop()
            await self.app.stop()
            await self.app.shutdown()

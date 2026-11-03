"""Avvio dell'assistente personale.

    python main.py              avvia tutto (voce, Telegram, HUD)
    python main.py --solo-testo avvia senza microfono (solo HUD e Telegram)
    python main.py --voci       elenca le voci italiane disponibili
    python main.py --microfoni  elenca i microfoni
    python main.py --prova      chat da terminale per provare il cervello
"""
import argparse
import asyncio
import sys
import webbrowser
from datetime import datetime

from jarvis import store
from jarvis.agent import Agent
from jarvis.config import load_config


class Hub:
    """Collega i pezzi: HUD, Telegram e voce. Ogni parte è opzionale."""

    def __init__(self, loop):
        self.loop = loop
        self.hud = None
        self.tg = None
        self.voce = None

    def _hud(self, dati):
        if self.hud:
            asyncio.run_coroutine_threadsafe(self.hud.invia(dati), self.loop)

    def stato(self, valore, dettaglio=""):
        self._hud({"tipo": "stato", "valore": valore, "dettaglio": dettaglio})

    def messaggio(self, chi, testo):
        self._hud({"tipo": "msg", "chi": chi, "testo": testo})

    def parla(self, testo):
        if self.voce:
            from jarvis.agent import testo_per_voce
            self.voce.parla(testo_per_voce(testo))

    async def notifica(self, testo, parla=True):
        print(f"[notifica] {testo}")
        self.messaggio("assistente", testo)
        if parla:
            self.parla(testo)
        if self.tg:
            try:
                await self.tg.invia(testo)
            except Exception as e:
                print(f"[telegram] {e}")

    async def invia_file(self, p):
        if self.tg:
            await self.tg.invia_file(p)

    async def invia_foto(self, p, didascalia=""):
        if self.tg:
            await self.tg.invia_foto(p, didascalia)


async def ciclo_promemoria(cfg, hub):
    from zoneinfo import ZoneInfo

    tz = ZoneInfo(cfg.get("fuso_orario", "Europe/Rome"))
    while True:
        adesso = datetime.now(tz)
        for p in store.promemoria_lista():
            try:
                quando = datetime.fromisoformat(p["quando"])
            except ValueError:
                store.promemoria_rimuovi(p["id"])
                continue
            if quando <= adesso:
                store.promemoria_rimuovi(p["id"])
                await hub.notifica(f"⏰ {cfg.get('appellativo').capitalize()}, promemoria: {p['messaggio']}")
        await asyncio.sleep(20)


async def avvia(cfg, solo_testo=False):
    loop = asyncio.get_running_loop()
    hub = Hub(loop)
    agent = Agent(cfg, hub)
    stt = tts = None

    usa_voce = cfg.get_path("voce.attiva", True) and not solo_testo
    usa_tg = cfg.get_path("telegram.attivo", True) and cfg["secrets"]["telegram_token"]
    if usa_voce or usa_tg:
        from jarvis.voice import STT, TTS
        stt, tts = STT(cfg), TTS(cfg)

    if cfg.get_path("hud.attivo", True):
        from jarvis.hud import HUD
        hub.hud = HUD(cfg, agent)
        await hub.hud.avvia()
        if cfg.get_path("hud.apri_all_avvio", True):
            webbrowser.open(f"http://127.0.0.1:{hub.hud.porta}")

    if usa_tg:
        from jarvis.telegram_bot import TelegramBot
        hub.tg = TelegramBot(cfg, agent, stt, tts)
        await hub.tg.avvia()
    else:
        print("[telegram] disattivato (manca TELEGRAM_BOT_TOKEN nel .env)")

    if usa_voce:
        from jarvis.voice import VoiceEngine
        hub.voce = VoiceEngine(cfg, hub, agent, stt, tts, loop)
        if hub.hud:
            hub.hud.voce = hub.voce
        hub.voce.avvia()

    asyncio.create_task(ciclo_promemoria(cfg, hub))
    nome = cfg.get("nome_assistente", "Jarvis")
    print(f"\n=== {nome} online. Chiudi questa finestra per spegnerlo. ===\n")
    if hub.voce:
        hub.voce.parla(f"{nome} online. Sono a sua disposizione, {cfg.get('appellativo')}.")
    await asyncio.Event().wait()


async def prova_testo(cfg):
    class HubFinto:
        def stato(self, *a): pass
        def messaggio(self, *a): pass
        def parla(self, *a): pass
        async def notifica(self, t, parla=True): print("[notifica]", t)
        async def invia_file(self, p): print("[file]", p)
        async def invia_foto(self, p, d=""): print("[foto]", p)

    agent = Agent(cfg, HubFinto())
    print("Scrivi (vuoto per uscire):")
    while True:
        t = await asyncio.to_thread(input, "> ")
        if not t.strip():
            break
        print(await agent.chat(t, "telegram"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--solo-testo", action="store_true")
    ap.add_argument("--voci", action="store_true")
    ap.add_argument("--microfoni", action="store_true")
    ap.add_argument("--prova", action="store_true")
    a = ap.parse_args()

    if a.microfoni:
        import sounddevice as sd
        print(sd.query_devices())
        return
    if a.voci:
        import edge_tts
        voci = asyncio.run(edge_tts.list_voices())
        for v in voci:
            if v["Locale"].startswith("it") or "Multilingual" in v["ShortName"]:
                print(f'{v["ShortName"]:45} {v["Gender"]}')
        return

    cfg = load_config()
    if not cfg["secrets"]["anthropic"]:
        print("Manca ANTHROPIC_API_KEY nel file .env")
        sys.exit(1)
    try:
        asyncio.run(prova_testo(cfg) if a.prova else avvia(cfg, a.solo_testo))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()

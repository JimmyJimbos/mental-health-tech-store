"""HUD stile Iron Man nel browser (http://127.0.0.1:8765): stato, conversazione, scrivi o premi per parlare."""
import json

from aiohttp import WSMsgType, web

from .config import ROOT


class HUD:
    def __init__(self, cfg, agent):
        self.cfg, self.agent = cfg, agent
        self.porta = cfg.get_path("hud.porta", 8765)
        self.clients = set()
        self.voce = None  # VoiceEngine, impostato da main

    async def _index(self, req):
        html = (ROOT / "web" / "hud.html").read_text(encoding="utf-8")
        return web.Response(text=html.replace("{{NOME}}", self.agent.nome.upper()), content_type="text/html")

    async def _ws(self, req):
        ws = web.WebSocketResponse(heartbeat=30)
        await ws.prepare(req)
        self.clients.add(ws)
        try:
            async for msg in ws:
                if msg.type != WSMsgType.TEXT:
                    continue
                d = json.loads(msg.data)
                if d.get("tipo") == "testo" and d.get("testo", "").strip():
                    await self.invia({"tipo": "msg", "chi": "utente", "testo": d["testo"]})
                    await self.invia({"tipo": "stato", "valore": "pensa"})
                    r = await self.agent.chat(d["testo"], "pc")
                    await self.invia({"tipo": "msg", "chi": "assistente", "testo": r})
                    await self.invia({"tipo": "stato", "valore": "attesa"})
                    if d.get("leggi") and self.voce:
                        from .agent import testo_per_voce
                        self.voce.parla(testo_per_voce(r))
                elif d.get("tipo") == "ascolta" and self.voce:
                    self.voce.ascolta_ora.set()
                elif d.get("tipo") == "stop" and self.voce:
                    self.voce.ferma_voce.set()
        finally:
            self.clients.discard(ws)
        return ws

    async def invia(self, dati):
        morti = []
        for c in list(self.clients):
            try:
                await c.send_str(json.dumps(dati, ensure_ascii=False))
            except Exception:
                morti.append(c)
        for c in morti:
            self.clients.discard(c)

    async def avvia(self):
        app = web.Application()
        app.router.add_get("/", self._index)
        app.router.add_get("/ws", self._ws)
        runner = web.AppRunner(app)
        await runner.setup()
        await web.TCPSite(runner, "127.0.0.1", self.porta).start()
        print(f"[hud] http://127.0.0.1:{self.porta}")

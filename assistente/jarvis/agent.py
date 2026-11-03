"""Il cervello: Claude + strumenti (calendario, tasks, web, PC, memoria, agente di ricerca)."""
import asyncio
import json
import os
import re
import subprocess
import traceback
import webbrowser
from datetime import datetime
from zoneinfo import ZoneInfo

from anthropic import AsyncAnthropic

from . import store
from .config import DATA
from .google_services import Google

GIORNI = ["lunedì", "martedì", "mercoledì", "giovedì", "venerdì", "sabato", "domenica"]


def testo_per_voce(t: str) -> str:
    """Pulisce il markdown prima di leggerlo ad alta voce."""
    t = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", t)
    t = re.sub(r"https?://\S+", "", t)
    t = re.sub(r"[*_#`>|]", "", t)
    t = re.sub(r"\n\s*[-•]\s*", ". ", t)
    return re.sub(r"\s+", " ", t).strip()


class Agent:
    def __init__(self, cfg, hub):
        self.cfg = cfg
        self.hub = hub
        self.client = AsyncAnthropic(api_key=cfg["secrets"]["anthropic"])
        self.tz = ZoneInfo(cfg.get("fuso_orario", "Europe/Rome"))
        self.google = Google(cfg.get("fuso_orario", "Europe/Rome"))
        self.storie = {}            # cronologia per canale ("pc", "telegram")
        self.lock = {}
        self.ricerche_attive = {}
        self.nome = cfg.get("nome_assistente", "Jarvis")

    # ------------------------------------------------------------------ prompt
    def _system(self, canale):
        c = self.cfg
        statico = f"""Sei {self.nome}, l'assistente personale di {c.get('nome_utente')}, ispirato al J.A.R.V.I.S. di Iron Man.
Personalità: elegante, preciso, leale, con un'ironia britannica sottile e mai invadente. Chiami l'utente "{c.get('appellativo')}".
Parli sempre in italiano.

Regole:
- Vai dritto al punto. Per la voce rispondi in 1-3 frasi, senza elenchi lunghi, senza markdown, senza link.
- Usa gli strumenti invece di inventare: calendario, cose da fare, promemoria, ricerca web, PC.
- Per date relative ("domani alle 3", "venerdì") calcola la data esatta partendo dalla data di oggi qui sotto. Le 3 del pomeriggio = 15:00 se non è chiaro diversamente.
- Prima di cancellare eventi chiedi conferma, a meno che l'utente non sia stato esplicito.
- Per domande veloci di attualità usa la ricerca web. Per lavori lunghi (confronti, analisi, ricerche di mercato, "studiami", "cercami bene") avvia la ricerca approfondita: lavora in background e manda il rapporto su Telegram.
- Se l'utente ti dice qualcosa di duraturo su di sé ("ricorda che...") salvalo in memoria.
- Città dell'utente: {c.get('citta')}.
- Non dire mai che sei Claude o un modello: sei {self.nome}. Se ti chiedono come funzioni puoi dire che usi Claude di Anthropic come cervello."""
        ora = datetime.now(self.tz)
        mem = store.memoria_lista()
        mem_txt = "\n".join(f"{i+1}. {m['fatto']}" for i, m in enumerate(mem)) or "(vuota)"
        dinamico = (
            f"Adesso: {GIORNI[ora.weekday()]} {ora.strftime('%d/%m/%Y %H:%M')} (fuso {self.cfg.get('fuso_orario')}).\n"
            f"Canale: {'voce sul PC (risposte brevi e parlate)' if canale == 'pc' else 'Telegram (puoi usare un po più di testo)'}.\n"
            f"Memoria su {c.get('nome_utente')}:\n{mem_txt}"
        )
        return [
            {"type": "text", "text": statico, "cache_control": {"type": "ephemeral"}},
            {"type": "text", "text": dinamico},
        ]

    # ------------------------------------------------------------------ strumenti
    def _tools(self):
        prog = list((self.cfg.get_path("pc.programmi") or {}).keys())
        azioni = list((self.cfg.get_path("pc.azioni") or {}).keys())
        rw = self.cfg.get("ricerca_web", {})
        tools = [
            {"type": rw.get("tipo_strumento", "web_search_20260318"), "name": "web_search",
             "max_uses": rw.get("ricerche_max_per_risposta", 3),
             "user_location": {"type": "approximate", "city": self.cfg.get("citta", "Firenze"), "country": "IT"}},
            {"name": "calendario_eventi", "description": "Legge gli eventi del Google Calendar.",
             "input_schema": {"type": "object", "properties": {
                 "giorni_da_oggi": {"type": "integer", "description": "0=oggi, 1=domani, -1=ieri"},
                 "numero_giorni": {"type": "integer", "description": "quanti giorni leggere (default 1)"},
                 "cerca": {"type": "string", "description": "testo da cercare negli eventi (opzionale)"}},
                 "required": []}},
            {"name": "calendario_crea", "description": "Crea un evento sul Google Calendar.",
             "input_schema": {"type": "object", "properties": {
                 "titolo": {"type": "string"},
                 "inizio": {"type": "string", "description": "ISO locale, es. 2026-11-05T15:00 oppure 2026-11-05 per tutto il giorno"},
                 "fine": {"type": "string", "description": "ISO locale, opzionale"},
                 "durata_minuti": {"type": "integer"},
                 "luogo": {"type": "string"}, "descrizione": {"type": "string"},
                 "promemoria_minuti": {"type": "integer", "description": "notifica sul telefono X minuti prima"}},
                 "required": ["titolo", "inizio"]}},
            {"name": "calendario_elimina", "description": "Elimina un evento (serve l'id da calendario_eventi).",
             "input_schema": {"type": "object", "properties": {"id_evento": {"type": "string"}}, "required": ["id_evento"]}},
            {"name": "tasks_lista", "description": "Elenca le cose da fare (Google Tasks).",
             "input_schema": {"type": "object", "properties": {}, "required": []}},
            {"name": "tasks_aggiungi", "description": "Aggiunge una cosa da fare a Google Tasks.",
             "input_schema": {"type": "object", "properties": {
                 "titolo": {"type": "string"}, "scadenza": {"type": "string", "description": "YYYY-MM-DD"},
                 "note": {"type": "string"}}, "required": ["titolo"]}},
            {"name": "tasks_completa", "description": "Segna come fatta una cosa da fare (id da tasks_lista).",
             "input_schema": {"type": "object", "properties": {"id_task": {"type": "string"}}, "required": ["id_task"]}},
            {"name": "promemoria_imposta",
             "description": "Promemoria a un orario preciso: te lo dico a voce sul PC e ti scrivo su Telegram.",
             "input_schema": {"type": "object", "properties": {
                 "quando": {"type": "string", "description": "ISO locale, es. 2026-11-03T18:30"},
                 "messaggio": {"type": "string"}}, "required": ["quando", "messaggio"]}},
            {"name": "promemoria_lista", "description": "Elenca i promemoria attivi.",
             "input_schema": {"type": "object", "properties": {}, "required": []}},
            {"name": "promemoria_cancella", "description": "Cancella un promemoria per id.",
             "input_schema": {"type": "object", "properties": {"id": {"type": "integer"}}, "required": ["id"]}},
            {"name": "ricerca_approfondita",
             "description": "Avvia in background un agente di ricerca che cerca a fondo sul web e manda un rapporto su Telegram. Usalo per richieste che richiedono molte fonti.",
             "input_schema": {"type": "object", "properties": {
                 "argomento": {"type": "string"},
                 "istruzioni": {"type": "string", "description": "cosa deve contenere il rapporto, vincoli, formato"}},
                 "required": ["argomento"]}},
            {"name": "memoria_salva", "description": "Salva un fatto duraturo sull'utente.",
             "input_schema": {"type": "object", "properties": {"fatto": {"type": "string"}}, "required": ["fatto"]}},
            {"name": "memoria_elimina", "description": "Elimina il fatto numero N dalla memoria.",
             "input_schema": {"type": "object", "properties": {"numero": {"type": "integer"}}, "required": ["numero"]}},
            {"name": "consumi_mese", "description": "Quanto è stato speso questo mese in API.",
             "input_schema": {"type": "object", "properties": {}, "required": []}},
            {"name": "pc_apri_sito", "description": "Apre un sito nel browser del PC.",
             "input_schema": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}},
            {"name": "pc_screenshot", "description": "Fa uno screenshot del PC e lo manda su Telegram.",
             "input_schema": {"type": "object", "properties": {}, "required": []}},
        ]
        if prog:
            tools.append({"name": "pc_apri_programma", "description": "Apre un programma sul PC.",
                          "input_schema": {"type": "object", "properties": {"nome": {"type": "string", "enum": prog}},
                                           "required": ["nome"]}})
        if azioni:
            tools.append({"name": "pc_azione", "description": "Esegue un'azione consentita sul PC.",
                          "input_schema": {"type": "object", "properties": {"nome": {"type": "string", "enum": azioni}},
                                           "required": ["nome"]}})
        return tools

    async def _esegui(self, nome, a):
        g = self.google
        if nome == "calendario_eventi":
            return await asyncio.to_thread(g.eventi, a.get("giorni_da_oggi", 0), a.get("numero_giorni", 1), a.get("cerca"))
        if nome == "calendario_crea":
            return await asyncio.to_thread(g.crea_evento, a["titolo"], a["inizio"], a.get("fine"),
                                           a.get("durata_minuti", 60), a.get("luogo"), a.get("descrizione"),
                                           a.get("promemoria_minuti"))
        if nome == "calendario_elimina":
            await asyncio.to_thread(g.elimina_evento, a["id_evento"])
            return "eliminato"
        if nome == "tasks_lista":
            return await asyncio.to_thread(g.lista_tasks)
        if nome == "tasks_aggiungi":
            return await asyncio.to_thread(g.aggiungi_task, a["titolo"], a.get("scadenza"), a.get("note"))
        if nome == "tasks_completa":
            await asyncio.to_thread(g.completa_task, a["id_task"])
            return "completato"
        if nome == "promemoria_imposta":
            q = datetime.fromisoformat(a["quando"])
            if q.tzinfo is None:
                q = q.replace(tzinfo=self.tz)
            pid = store.promemoria_aggiungi(q.isoformat(), a["messaggio"])
            return {"id": pid, "quando": q.strftime("%d/%m %H:%M")}
        if nome == "promemoria_lista":
            return store.promemoria_lista()
        if nome == "promemoria_cancella":
            return "cancellato" if store.promemoria_rimuovi(int(a["id"])) else "non trovato"
        if nome == "ricerca_approfondita":
            return self.avvia_ricerca(a["argomento"], a.get("istruzioni", ""))
        if nome == "memoria_salva":
            return f"salvato come numero {store.memoria_aggiungi(a['fatto'])}"
        if nome == "memoria_elimina":
            t = store.memoria_elimina(int(a["numero"]))
            return f"eliminato: {t}" if t else "numero non valido"
        if nome == "consumi_mese":
            m = store.consumi_mese()
            m["limite_usd"] = self.cfg.get_path("budget.limite_mensile_usd")
            return m
        if nome == "pc_apri_sito":
            url = a["url"] if a["url"].startswith("http") else "https://" + a["url"]
            webbrowser.open(url)
            return "aperto"
        if nome == "pc_apri_programma":
            cmd = self.cfg.get_path("pc.programmi", {})[a["nome"]]
            subprocess.Popen(os.path.expandvars(cmd), shell=True)
            return "aperto"
        if nome == "pc_azione":
            cmd = self.cfg.get_path("pc.azioni", {})[a["nome"]]
            subprocess.Popen(os.path.expandvars(cmd), shell=True)
            return "eseguito"
        if nome == "pc_screenshot":
            from PIL import ImageGrab
            p = DATA / "screenshot.png"
            await asyncio.to_thread(lambda: ImageGrab.grab(all_screens=True).save(p))
            await self.hub.invia_foto(p, "Ecco il suo schermo.")
            return "screenshot inviato su Telegram"
        return f"strumento sconosciuto: {nome}"

    # ------------------------------------------------------------------ costi
    def _registra(self, model, usage):
        prezzi = self.cfg.get_path("budget.prezzi_usd_per_milione", {}).get(model, {"input": 0, "output": 0})
        tin = (usage.input_tokens or 0) + (getattr(usage, "cache_creation_input_tokens", 0) or 0) * 1.25 \
            + (getattr(usage, "cache_read_input_tokens", 0) or 0) * 0.1
        tout = usage.output_tokens or 0
        stu = getattr(usage, "server_tool_use", None)
        ricerche = (getattr(stu, "web_search_requests", 0) or 0) if stu else 0
        costo = tin / 1e6 * prezzi["input"] + tout / 1e6 * prezzi["output"] \
            + ricerche * self.cfg.get_path("budget.costo_ricerca_web_usd", 0.01)
        store.consumi_registra(costo, model, int(tin), int(tout), ricerche)

    def _oltre_budget(self):
        return store.consumi_mese()["usd"] >= self.cfg.get_path("budget.limite_mensile_usd", 30)

    # ------------------------------------------------------------------ chat
    def _taglia_storia(self, storia, massimo=30):
        if len(storia) <= massimo:
            return storia
        for i in range(len(storia) - massimo, len(storia)):
            m = storia[i]
            if m["role"] == "user" and isinstance(m["content"], str):
                return storia[i:]
        return storia[-2:]

    async def chat(self, testo: str, canale: str = "pc") -> str:
        lock = self.lock.setdefault(canale, asyncio.Lock())
        async with lock:
            try:
                return await self._chat(testo, canale)
            except Exception as e:
                traceback.print_exc()
                return f"Mi scusi {self.cfg.get('appellativo')}, ho avuto un problema: {e}"

    async def _chat(self, testo, canale):
        storia = self._taglia_storia(self.storie.setdefault(canale, []))
        storia.append({"role": "user", "content": testo})
        model = self.cfg.get_path("modelli.veloce", "claude-haiku-5-5")
        extra = {}
        eff = self.cfg.get_path("modelli.effort_veloce")
        if eff:
            extra["output_config"] = {"effort": eff}
        for _ in range(10):
            r = await self.client.messages.create(
                model=model, max_tokens=2000, system=self._system(canale),
                tools=self._tools(), messages=storia, **extra)
            self._registra(model, r.usage)
            storia.append({"role": "assistant", "content": r.content})
            if r.stop_reason == "pause_turn":
                continue
            if r.stop_reason != "tool_use":
                break
            risultati = []
            for b in r.content:
                if b.type != "tool_use":
                    continue
                self.hub.stato("strumento", b.name)
                try:
                    out = await self._esegui(b.name, b.input)
                    risultati.append({"type": "tool_result", "tool_use_id": b.id,
                                      "content": json.dumps(out, ensure_ascii=False, default=str)})
                except Exception as e:
                    risultati.append({"type": "tool_result", "tool_use_id": b.id,
                                      "content": f"Errore: {e}", "is_error": True})
            storia.append({"role": "user", "content": risultati})
        self.storie[canale] = storia
        testo_finale = "".join(b.text for b in r.content if b.type == "text").strip()
        return testo_finale or "Fatto."

    # ------------------------------------------------------------------ agente di ricerca
    def avvia_ricerca(self, argomento, istruzioni):
        if self._oltre_budget():
            return "Budget mensile raggiunto: ricerca approfondita non avviata."
        rid = len(self.ricerche_attive) + 1
        self.ricerche_attive[rid] = asyncio.create_task(self._ricerca(rid, argomento, istruzioni))
        return f"Ricerca n.{rid} avviata in background, ci vorrà qualche minuto. Il rapporto arriverà su Telegram."

    async def _ricerca(self, rid, argomento, istruzioni):
        model = self.cfg.get_path("modelli.ricerca", "claude-sonnet-5-5")
        rw = self.cfg.get("ricerca_web", {})
        oggi = datetime.now(self.tz).strftime("%d/%m/%Y")
        prompt = (f"Oggi è il {oggi}. Fai una ricerca approfondita sul web su: {argomento}\n"
                  f"Istruzioni dell'utente: {istruzioni or 'nessuna'}\n\n"
                  "Cerca più fonti, confrontale e scrivi in italiano un rapporto chiaro e concreto in markdown: "
                  "inizia con un riassunto di 3 righe, poi i dettagli, numeri e prezzi con la data della fonte, "
                  "e alla fine l'elenco delle fonti con i link. Se qualcosa non è verificabile dillo.")
        msgs = [{"role": "user", "content": prompt}]
        tools = [{"type": rw.get("tipo_strumento", "web_search_20260318"), "name": "web_search",
                  "max_uses": rw.get("ricerche_max_agente", 10)}]
        try:
            for _ in range(6):
                r = await self.client.messages.create(model=model, max_tokens=8000, tools=tools, messages=msgs)
                self._registra(model, r.usage)
                if r.stop_reason == "pause_turn":
                    msgs.append({"role": "assistant", "content": r.content})
                    continue
                break
            testo = "".join(b.text for b in r.content if b.type == "text").strip()
            nome_file = re.sub(r"[^\w]+", "_", argomento.lower())[:50]
            p = DATA / "report" / f"{datetime.now():%Y%m%d_%H%M}_{nome_file}.md"
            p.write_text(f"# {argomento}\n\n{testo}", encoding="utf-8")
            riassunto = testo.split("\n\n")[0][:600]
            await self.hub.notifica(f"📑 Ricerca completata: {argomento}\n\n{riassunto}", parla=False)
            await self.hub.invia_file(p)
            self.hub.parla(f"{self.cfg.get('appellativo').capitalize()}, la ricerca su {argomento} è pronta. Le ho mandato il rapporto su Telegram.")
        except Exception as e:
            traceback.print_exc()
            await self.hub.notifica(f"La ricerca su {argomento} non è riuscita: {e}")

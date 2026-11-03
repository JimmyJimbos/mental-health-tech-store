"""Voce: parola d'attivazione, ascolto (Whisper), sintesi vocale (Edge TTS) e riproduzione."""
import asyncio
import io
import os
import queue
import sys
import threading
import time
from pathlib import Path

import av
import numpy as np

SR = 16000
BLOCCO = 1280  # 80 ms, quello che si aspetta openWakeWord


# ============================================================ audio utils
def decodifica_audio(dati: bytes, rate=24000) -> np.ndarray:
    """mp3/ogg -> int16 mono."""
    c = av.open(io.BytesIO(dati))
    res = av.AudioResampler(format="s16", layout="mono", rate=rate)
    pezzi = []
    for frame in c.decode(audio=0):
        for f in res.resample(frame):
            pezzi.append(f.to_ndarray().reshape(-1))
    for f in res.resample(None):
        pezzi.append(f.to_ndarray().reshape(-1))
    c.close()
    return np.concatenate(pezzi) if pezzi else np.zeros(0, dtype=np.int16)


def codifica_ogg_opus(pcm: np.ndarray, rate: int) -> bytes:
    """int16 mono -> OGG/Opus (formato dei vocali di Telegram)."""
    out = io.BytesIO()
    c = av.open(out, mode="w", format="ogg")
    s = c.add_stream("libopus", rate=48000)
    s.layout = "mono"
    frame = av.AudioFrame.from_ndarray(pcm.reshape(1, -1).astype(np.int16), format="s16", layout="mono")
    frame.sample_rate = rate
    res = av.AudioResampler(format="s16", layout="mono", rate=48000)
    for f in list(res.resample(frame)) + list(res.resample(None)):
        for p in s.encode(f):
            c.mux(p)
    for p in s.encode(None):
        c.mux(p)
    c.close()
    return out.getvalue()


def bip(freq=880, dur=0.12, rate=24000, vol=0.25):
    t = np.linspace(0, dur, int(rate * dur), endpoint=False)
    env = np.minimum(1, np.minimum(t, dur - t) * 40)
    return (np.sin(2 * np.pi * freq * t) * env * vol * 32767).astype(np.int16)


# ============================================================ TTS
class TTS:
    def __init__(self, cfg):
        v = cfg.get("voce", {})
        self.voce = v.get("voce_tts", "it-IT-DiegoNeural")
        self.velocita = v.get("velocita", "+0%")
        self.tono = v.get("tono", "+0Hz")

    async def sintetizza(self, testo: str) -> bytes:
        import edge_tts

        comm = edge_tts.Communicate(testo, self.voce, rate=self.velocita, pitch=self.tono)
        buf = bytearray()
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                buf.extend(chunk["data"])
        return bytes(buf)

    async def pcm(self, testo: str):
        mp3 = await self.sintetizza(testo)
        return decodifica_audio(mp3, 24000), 24000

    async def vocale_telegram(self, testo: str) -> bytes:
        pcm, rate = await self.pcm(testo)
        return await asyncio.to_thread(codifica_ogg_opus, pcm, rate)


# ============================================================ STT
def _aggiungi_dll_cuda():
    """Su Windows rende visibili le DLL CUDA installate via pip (nvidia-cublas-cu12, nvidia-cudnn-cu12)."""
    if sys.platform != "win32":
        return
    import site

    for base in site.getsitepackages() + [site.getusersitepackages()]:
        nv = Path(base) / "nvidia"
        if nv.exists():
            for b in nv.glob("*/bin"):
                os.add_dll_directory(str(b))
                os.environ["PATH"] = str(b) + os.pathsep + os.environ["PATH"]


class STT:
    def __init__(self, cfg):
        v = cfg.get("voce", {})
        self.dim = v.get("whisper_modello", "small")
        self.disp = v.get("whisper_dispositivo", "auto")
        self.model = None
        self.lock = threading.Lock()

    def carica(self):
        if self.model is not None:
            return
        from faster_whisper import WhisperModel

        tentativi = []
        if self.disp in ("auto", "cuda"):
            _aggiungi_dll_cuda()
            tentativi.append(("cuda", "float16"))
        if self.disp in ("auto", "cpu"):
            tentativi.append(("cpu", "int8"))
        for dev, ct in tentativi:
            try:
                m = WhisperModel(self.dim, device=dev, compute_type=ct)
                list(m.transcribe(np.zeros(SR, dtype=np.float32), language="it")[0])  # prova vera
                self.model = m
                print(f"[voce] Whisper '{self.dim}' caricato su {dev}")
                return
            except Exception as e:
                print(f"[voce] Whisper su {dev} non disponibile: {e}")
        raise RuntimeError("Impossibile caricare Whisper")

    def trascrivi(self, audio) -> str:
        """audio: np.float32 a 16 kHz oppure percorso/file (es. vocale Telegram)."""
        self.carica()
        with self.lock:
            segs, _ = self.model.transcribe(audio, language="it", vad_filter=True, beam_size=5)
            return " ".join(s.text.strip() for s in segs).strip()


# ============================================================ motore vocale del PC
class VoiceEngine:
    """Thread che ascolta il microfono: parola d'attivazione -> registra -> trascrive -> risponde."""

    def __init__(self, cfg, hub, agent, stt: STT, tts: TTS, loop):
        self.cfg, self.hub, self.agent, self.stt, self.tts, self.loop = cfg, hub, agent, stt, tts, loop
        v = cfg.get("voce", {})
        self.soglia = v.get("soglia_wake", 0.5)
        self.ww = v.get("wake_word", "hey_jarvis")
        self.continua = v.get("conversazione_continua", True)
        self.mic = v.get("microfono")
        self.coda_parla = queue.Queue()
        self.sta_parlando = threading.Event()
        self.ascolta_ora = threading.Event()   # pulsante "parla" dell'HUD
        self.ferma_voce = threading.Event()
        self.audio_q = queue.Queue()
        self.attivo = True

    # ---------------- parlato
    def parla(self, testo: str):
        self.coda_parla.put(testo)

    def _thread_parlato(self):
        import sounddevice as sd

        while self.attivo:
            testo = self.coda_parla.get()
            testo = testo.strip()
            if not testo:
                continue
            try:
                fut = asyncio.run_coroutine_threadsafe(self.tts.pcm(testo), self.loop)
                pcm, rate = fut.result(timeout=60)
                self.sta_parlando.set()
                self.ferma_voce.clear()
                self.hub.stato("parla")
                sd.play(pcm, rate)
                durata = len(pcm) / rate
                t0 = time.time()
                while time.time() - t0 < durata + 0.2:
                    if self.ferma_voce.is_set():
                        sd.stop()
                        break
                    time.sleep(0.05)
            except Exception as e:
                print(f"[voce] errore sintesi: {e}")
            finally:
                time.sleep(0.3)
                if self.coda_parla.empty():
                    self.sta_parlando.clear()
                    self.hub.stato("attesa")

    def _suona(self, pcm, rate=24000):
        import sounddevice as sd

        sd.play(pcm, rate)
        sd.wait()

    # ---------------- ascolto
    def _callback(self, indata, frames, t, status):
        self.audio_q.put(indata[:, 0].copy())

    def _registra_frase(self, attesa_max=6.0, durata_max=20.0):
        """Registra finché l'utente parla; si ferma dopo ~1 s di silenzio."""
        pezzi, iniziato, silenzio, t0 = [], False, 0.0, time.time()
        # stima del rumore di fondo
        rumore = 300.0
        while True:
            try:
                b = self.audio_q.get(timeout=1)
            except queue.Empty:
                continue
            rms = float(np.sqrt(np.mean(b.astype(np.float32) ** 2)))
            if not iniziato:
                rumore = 0.9 * rumore + 0.1 * rms
                if rms > max(500, rumore * 2.5):
                    iniziato = True
                    pezzi.append(b)
                elif time.time() - t0 > attesa_max:
                    return None
                continue
            pezzi.append(b)
            silenzio = silenzio + len(b) / SR if rms < max(400, rumore * 1.8) else 0.0
            if silenzio > 1.0 or time.time() - t0 > durata_max:
                break
        audio = np.concatenate(pezzi).astype(np.float32) / 32768.0
        return audio

    def _svuota_coda(self):
        while not self.audio_q.empty():
            try:
                self.audio_q.get_nowait()
            except queue.Empty:
                break

    def _turno(self, attesa_max=6.0):
        """Un giro di domanda/risposta. Ritorna True se l'utente ha parlato."""
        self.hub.stato("ascolto")
        audio = self._registra_frase(attesa_max=attesa_max)
        if audio is None:
            self.hub.stato("attesa")
            return False
        self.hub.stato("pensa")
        testo = self.stt.trascrivi(audio)
        if len(testo) < 2:
            self.hub.stato("attesa")
            return False
        print(f"[tu] {testo}")
        self.hub.messaggio("utente", testo)
        fut = asyncio.run_coroutine_threadsafe(self.agent.chat(testo, "pc"), self.loop)
        risposta = fut.result(timeout=300)
        print(f"[{self.agent.nome}] {risposta}")
        self.hub.messaggio("assistente", risposta)
        from .agent import testo_per_voce

        self.parla(testo_per_voce(risposta))
        time.sleep(0.5)
        while self.sta_parlando.is_set():
            time.sleep(0.1)
        self._svuota_coda()
        return True

    def _carica_wakeword(self):
        import openwakeword
        from openwakeword.model import Model

        if self.ww.endswith(".onnx"):
            return Model(wakeword_models=[self.ww], inference_framework="onnx"), Path(self.ww).stem
        try:
            openwakeword.utils.download_models(model_names=[self.ww])
        except Exception as e:
            print(f"[voce] download modelli wake word: {e}")
        return Model(wakeword_models=[self.ww], inference_framework="onnx"), self.ww

    def _thread_ascolto(self):
        import sounddevice as sd

        try:
            self.stt.carica()
            modello, chiave = self._carica_wakeword()
        except Exception as e:
            print(f"[voce] Voce disattivata: {e}")
            self.hub.stato("errore", str(e))
            return
        print(f"[voce] Pronto. Di' \"{chiave.replace('_', ' ')}\" per parlarmi.")
        with sd.InputStream(samplerate=SR, channels=1, dtype="int16", blocksize=BLOCCO,
                            device=self.mic, callback=self._callback):
            self.hub.stato("attesa")
            while self.attivo:
                try:
                    b = self.audio_q.get(timeout=0.5)
                except queue.Empty:
                    b = None
                if self.sta_parlando.is_set():
                    continue  # non ascoltare mentre parla (evita di sentirsi da solo)
                attivato = self.ascolta_ora.is_set()
                if b is not None and not attivato:
                    punteggi = modello.predict(b)
                    attivato = max(punteggi.values()) >= self.soglia
                if not attivato:
                    continue
                self.ascolta_ora.clear()
                modello.reset()
                self._svuota_coda()
                self._suona(bip(880), 24000)
                try:
                    if self._turno() and self.continua:
                        while self._turno(attesa_max=4.0):
                            pass
                except Exception as e:
                    print(f"[voce] errore: {e}")
                    self.hub.stato("attesa")
                modello.reset()
                self._svuota_coda()

    def avvia(self):
        threading.Thread(target=self._thread_parlato, daemon=True).start()
        threading.Thread(target=self._thread_ascolto, daemon=True).start()

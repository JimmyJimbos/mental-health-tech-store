"""Piccoli archivi su file JSON: memoria a lungo termine, consumi, promemoria."""
import json
import threading
from datetime import datetime

from .config import DATA

_lock = threading.Lock()


def _load(name, default):
    p = DATA / name
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default


def _save(name, data):
    p = DATA / name
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(p)


# ---------------- memoria a lungo termine ----------------
def memoria_lista():
    return _load("memoria.json", [])


def memoria_aggiungi(fatto: str):
    with _lock:
        m = memoria_lista()
        m.append({"fatto": fatto.strip(), "data": datetime.now().strftime("%Y-%m-%d")})
        _save("memoria.json", m)
        return len(m)


def memoria_elimina(numero: int):
    with _lock:
        m = memoria_lista()
        if 1 <= numero <= len(m):
            tolto = m.pop(numero - 1)
            _save("memoria.json", m)
            return tolto["fatto"]
        return None


# ---------------- consumi API ----------------
def _mese():
    return datetime.now().strftime("%Y-%m")


def consumi_registra(costo_usd: float, modello: str, tin: int, tout: int, ricerche: int):
    with _lock:
        c = _load("consumi.json", {})
        m = c.setdefault(_mese(), {"usd": 0.0, "richieste": 0, "ricerche_web": 0, "token_in": 0, "token_out": 0})
        m["usd"] = round(m["usd"] + costo_usd, 5)
        m["richieste"] += 1
        m["ricerche_web"] += ricerche
        m["token_in"] += tin
        m["token_out"] += tout
        _save("consumi.json", c)


def consumi_mese():
    return _load("consumi.json", {}).get(
        _mese(), {"usd": 0.0, "richieste": 0, "ricerche_web": 0, "token_in": 0, "token_out": 0}
    )


# ---------------- promemoria ----------------
def promemoria_lista():
    return _load("promemoria.json", [])


def promemoria_aggiungi(quando_iso: str, messaggio: str):
    with _lock:
        p = promemoria_lista()
        nuovo_id = max([x["id"] for x in p], default=0) + 1
        p.append({"id": nuovo_id, "quando": quando_iso, "messaggio": messaggio})
        _save("promemoria.json", p)
        return nuovo_id


def promemoria_rimuovi(pid: int):
    with _lock:
        p = promemoria_lista()
        nuovi = [x for x in p if x["id"] != pid]
        _save("promemoria.json", nuovi)
        return len(nuovi) != len(p)

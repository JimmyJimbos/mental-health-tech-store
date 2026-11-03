"""Google Calendar e Google Tasks.

La prima volta va eseguito `python autorizza_google.py`, che apre il browser
per il consenso e salva data/google_token.json.
"""
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from .config import DATA, ROOT

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/tasks",
]
TOKEN = DATA / "google_token.json"
CREDENTIALS = ROOT / "credentials.json"


def autorizza_interattivo():
    from google_auth_oauthlib.flow import InstalledAppFlow

    flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS), SCOPES)
    creds = flow.run_local_server(port=0, prompt="consent")
    TOKEN.write_text(creds.to_json(), encoding="utf-8")
    return creds


class Google:
    def __init__(self, tz: str):
        self.tz = ZoneInfo(tz)
        self.tz_name = tz
        self._cal = None
        self._tasks = None

    # -------- connessione --------
    def _creds(self):
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials

        if not TOKEN.exists():
            raise RuntimeError("Google non autorizzato: esegui 'python autorizza_google.py' una volta.")
        creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
        if not creds.valid:
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                TOKEN.write_text(creds.to_json(), encoding="utf-8")
            else:
                raise RuntimeError("Autorizzazione Google scaduta: riesegui 'python autorizza_google.py'.")
        return creds

    def cal(self):
        if self._cal is None:
            from googleapiclient.discovery import build

            self._cal = build("calendar", "v3", credentials=self._creds(), cache_discovery=False)
        return self._cal

    def tasks(self):
        if self._tasks is None:
            from googleapiclient.discovery import build

            self._tasks = build("tasks", "v1", credentials=self._creds(), cache_discovery=False)
        return self._tasks

    # -------- calendario --------
    def eventi(self, giorni_da_oggi: int = 0, numero_giorni: int = 1, cerca: str = None):
        oggi = datetime.now(self.tz).replace(hour=0, minute=0, second=0, microsecond=0)
        inizio = oggi + timedelta(days=giorni_da_oggi)
        fine = inizio + timedelta(days=max(1, numero_giorni))
        params = dict(
            calendarId="primary", timeMin=inizio.isoformat(), timeMax=fine.isoformat(),
            singleEvents=True, orderBy="startTime", maxResults=50,
        )
        if cerca:
            params["q"] = cerca
        res = self.cal().events().list(**params).execute()
        out = []
        for e in res.get("items", []):
            s = e["start"].get("dateTime", e["start"].get("date"))
            f = e["end"].get("dateTime", e["end"].get("date"))
            out.append({
                "id": e["id"], "titolo": e.get("summary", "(senza titolo)"),
                "inizio": s, "fine": f, "luogo": e.get("location", ""),
            })
        return out

    def crea_evento(self, titolo, inizio, fine=None, durata_minuti=60, luogo=None,
                    descrizione=None, promemoria_minuti=None, tutto_il_giorno=False):
        body = {"summary": titolo}
        if luogo:
            body["location"] = luogo
        if descrizione:
            body["description"] = descrizione
        if tutto_il_giorno or len(inizio) == 10:
            d = datetime.fromisoformat(inizio[:10]).date()
            d_fine = datetime.fromisoformat(fine[:10]).date() + timedelta(days=1) if fine else d + timedelta(days=1)
            body["start"] = {"date": d.isoformat()}
            body["end"] = {"date": d_fine.isoformat()}
        else:
            s = datetime.fromisoformat(inizio)
            if s.tzinfo is None:
                s = s.replace(tzinfo=self.tz)
            if fine:
                f = datetime.fromisoformat(fine)
                if f.tzinfo is None:
                    f = f.replace(tzinfo=self.tz)
            else:
                f = s + timedelta(minutes=durata_minuti or 60)
            body["start"] = {"dateTime": s.isoformat(), "timeZone": self.tz_name}
            body["end"] = {"dateTime": f.isoformat(), "timeZone": self.tz_name}
        if promemoria_minuti is not None:
            body["reminders"] = {"useDefault": False,
                                 "overrides": [{"method": "popup", "minutes": int(promemoria_minuti)}]}
        e = self.cal().events().insert(calendarId="primary", body=body).execute()
        return {"id": e["id"], "link": e.get("htmlLink"), "titolo": titolo}

    def elimina_evento(self, id_evento):
        self.cal().events().delete(calendarId="primary", eventId=id_evento).execute()
        return True

    # -------- tasks --------
    def lista_tasks(self, includi_completati=False):
        res = self.tasks().tasks().list(tasklist="@default", showCompleted=includi_completati,
                                        maxResults=100).execute()
        out = []
        for t in res.get("items", []):
            out.append({"id": t["id"], "titolo": t.get("title", ""),
                        "scadenza": (t.get("due") or "")[:10], "note": t.get("notes", ""),
                        "stato": t.get("status")})
        return out

    def aggiungi_task(self, titolo, scadenza=None, note=None):
        body = {"title": titolo}
        if scadenza:
            body["due"] = f"{scadenza[:10]}T00:00:00.000Z"
        if note:
            body["notes"] = note
        t = self.tasks().tasks().insert(tasklist="@default", body=body).execute()
        return {"id": t["id"], "titolo": titolo}

    def completa_task(self, id_task):
        self.tasks().tasks().patch(tasklist="@default", task=id_task, body={"status": "completed"}).execute()
        return True

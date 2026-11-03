"""Da eseguire UNA volta: collega il tuo Google Calendar e Google Tasks."""
from jarvis.google_services import CREDENTIALS, Google, autorizza_interattivo

if not CREDENTIALS.exists():
    print("Manca credentials.json nella cartella del progetto (vedi README, passo Google).")
    raise SystemExit(1)

autorizza_interattivo()
g = Google("Europe/Rome")
eventi = g.eventi(0, 7)
print(f"Collegato! Eventi nei prossimi 7 giorni: {len(eventi)}")
for e in eventi[:5]:
    print(" -", e["inizio"], e["titolo"])
print(f"Cose da fare aperte: {len(g.lista_tasks())}")

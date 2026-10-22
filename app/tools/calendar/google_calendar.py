import datetime
import os
from pathlib import Path

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()

# Si tu modifies les scopes, supprime token.json pour te reconnecter.
SCOPES = [os.getenv("GOOGLE_SCOPES")]

# Chemins basés sur l'emplacement de ce fichier : ça marche quel que soit
# le dossier depuis lequel on lance le programme.
BASE_DIR = Path(__file__).parent
CREDENTIALS_FILE = BASE_DIR / "credentials.json"
TOKEN_FILE = BASE_DIR / "token.json"


def get_service():
    """Crée un client connecté à l'API Google Calendar.

    Fonction interne : ce n'est pas un outil pour le modèle (il ne peut pas
    manipuler un objet Python). Les outils l'appellent eux-mêmes.

    - Si token.json existe et est valide, il est réutilisé.
    - S'il a expiré, il est rafraîchi automatiquement.
    - Sinon, une page de connexion Google s'ouvre dans le navigateur,
      puis le nouveau token est enregistré dans token.json.

    Returns:
        Le service Google Calendar (googleapiclient Resource).
    """
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_FILE.write_text(creds.to_json())

    return build("calendar", "v3", credentials=creds)


def get_upcoming_events(max_results: int = 10) -> str:
    """Récupère les prochains événements de l'agenda Google principal.

    Outil exposé au modèle (voir tools/TOOLS.py).

    Args:
        max_results: Nombre maximum d'événements à renvoyer (1 à 50, 10 par défaut).

    Returns:
        Un texte lisible, un événement par ligne : "<début> - <titre>".
        En cas de problème, un message commençant par "Erreur".
    """
    max_results = max(1, min(int(max_results), 50))

    try:
        service = get_service()
        now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
    except HttpError as error:
        return f"Erreur de l'API Google Calendar : {error}"

    events = events_result.get("items", [])
    if not events:
        return "Aucun événement à venir."

    lines = []
    for event in events:
        # "dateTime" pour un événement avec horaire, "date" pour un événement sur la journée
        start = event["start"].get("dateTime", event["start"].get("date"))
        lines.append(f"{start} - {event.get('summary', '(sans titre)')}")
    return "\n".join(lines)




if __name__ == "__main__":
    print(get_upcoming_events())

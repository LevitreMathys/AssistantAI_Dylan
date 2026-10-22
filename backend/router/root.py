import os
from contextlib import closing

from fastapi import APIRouter, Response, status

from app.db import get_db_connection

# Variables sans lesquelles l'agent ne peut pas répondre
REQUIRED_ENV_VARS: tuple[str, ...] = ("GROQ_API_KEY", "MODEL", "BASE_URL")


class RootRouter(APIRouter):
    def __init__(self) -> None:
        super().__init__()
        self._insert_endpoints()

    def _insert_endpoints(self) -> None:
        self.add_api_route("/", self.root, methods=["GET"])
        self.add_api_route("/health", self.health, methods=["GET"])

    def root(self) -> dict:
        """Accueil : ne peut pas échouer, toujours 200."""
        return {"message": "Bienvenue sur l'API Louis"}

    def health(self, response: Response) -> dict:
        """Vérifie que l'agent est prêt à répondre.

        200 si tout va bien, 503 si un élément indispensable manque.
        Le détail de chaque vérification est renvoyé pour faciliter le diagnostic.

        On n'appelle volontairement pas Groq : cette route est appelée souvent
        (Docker, Node…) et consommerait du quota pour rien.
        """
        checks = {
            "config": self._check_config(),
            "database": self._check_database(),
        }
        healthy = all(result == "ok" for result in checks.values())

        if not healthy:
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

        return {"status": "ok" if healthy else "error", "checks": checks}

    @staticmethod
    def _check_config() -> str:
        missing = [name for name in REQUIRED_ENV_VARS if not os.getenv(name)]
        # On donne le nom des variables manquantes, jamais leur valeur
        return "ok" if not missing else f"variables manquantes : {', '.join(missing)}"

    @staticmethod
    def _check_database() -> str:
        try:
            with closing(get_db_connection()) as conn:
                conn.execute("SELECT 1")
            return "ok"
        except Exception as e:
            return f"base inaccessible : {e}"

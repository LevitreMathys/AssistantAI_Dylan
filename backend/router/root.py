

from fastapi import APIRouter

class RootRouter(APIRouter):
    def __init__(self) -> None:
        super().__init__()
        self._insert_endpoints()

    def _insert_endpoints(self):
        self.add_api_route("/", self.root, methods=["GET"])

    def root(self) -> dict:
        return {"message": "Bienvenue sur l'API Louis"}
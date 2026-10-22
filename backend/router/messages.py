
from fastapi import APIRouter

from app.LouisApp import LouisApp
from backend.MessageRequest import MessageRequest


class MessagesRouter(APIRouter):
    def __init__(self, louisApp: LouisApp) -> None:
        super().__init__(prefix="/messages")
        self.Louis = louisApp
        self._insert_endpoints()

    def _insert_endpoints(self):
        self.add_api_route("/", self.get_messages, methods=["GET"])
        self.add_api_route("/send", self.send_message, methods=["POST"])

    def send_message(self, request: MessageRequest):
        return self.Louis.chat(message=request.message)

    def get_messages(self):
        return {"messages": []}

    
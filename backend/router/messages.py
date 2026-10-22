
from fastapi import APIRouter

from app.LouisApp import LouisApp
from backend.MessageRequest import MessageRequest
from app.db import get_db_connection, load_history, trim_history


class MessagesRouter(APIRouter):
    def __init__(self, louisApp: LouisApp) -> None:
        super().__init__(prefix="/messages")
        self.Louis = louisApp
        self._insert_endpoints()

    def _insert_endpoints(self):
        self.add_api_route("", self.get_messages, methods=["GET"])
        self.add_api_route("/send", self.send_message, methods=["POST"])

    def send_message(self, request: MessageRequest):

        if not request.message:
            return {"error": "Message is required"}
        try:
            return self.Louis.chat(message=request.message)
        except Exception as e:
            print(f"Error occurred while sending message: {e}")

    def get_messages(self):
        try:
            messages = trim_history(load_history(get_db_connection()))
        except Exception as e:
            print(f"Error occurred while fetching messages: {e}")
            messages = []

        return {"messages": messages}

    
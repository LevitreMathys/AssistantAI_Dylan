

import os
import sqlite3
from openai.types.responses import Response
from app.client import client

from app.db import get_db_connection, save_message, load_history, trim_history
from app.tools.TOOLS import AVAILABLES_TOOLS, TOOLS_DEFINITIONS
import json
from dotenv import load_dotenv

class LouisApp:

    def __init__(self) -> None:
        load_dotenv()

        self.MODEL = os.getenv("MODEL")

    def execute_tool_call(self, tool_call) -> dict:
        try:
                
            """Parse and execute a single tool call"""
            function_name = tool_call.function.name
            function_to_call = AVAILABLES_TOOLS[function_name]
            function_args = json.loads(tool_call.function.arguments)
            
            # Call the function with unpacked arguments
            return function_to_call(**function_args)
        except Exception as e:
            return f"Erreur lors de l'exécution de l'outil : {str(e)}"

    def chat(self, message: str) -> dict:

        conn : sqlite3.Connection = get_db_connection()

        if not load_history(conn):
                save_message(conn, {"role": "system", "content": "Tu es un assistant. ..."})

        if message.upper() in ("QUIT", "EXIT"):
            conn.close()
            return {"role": "system", "content": "Au revoir!"}

        save_message(conn, {"role": "user", "content": message})

        while True:
            # 'Envoi' du message au model
            response : Response = client.chat.completions.create(
                messages=trim_history(load_history(conn)),
                model=self.MODEL,
                tools=TOOLS_DEFINITIONS,
                tool_choice="auto"
            )

            assistant_message = response.choices[0].message
            save_message(conn, assistant_message.model_dump(exclude_none=True))

            # Recherche d'utilisation d'outils
            if not assistant_message.tool_calls:
                break

            # Exécution des fonctions
            for tool_call in assistant_message.tool_calls:
                print(f"[TOOL] {tool_call.function.name}")
                tool_result = self.execute_tool_call(tool_call)
                save_message(conn, {"role": "tool", "content": str(tool_result), "tool_call_id": tool_call.id})

        conn.close()
        return {"role": "assistant", "content": assistant_message.content}
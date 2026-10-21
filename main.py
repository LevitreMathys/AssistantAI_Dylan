
from dotenv import load_dotenv
import os
from openai.types.responses import Response
from db import get_db_connection, load_history, save_message
from client import client
from tools.TOOLS import AVAILABLES_TOOLS, TOOLS_DEFINITIONS
import json

load_dotenv()

def execute_tool_call(tool_call):
    try:
            
        """Parse and execute a single tool call"""
        function_name = tool_call.function.name
        function_to_call = AVAILABLES_TOOLS[function_name]
        function_args = json.loads(tool_call.function.arguments)
        
        # Call the function with unpacked arguments
        return function_to_call(**function_args)
    except Exception as e:
        return f"Erreur lors de l'exécution de l'outil : {str(e)}"

def chat() -> None:

    MODEL = os.getenv("MODEL")
    conn = get_db_connection()

    
    if not load_history(conn):
        save_message(conn, {"role": "system", "content": "Tu es un assistant. ..."})


    while True:
        user_message = input("[YOU] ")
        if user_message.upper() in ("QUIT", "EXIT"):
            break

        save_message(conn, {"role": "user", "content": user_message})
        while True:    
            # 'Envoi' du message au model
            response : Response = client.chat.completions.create(
                messages=load_history(conn),
                model=MODEL,
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
                tool_result = execute_tool_call(tool_call)
                save_message(conn, {"role": "tool", "content": str(tool_result), "tool_call_id": tool_call.id})
            
        # Stockage et affichage de la réponse du model
        print(f"[ASSISTANT] {assistant_message.content}")

    conn.close()

    
if __name__ == '__main__':

    chat()
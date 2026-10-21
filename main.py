
from openai.types.responses import Response
from client import client
from tools.TOOLS import AVAILABLES_TOOLS, TOOLS_DEFINITIONS
import json

def execute_tool_call(tool_call):
    """Parse and execute a single tool call"""
    function_name = tool_call.function.name
    function_to_call = AVAILABLES_TOOLS[function_name]
    function_args = json.loads(tool_call.function.arguments)
    
    # Call the function with unpacked arguments
    return function_to_call(**function_args)


def chat() -> None:

    history : list[dict[str, str]] = [
        {"role": "system", "content": "Tu es un assistant. Ton rôle est de parler en français de la manière la plus soutenue possible."}
    ]

    while True:
        user_message = input("[YOU] ")
        if user_message.upper() in ("QUIT", "EXIT"):
            break

        history.append({"role": "user", "content": user_message})
        while True:    
            # 'Envoi' du message au model
            response : Response = client.chat.completions.create(
                messages=history,
                model="openai/gpt-oss-120b",
                tools=TOOLS_DEFINITIONS,
                tool_choice="auto"
            )
            assistant_message = response.choices[0].message
            history.append(assistant_message.model_dump(exclude_none=True))

            # Recherche d'utilisation d'outils
            if not assistant_message.tool_calls:
                break

            # Exécution des fonctions
            for tool_call in assistant_message.tool_calls:
                print(f"[TOOL] {tool_call.function.name}")
                tool_result = execute_tool_call(tool_call)
                history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(tool_result)
                })
            
        # Stockage et affichage de la réponse du model
        print(f"[ASSISTANT] {assistant_message.content}")

if __name__ == '__main__':

    chat()
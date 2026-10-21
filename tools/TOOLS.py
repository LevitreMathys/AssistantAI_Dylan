from tools.Hour import get_time


TOOLS_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "Donne l'heure actuelle au format HH:MM. Affiche-la telle quelle à l'utilisateur.",
        }
    },
    # {
    #     "type": "function",
    #     "function": {
    #         "name": "get_time",
    #         "description": "Donne l'heure actuelle.",
    #         "parameters": {
    #             "type": "object",
    #             "properties": {
    #                 "ville": {
    #                     "type": "string",
    #                     "description": "Le nom de la ville (ex: Paris)"
    #                 }
    #             },
    #             "required": ["ville"]
    #         }
    #     }
    # }
]


AVAILABLES_TOOLS : dict = {
    "get_time" : get_time
}
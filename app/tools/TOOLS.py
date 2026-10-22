from tools.Hour import get_time
from tools.search import search
from tools.calendar.google_calendar import get_upcoming_events
from db import create_table, drop_table


TOOLS_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_time",
            "description": "Donne l'heure actuelle au format HH:MM. Affiche-la telle quelle à l'utilisateur.",
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_table",
            "description": "Crée une nouvelle table dans la base de données.",
            "parameters": {
                "type": "object",
                "properties": {
                    "tablename": {
                        "type": "string",
                        "description": "Nom de la table (lettres, chiffres, _).",
                    },
                    "columns": {
                        "type": "array",
                        "description": "Les colonnes de la table. Ne pas inclure 'id' : il est ajouté automatiquement.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "type": {"type": "string", "enum": ["TEXT", "INTEGER", "REAL", "BOOLEAN", "DATETIME"]},
                            },
                            "required": ["name", "type"],
                        },
                    },
                },
                "required": ["tablename", "columns"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "drop_table",
            "description": "Supprime une table de la base de données.",
            "parameters": {
                "type": "object",
                "properties": {
                    "tablename": {
                        "type": "string",
                        "description": "Nom de la table (lettres, chiffres, _).",
                    },
                },
                "required": ["tablename"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search",
            "description": "Recherche dans les résultats.",
            "parameters": {
                "type": "object",
                "properties": {
                    "search_query": {
                        "type": "string",
                        "description": "La requête de recherche.",
                    }
                },
                "required": ["search_query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_upcoming_events",
            "description": "Liste les prochains événements de l'agenda Google de l'utilisateur (date de début et titre). À utiliser quand il demande son planning, ses rendez-vous ou ce qu'il a de prévu.",
            "parameters": {
                "type": "object",
                "properties": {
                    "max_results": {
                        "type": "integer",
                        "description": "Nombre maximum d'événements à renvoyer (1 à 50). 10 par défaut.",
                    }
                },
                "required": [],
            },
        },
    },

]



AVAILABLES_TOOLS : dict = {
    "get_time" : get_time,
    "create_table" : create_table,
    "drop_table" : drop_table,
    "search" : search,
    "get_upcoming_events" : get_upcoming_events,
}
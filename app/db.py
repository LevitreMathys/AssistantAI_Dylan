import sqlite3
from enum import Enum
import json
import re
from pathlib import Path

# Toujours agent/app/chatbot.db, quel que soit le dossier de lancement
DB_PATH: Path = Path(__file__).parent / "chatbot.db"

# Taille max (en caractères JSON) de l'historique envoyé au modèle.
# ~3,5 caractères par token : 12 000 caractères ≈ 3 500 tokens, ce qui laisse
# de la place pour les définitions d'outils sous la limite de 7 000 tokens/min.
MAX_HISTORY_CHARS: int = 12_000

class Role(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"

class ColumnType(Enum):
    TEXT = "TEXT"
    INTEGER = "INTEGER"
    DATETIME = "DATETIME"

def get_db_connection() -> sqlite3.Connection:

    conn : sqlite3.Connection = sqlite3.connect(DB_PATH)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS History (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    return conn

def create_table(tablename: str, columns: list[dict]) -> str:

    NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")

    if not NAME_RE.match(tablename):
        return f"Erreur : nom de table invalide '{tablename}'."
    if tablename.lower() == "history":
        return "Erreur : la table History est réservée."

    cols: list[str] = []
    for col in columns:
        name, col_type = col["name"], col["type"]
        if name.lower() == "id":
            continue
        if not NAME_RE.match(name):
            return f"Erreur : nom de colonne invalide '{name}'."
        try:
            ColumnType(col_type)          
        except ValueError:
            return f"Erreur : type invalide '{col_type}'."
        cols.append(f"{name} {col_type}")

    conn = get_db_connection()
    try:
        conn.execute(
            f"CREATE TABLE IF NOT EXISTS {tablename} "
            f"(id INTEGER PRIMARY KEY AUTOINCREMENT, {', '.join(cols)})"
        )
        conn.commit()
    finally:
        conn.close()

    return f"Table '{tablename}' créée avec les colonnes : {', '.join(cols)}."

def drop_table(tablename: str) -> str:
    conn = get_db_connection()
    try:
        conn.execute(f"DROP TABLE IF EXISTS {tablename}")
        conn.commit()
    finally:
        conn.close()
    return f"Table '{tablename}' supprimée."

def save_message(conn: sqlite3.Connection, message: dict) -> None:
    conn.execute(
        "INSERT INTO History (role, message) VALUES (?, ?)",
        (Role(message["role"]).value, json.dumps(message, ensure_ascii=False)),
    )
    conn.commit()


def load_history(conn: sqlite3.Connection) -> list[dict]:
    rows = conn.execute("SELECT message FROM History ORDER BY id").fetchall()
    return [json.loads(row[0]) for row in rows]


def trim_history(history: list[dict], max_chars: int = MAX_HISTORY_CHARS) -> list[dict]:
    """Réduit l'historique avant de l'envoyer au modèle (la base, elle, garde tout).

    - Le prompt système (1er message) est toujours gardé.
    - Le tour en cours (dernier message user et tout ce qui suit) est toujours gardé.
    - On ajoute ensuite les messages plus anciens tant qu'on reste sous max_chars.
    - La coupe commence toujours sur un message user, pour ne jamais séparer
      une demande d'outil (tool_calls) de sa réponse (role "tool").
    """
    if not history:
        return history

    system = [history[0]] if history[0]["role"] == "system" else []
    rest = history[len(system):]

    def size(msg: dict) -> int:
        return len(json.dumps(msg, ensure_ascii=False))

    user_indexes = [i for i, msg in enumerate(rest) if msg["role"] == "user"]
    last_user = user_indexes[-1] if user_indexes else 0

    # Le tour en cours est toujours envoyé
    start = last_user
    total = sum(size(msg) for msg in rest[last_user:])

    # On remonte vers les messages plus anciens tant que ça tient
    for i in range(last_user - 1, -1, -1):
        total += size(rest[i])
        if total > max_chars:
            break
        start = i

    # On avance jusqu'au premier message user pour ne pas couper un échange d'outils
    while start < last_user and rest[start]["role"] != "user":
        start += 1

    return system + rest[start:]
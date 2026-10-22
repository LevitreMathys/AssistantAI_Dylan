import sqlite3
from enum import Enum
import json
import re
DB_PATH : str = 'chatbot.db'

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
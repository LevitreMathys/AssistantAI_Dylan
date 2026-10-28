def readFile(file_path: str) -> str:
    try:
        with open(file_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return "Fichier non trouvé."
    except Exception as e:
        return f"Erreur lors de la lecture du fichier : {e}"

def writeFile(file_path: str, content: str) -> str:
    try:
        with open(file_path, "w") as f:
            f.write(content)
        return "Fichier écrit avec succès."
    except Exception as e:
        return f"Erreur lors de l'écriture du fichier : {e}"
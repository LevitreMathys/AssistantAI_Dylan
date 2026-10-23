from datetime import datetime

def get_time() -> datetime:

    """ Cette fonction renvoie l'heure actuelle
    :return: `datetime` => L'heure actuelle
    """
    # Obtenir la date et l'heure courantes
    return datetime.now().strftime("%H:%M:%S")
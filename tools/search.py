from ddgs import DDGS

def search(search_query: str) -> list:
    """ Lance une recherche sur internet

    Args:
        search_query (str): Nom de la requête

    Returns:
        list: Liste des résultats de la recherche
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(search_query, max_results=2))

            if not results:
                print("Aucun résultat trouvé.")
                
    except Exception as e:
        print(f"Erreur lors de la recherche: {e}")

    return results

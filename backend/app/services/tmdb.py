"""
Service TMDB.

Toute communication avec l'API TMDB passe par ce fichier — c'est le seul
endroit du projet qui connaît l'URL et le format de réponse de TMDB.
Si TMDB change son API un jour, on ne modifie que ce fichier.

Point important : TMDB traite les films ("movie") et les séries ("tv")
comme deux catégories séparées, avec des endpoints et des noms de champs
différents (ex: "title"/"release_date" pour les films vs "name"/
"first_air_date" pour les séries). Chaque fonction ci-dessous accepte donc
un paramètre `media_type` ("movie" ou "tv") et adapte les champs en
conséquence, mais renvoie toujours la même forme de données en sortie
— le reste de l'app n'a pas à se soucier de cette différence.

On utilise httpx (client HTTP asynchrone) pour ne pas bloquer le serveur
pendant les appels réseau.
"""

import httpx
from app.config import settings
from app.models.schemas import MovieSearchResult, MediaType

# Cache mémoire très simple : évite de re-appeler TMDB pour les mêmes
# films/séries pendant la durée de vie du serveur. Suffisant pour un projet
# de cette taille ; on pourra migrer vers Redis plus tard si besoin.
# Clé composite (media_type, id) car un film et une série peuvent partager
# le même ID numérique côté TMDB.
_media_details_cache: dict[tuple[str, int], dict] = {}

# Cache du mapping "nom de genre" -> "id TMDB", séparé par type de média
# car TMDB a deux listes de genres différentes (ex: "Soap" n'existe qu'en série).
_genre_name_to_id: dict[str, dict[str, int]] = {}


def _title_field(media_type: MediaType) -> str:
    return "title" if media_type == "movie" else "name"


def _date_field(media_type: MediaType) -> str:
    return "release_date" if media_type == "movie" else "first_air_date"


async def get_genre_map(media_type: MediaType) -> dict[str, int]:
    """
    Récupère (et met en cache) le mapping officiel nom de genre -> ID TMDB,
    séparément pour les films et les séries.
    """
    if media_type in _genre_name_to_id:
        return _genre_name_to_id[media_type]

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.tmdb_base_url}/genre/{media_type}/list",
            params={"api_key": settings.tmdb_api_key, "language": "fr-FR"},
        )
        response.raise_for_status()
        data = response.json()

    mapping = {g["name"]: g["id"] for g in data.get("genres", [])}
    _genre_name_to_id[media_type] = mapping
    return mapping


async def search_media(
    query: str, media_type: MediaType, limit: int = 5
) -> list[MovieSearchResult]:
    """
    Utilisé par l'endpoint d'autocomplétion.
    Renvoie une liste courte de films OU de séries (selon media_type)
    correspondant au texte tapé.
    """
    title_field = _title_field(media_type)
    date_field = _date_field(media_type)

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.tmdb_base_url}/search/{media_type}",
            params={
                "api_key": settings.tmdb_api_key,
                "query": query,
                "language": "fr-FR",
            },
        )
        response.raise_for_status()
        data = response.json()

    results = []
    for item in data.get("results", [])[:limit]:
        year = None
        if item.get(date_field):
            year = int(item[date_field][:4])
        results.append(
            MovieSearchResult(
                tmdb_id=item["id"],
                title=item[title_field],
                year=year,
                poster_path=item.get("poster_path"),
            )
        )
    return results


async def get_media_details(media_id: int, media_type: MediaType) -> dict:
    """
    Récupère les métadonnées complètes d'un film ou d'une série (genres,
    acteurs, réalisateur/showrunner, mots-clés, synopsis) à partir de son ID TMDB.
    Le paramètre append_to_response évite de faire plusieurs appels séparés.
    """
    cache_key = (media_type, media_id)
    if cache_key in _media_details_cache:
        return _media_details_cache[cache_key]

    title_field = _title_field(media_type)
    date_field = _date_field(media_type)

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.tmdb_base_url}/{media_type}/{media_id}",
            params={
                "api_key": settings.tmdb_api_key,
                "language": "fr-FR",
                "append_to_response": "credits,keywords",
            },
        )
        response.raise_for_status()
        data = response.json()

    # Les séries n'ont pas de "réalisateur" à proprement parler ; on prend
    # le créateur ("created_by") s'il existe, sinon le premier "director" trouvé.
    if media_type == "tv":
        creators = data.get("created_by", [])
        director = creators[0]["name"] if creators else None
    else:
        director = next(
            (c["name"] for c in data.get("credits", {}).get("crew", [])
             if c["job"] == "Director"),
            None,
        )

    # Le champ "keywords" n'est pas structuré pareil entre film et série
    keywords_data = data.get("keywords", {})
    keywords_list = keywords_data.get("keywords") or keywords_data.get("results") or []

    details = {
        "id": data["id"],
        "media_type": media_type,
        "title": data[title_field],
        "overview": data.get("overview", ""),
        "genres": [g["name"] for g in data.get("genres", [])],
        "keywords": [k["name"] for k in keywords_list],
        "director": director,
        "cast": [c["name"] for c in data.get("credits", {}).get("cast", [])[:5]],
        "poster_path": data.get("poster_path"),
        "release_date": data.get(date_field),
        "vote_average": data.get("vote_average"),
    }

    _media_details_cache[cache_key] = details
    return details


async def get_candidate_media(
    media_type: MediaType,
    genre_ids: list[int],
    exclude_ids: list[int],
    min_year: int | None = None,
    min_rating: float | None = None,
) -> list[dict]:
    """
    Récupère un pool de films OU de séries candidats partageant des genres
    communs. Ce pool sera ensuite transmis à l'IA, qui affinera le choix
    final parmi ces résultats réels (elle n'invente jamais de titre).

    min_year : ne renvoie que des résultats sortis/diffusés à partir de cette année
    min_rating : ne renvoie que des résultats avec une note TMDB >= à ce seuil
    """
    date_gte_field = (
        "primary_release_date.gte" if media_type == "movie" else "first_air_date.gte"
    )

    params = {
        "api_key": settings.tmdb_api_key,
        "language": "fr-FR",
        "sort_by": "popularity.desc",
        "vote_count.gte": 100,  # évite les résultats trop confidentiels/mal notés
    }
    if genre_ids:
        params["with_genres"] = ",".join(str(g) for g in genre_ids)
    if min_year:
        params[date_gte_field] = f"{min_year}-01-01"
    if min_rating:
        params["vote_average.gte"] = min_rating

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.tmdb_base_url}/discover/{media_type}",
            params=params,
        )
        response.raise_for_status()
        data = response.json()

    candidates = [
        item for item in data.get("results", [])
        if item["id"] not in exclude_ids
    ]
    return candidates[:15]  # on limite le pool envoyé à l'IA


async def get_video_key(media_id: int, media_type: MediaType) -> str | None:
    """
    Récupère la clé YouTube de la bande-annonce officielle (si disponible).
    Appelée seulement pour les suggestions finalement retenues (2-3 titres),
    pas pour tout le pool de candidats, afin de limiter le nombre d'appels TMDB.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.tmdb_base_url}/{media_type}/{media_id}/videos",
            params={"api_key": settings.tmdb_api_key, "language": "fr-FR"},
        )
        response.raise_for_status()
        data = response.json()

    videos = data.get("results", [])
    # Si aucune bande-annonce en français, on retente en anglais (plus de contenu dispo)
    if not videos:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.tmdb_base_url}/{media_type}/{media_id}/videos",
                params={"api_key": settings.tmdb_api_key, "language": "en-US"},
            )
            response.raise_for_status()
            videos = response.json().get("results", [])

    trailer = next(
        (v for v in videos if v["site"] == "YouTube" and v["type"] == "Trailer"),
        None,
    )
    return trailer["key"] if trailer else None
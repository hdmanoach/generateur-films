"""
Route /search — utilisée par le champ d'autocomplétion du frontend.

Le frontend appelle GET /search?q=inter...&media_type=movie (ou "tv") après
un debounce de ~300ms (pas à chaque frappe de touche), pour éviter de
saturer le rate limit TMDB. Le media_type vient du mode choisi par
l'utilisateur (Films OU Séries) avant de commencer sa recherche.
"""

from fastapi import APIRouter, Query
from app.services.tmdb import search_media
from app.models.schemas import MovieSearchResult, MediaType

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=list[MovieSearchResult])
async def search(
    q: str = Query(..., min_length=1, description="Texte tapé par l'utilisateur"),
    media_type: MediaType = Query("movie", description="'movie' ou 'tv'"),
):
    """
    Renvoie une liste courte de films OU de séries (selon media_type)
    correspondant au texte tapé, avec leur ID TMDB — c'est cet ID que le
    frontend doit conserver, pas le texte, pour éviter toute ambiguïté de titre.
    """
    return await search_media(q, media_type, limit=5)

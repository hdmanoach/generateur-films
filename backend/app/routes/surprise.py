"""
Route /surprise — "Surprise moi".

Plutôt que de faire saisir 2 titres à l'utilisateur, on en tire 2 au hasard
parmi les titres populaires du moment, puis on réutilise exactement la même
logique de suggestion que /suggest (voir app/services/suggestion.py).
"""

from fastapi import APIRouter
from app.models.schemas import SurpriseResponse, MediaType
from app.services import tmdb
from app.services.suggestion import build_suggestions

router = APIRouter(prefix="/surprise", tags=["surprise"])


@router.get("", response_model=SurpriseResponse)
async def surprise(
    media_type: MediaType = "movie",
    min_year: int | None = None,
    min_rating: float | None = None,
):
    base_media = await tmdb.get_random_popular(media_type, count=2)

    result = await build_suggestions(
        media_type=media_type,
        id_1=base_media[0].tmdb_id,
        id_2=base_media[1].tmdb_id,
        min_year=min_year,
        min_rating=min_rating,
    )

    return SurpriseResponse(base_media=base_media, suggestions=result.suggestions)
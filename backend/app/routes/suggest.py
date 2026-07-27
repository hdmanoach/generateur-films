"""
Route /suggest — l'utilisateur choisit lui-même les 2 films/séries de référence.

La logique de génération elle-même vit dans app/services/suggestion.py,
partagée avec /surprise.
"""

from fastapi import APIRouter
from app.models.schemas import SuggestRequest, SuggestResponse
from app.services.suggestion import build_suggestions

router = APIRouter(prefix="/suggest", tags=["suggest"])


@router.post("", response_model=SuggestResponse)
async def suggest(request: SuggestRequest):
    return await build_suggestions(
        media_type=request.media_type,
        id_1=request.movie_id_1,
        id_2=request.movie_id_2,
        min_year=request.min_year,
        min_rating=request.min_rating,
    )
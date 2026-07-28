"""
Logique de génération de suggestion, partagée entre :
  - /suggest (l'utilisateur choisit lui-même les 2 films/séries)
  - /surprise (2 titres populaires sont choisis au hasard par le serveur)

Centraliser cette logique ici évite de la dupliquer dans deux routes.
"""

from fastapi import HTTPException
from app.models.schemas import SuggestResponse, MovieSuggestion, MediaType
from app.services import tmdb, ai


async def build_suggestions(
    media_type: MediaType,
    id_1: int,
    id_2: int,
    min_year: int | None = None,
    min_rating: float | None = None,
) -> SuggestResponse:
    # Étape 1 : métadonnées réelles des 2 références
    item1 = await tmdb.get_media_details(id_1, media_type)
    item2 = await tmdb.get_media_details(id_2, media_type)

    # Étape 2 : pool de candidats réels, basé sur les genres communs et
    # filtré selon les critères optionnels de l'utilisateur
    genre_ids = await _to_genre_ids(item1, item2, media_type)
    candidates = await tmdb.get_candidate_media(
        media_type=media_type,
        genre_ids=genre_ids,
        exclude_ids=[id_1, id_2],
        min_year=min_year,
        min_rating=min_rating,
    )

    if not candidates:
        raise HTTPException(
            status_code=404,
            detail="Aucun résultat candidat trouvé — essaie d'assouplir les filtres (année/note)",
        )

    # Étape 3 : l'IA classe les candidats réels et rédige l'explication
    ai_results = await ai.generate_suggestions(item1, item2, candidates, media_type)

    # Fallback : si l'IA échoue, on retombe sur un tri simple par popularité
    if not ai_results:
        fallback_label = "Film populaire du même genre." if media_type == "movie" else "Série populaire du même genre."
        ai_results = [
            {"tmdb_id": c["id"], "compatibility_score": 50, "explanation": fallback_label}
            for c in candidates[:3]
        ]

    # Étape 4 : on enrichit chaque suggestion avec ses métadonnées complètes
    suggestions = []
    candidates_by_id = {c["id"]: c for c in candidates}
    title_field = "title" if media_type == "movie" else "name"
    date_field = "release_date" if media_type == "movie" else "first_air_date"

    for result in ai_results:
        candidate = candidates_by_id.get(result["tmdb_id"])
        if not candidate:
            continue
        trailer_key = await tmdb.get_video_key(candidate["id"], media_type)
        suggestions.append(
            MovieSuggestion(
                tmdb_id=candidate["id"],
                title=candidate[title_field],
                year=int(candidate[date_field][:4]) if candidate.get(date_field) else None,
                overview=candidate.get("overview", ""),
                poster_path=candidate.get("poster_path"),
                genres=[],
                compatibility_score=result["compatibility_score"],
                explanation=result["explanation"],
                trailer_key=trailer_key,
            )
        )

    return SuggestResponse(suggestions=suggestions)


async def _to_genre_ids(item1: dict, item2: dict, media_type: MediaType) -> list[int]:
    """Union des genres des 2 références, convertis en IDs TMDB."""
    genre_map = await tmdb.get_genre_map(media_type)
    genre_names = set(item1["genres"]) | set(item2["genres"])
    return [genre_map[name] for name in genre_names if name in genre_map]
"""
Route /suggest — cœur fonctionnel de l'application.

Déroulé complet (correspond aux étapes définies dans le cadrage du projet) :
  1. Récupérer les métadonnées réelles des 2 films/séries de référence (TMDB)
  2. Construire un pool de candidats réels du même type de média (TMDB), en
     tenant compte des genres communs et des filtres optionnels (année, note)
  3. Demander à l'IA de classer ces candidats + rédiger l'explication
  4. Enrichir chaque suggestion retenue avec ses métadonnées complètes
  5. Renvoyer le tout au frontend, prêt à afficher

Mode séparé (pas de mélange films/séries) : le champ `media_type` de la
requête détermine si TOUT le pipeline travaille sur des films ou des séries.

Note : pas d'historique / de base de données dans cette version — chaque
appel est stateless, la suggestion est générée puis renvoyée directement.
"""

from fastapi import APIRouter, HTTPException
from app.models.schemas import SuggestRequest, SuggestResponse, MovieSuggestion, MediaType
from app.services import tmdb, ai

router = APIRouter(prefix="/suggest", tags=["suggest"])


@router.post("", response_model=SuggestResponse)
async def suggest(request: SuggestRequest):
    media_type = request.media_type

    # Étape 1 : métadonnées réelles des 2 films/séries de référence
    item1 = await tmdb.get_media_details(request.movie_id_1, media_type)
    item2 = await tmdb.get_media_details(request.movie_id_2, media_type)

    # Étape 2 : pool de candidats réels du même type de média, basé sur les
    # genres communs et filtré selon les critères optionnels de l'utilisateur
    genre_ids = await _to_genre_ids(item1, item2, media_type)
    candidates = await tmdb.get_candidate_media(
        media_type=media_type,
        genre_ids=genre_ids,
        exclude_ids=[request.movie_id_1, request.movie_id_2],
        min_year=request.min_year,
        min_rating=request.min_rating,
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

    # Étape 4 : on enrichit chaque suggestion avec les métadonnées complètes
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
                genres=[],  # optionnel : mapping id→nom de genre à ajouter à l'affichage
                compatibility_score=result["compatibility_score"],
                explanation=result["explanation"],
                trailer_key=trailer_key,
            )
        )

    response = SuggestResponse(suggestions=suggestions)

    # Étape 5 : réponse prête pour le frontend
    return response


async def _to_genre_ids(item1: dict, item2: dict, media_type: MediaType) -> list[int]:
    """
    Convertit les noms de genres des 2 références (ex: "Action", "Drame")
    en IDs numériques TMDB, en utilisant le mapping officiel du bon type de
    média (mis en cache séparément pour "movie" et "tv").

    On prend l'union des genres des 2 références : ça donne un pool de
    candidats plus large que l'intersection stricte, ce que l'IA affinera ensuite.
    """
    genre_map = await tmdb.get_genre_map(media_type)
    genre_names = set(item1["genres"]) | set(item2["genres"])
    return [genre_map[name] for name in genre_names if name in genre_map]
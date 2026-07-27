"""
Schémas Pydantic.

Ces classes définissent la "forme" exacte des données qui entrent et sortent
de l'API. FastAPI s'en sert pour :
  - valider automatiquement les requêtes (erreur claire si un champ manque)
  - générer la documentation interactive (/docs) automatiquement
  - sérialiser les réponses JSON de façon cohérente
"""

from pydantic import BaseModel
from typing import Optional, Literal

# "movie" ou "tv" — choisi par l'utilisateur avant la recherche.
# Mode séparé assumé : pas de mélange films/séries dans une même requête.
MediaType = Literal["movie", "tv"]


# ---- Résultats d'autocomplétion (utilisés par /search) ----

class MovieSearchResult(BaseModel):
    tmdb_id: int
    title: str
    year: Optional[int] = None
    poster_path: Optional[str] = None


# ---- Requête de suggestion (utilisée par /suggest) ----

class SuggestRequest(BaseModel):
    media_type: MediaType = "movie"
    # On envoie les IDs TMDB choisis via l'autocomplétion, pas des titres en texte libre
    movie_id_1: int
    movie_id_2: int
    # Filtres optionnels (fonctionnalité V2)
    min_year: Optional[int] = None
    min_rating: Optional[float] = None


# ---- Une suggestion renvoyée par le backend ----

class MovieSuggestion(BaseModel):
    tmdb_id: int
    title: str
    year: Optional[int] = None
    overview: str
    poster_path: Optional[str] = None
    genres: list[str] = []
    compatibility_score: int  # score de 0 à 100
    explanation: str  # texte généré par l'IA
    trailer_key: Optional[str] = None  # clé YouTube, si une bande-annonce existe


class SuggestResponse(BaseModel):
    suggestions: list[MovieSuggestion]
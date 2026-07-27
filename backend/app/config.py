"""
Configuration centrale de l'application.

Toutes les clés API et variables sensibles passent par des variables
d'environnement (jamais en dur dans le code). On utilise pydantic-settings
pour charger automatiquement le fichier .env et valider les types.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Clé API TMDB (https://www.themoviedb.org/settings/api)
    tmdb_api_key: str
    tmdb_base_url: str = "https://api.themoviedb.org/3"

    # Clé API Gemini (https://aistudio.google.com/apikey)
    gemini_api_key: str
    gemini_model: str = "gemini-3.5-flash"

    # Autoriser le frontend Next.js à appeler ce backend (CORS)
    frontend_origin: str = "http://localhost:3000"

    class Config:
        env_file = ".env"


# Instance unique réutilisée partout dans l'app (pattern singleton simple)
settings = Settings()

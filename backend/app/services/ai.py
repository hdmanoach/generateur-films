"""
Service IA (Google Gemini).

Rôle précis de l'IA dans ce projet : elle NE choisit PAS un titre au hasard
dans le vide. Elle reçoit :
  1. les métadonnées réelles des 2 films/séries aimés par l'utilisateur
  2. une liste de candidats réels du même type de média (venant de TMDB)

... et elle doit uniquement classer/expliquer parmi ces candidats réels.
Ça élimine le risque d'hallucination (inventer un titre qui n'existe pas).

On demande à Gemini de répondre STRICTEMENT en JSON pour pouvoir parser
la réponse de façon fiable côté code.
"""

import json
import logging
import httpx
from app.config import settings
from app.models.schemas import MediaType

logger = logging.getLogger(__name__)

GEMINI_URL = (
    f"https://generativelanguage.googleapis.com/v1beta/models/"
    f"{settings.gemini_model}:generateContent"
)


def _build_prompt(
    item1: dict, item2: dict, candidates: list[dict], media_type: MediaType
) -> str:
    label = "film" if media_type == "movie" else "série"
    title_field = "title" if media_type == "movie" else "name"

    candidates_summary = "\n".join(
        f"- id={c['id']} | titre=\"{c[title_field]}\" | résumé: {c.get('overview', '')[:150]}"
        for c in candidates
    )

    return f"""Tu es un expert en {label}s. Un utilisateur aime ces deux {label}s :

{label.capitalize()} 1 : "{item1['title']}"
Genres : {', '.join(item1['genres'])}
Réalisateur/Créateur : {item1['director']}
Résumé : {item1['overview']}

{label.capitalize()} 2 : "{item2['title']}"
Genres : {', '.join(item2['genres'])}
Réalisateur/Créateur : {item2['director']}
Résumé : {item2['overview']}

Voici une liste de {label}s candidats réels (n'en propose aucun autre que ceux-ci) :
{candidates_summary}

Choisis les 3 meilleurs candidats à recommander, classés du plus pertinent
au moins pertinent. Pour chacun, donne un score de compatibilité de 0 à 100
et une explication courte (1-2 phrases) de pourquoi ce {label} plaira à
quelqu'un qui aime les deux {label}s de référence.

Réponds STRICTEMENT en JSON, sans texte autour, sous cette forme exacte :
{{
  "suggestions": [
    {{"tmdb_id": <id du candidat>, "compatibility_score": <0-100>, "explanation": "..."}}
  ]
}}
"""


async def generate_suggestions(
    item1: dict, item2: dict, candidates: list[dict], media_type: MediaType = "movie"
) -> list[dict]:
    """
    Appelle Gemini pour classer les candidats et générer les explications.
    Renvoie une liste de dicts : [{tmdb_id, compatibility_score, explanation}, ...]
    """
    prompt = _build_prompt(item1, item2, candidates, media_type)

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                GEMINI_URL,
                params={"key": settings.gemini_api_key},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.4},
                },
            )
            response.raise_for_status()
            data = response.json()

        raw_text = data["candidates"][0]["content"]["parts"][0]["text"]

        # Sécurité : Gemini peut parfois entourer le JSON de ```json ... ```
        cleaned = raw_text.strip().removeprefix("```json").removesuffix("```").strip()

        parsed = json.loads(cleaned)
        return parsed["suggestions"]
    except Exception as e:
        logger.error(f"Erreur lors de la génération des suggestions par l'IA : {e}")
        # En cas d'échec de l'appel API ou du parsing, on renvoie une liste vide plutôt que de planter
        # l'API — le endpoint de suggestion pourra utiliser le fallback par popularité.
        return []

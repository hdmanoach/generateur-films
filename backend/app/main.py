"""
Point d'entrée de l'application FastAPI.

C'est ce fichier qu'on lance pour démarrer le serveur :
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes import search, suggest, surprise

app = FastAPI(title="Générateur de suggestions de films — API")

# Autorise le frontend Next.js (autre origine) à appeler cette API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Chaque routeur correspond à un fichier dans app/routes/
app.include_router(search.router)
app.include_router(suggest.router)
app.include_router(surprise.router)


@app.get("/")
async def root():
    return {"status": "ok", "message": "API Générateur de suggestions de films"}
# 🎬 Générateur de suggestions de films & séries

Donne deux films (ou deux séries) que tu aimes, l'application croise leurs
genres, thèmes et casting via l'API TMDB, puis une IA (Google Gemini) affine
le choix parmi des candidats réels et rédige une explication personnalisée.

## Démo

<!--
  Remplace l'URL ci-dessous par celle générée par GitHub après l'upload de
  ta vidéo (voir instructions dans la section "Comment ajouter la vidéo"
  plus bas). Tant que ce n'est pas fait, cette balise n'affichera rien.
-->
<video src="COLLE_ICI_URL_VIDEO_GITHUB.mp4" controls width="700"></video>

## Aperçu

- Autocomplétion des titres (debounce, basée sur l'ID TMDB — pas d'ambiguïté de titre)
- Mode séparé **Films** ou **Séries**
- Suggestions classées par IA avec score de compatibilité et explication en langage naturel
- Bandes-annonces YouTube intégrées quand disponibles
- Interface avec transition : formulaire centré au départ, glisse à gauche au lancement de la recherche, résultats en carrousel à droite

## Stack technique

| Couche | Techno |
|---|---|
| Frontend | Next.js (App Router) + TypeScript + Tailwind CSS |
| Backend | Python + FastAPI |
| Données films/séries | [TMDB API](https://www.themoviedb.org/documentation/api) |
| IA | [Google Gemini API](https://ai.google.dev/) (gratuit pour démarrer) |

Pas de base de données : l'application est volontairement **stateless**, chaque
suggestion est générée à la demande sans historique conservé.

## Structure du dépôt

```
.
├── backend/          # API FastAPI
│   ├── app/
│   │   ├── main.py          # point d'entrée
│   │   ├── config.py        # variables d'environnement
│   │   ├── routes/          # /search, /suggest
│   │   ├── services/        # appels TMDB + IA
│   │   └── models/          # schémas de données (Pydantic)
│   ├── requirements.txt
│   └── .env.example
└── frontend/          # Interface Next.js
    ├── app/              # pages, layout, sitemap, robots, icône
    ├── components/       # champ de recherche, carrousel, cartes
    ├── lib/              # client API vers le backend
    └── .env.local.example
```

## Installation

### Prérequis

- Python 3.11+
- Node.js 18+
- Une clé [TMDB API](https://www.themoviedb.org/settings/api)
- Une clé [Gemini API](https://aistudio.google.com/apikey) (gratuite)

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows : venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# remplir .env avec tes clés TMDB_API_KEY et GEMINI_API_KEY
uvicorn app.main:app --reload
```

Le backend démarre sur `http://localhost:8000` (documentation interactive sur `/docs`).

### 2. Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
# vérifier que NEXT_PUBLIC_API_URL pointe vers le backend (http://localhost:8000 par défaut)
npm run dev
```

Le frontend démarre sur `http://localhost:3000`.

## Variables d'environnement

### `backend/.env`

| Variable | Description |
|---|---|
| `TMDB_API_KEY` | Clé API TMDB |
| `GEMINI_API_KEY` | Clé API Gemini |
| `GEMINI_MODEL` | Modèle Gemini utilisé (par défaut `gemini-2.5-flash-lite`) |
| `FRONTEND_ORIGIN` | URL du frontend, pour la config CORS |

### `frontend/.env.local`

| Variable | Description |
|---|---|
| `NEXT_PUBLIC_API_URL` | URL du backend FastAPI |

## Points d'attention avant déploiement

- Mettre à jour `https://ton-domaine.com` dans `frontend/app/layout.tsx`, `sitemap.ts` et `robots.ts` avec le vrai nom de domaine
- Le nom des modèles Gemini évolue régulièrement — en cas d'erreur 404 sur `/suggest`, vérifier la liste des modèles disponibles sur `https://ai.google.dev/gemini-api/docs/models`
- CORS : `FRONTEND_ORIGIN` côté backend doit correspondre exactement à l'URL de production du frontend

## Fonctionnalités à venir

- Filtres avancés (année, note minimale) — déjà supportés côté API, pas encore d'UI
- Bouton "Surprise moi"
- Partage social des suggestions

## Licence

Projet personnel / éducatif.

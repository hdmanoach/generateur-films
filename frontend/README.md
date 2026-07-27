# Frontend — Générateur de suggestions de films

Interface Next.js (App Router) + Tailwind CSS.

## Installation

```bash
cd frontend
npm install
cp .env.local.example .env.local
# vérifier que NEXT_PUBLIC_API_URL pointe bien vers ton backend FastAPI
```

## Lancer en développement

```bash
npm run dev
```

Ouvre http://localhost:3000 (le backend FastAPI doit tourner en parallèle sur http://localhost:8000)

## Structure du projet

```
frontend/
├── app/
│   ├── layout.tsx       ← polices (Fraunces + Inter) + métadonnées
│   ├── page.tsx         ← page principale (formulaire + résultats)
│   └── globals.css      ← design tokens (couleurs, typographie)
├── components/
│   ├── MovieSearchInput.tsx  ← champ + autocomplétion (debounce 300ms), sensible au media_type
│   ├── MatchDial.tsx         ← jauge circulaire de score de compatibilité
│   └── SuggestionCard.tsx    ← carte d'affichage d'une suggestion
└── lib/
    └── api.ts           ← tous les appels vers le backend FastAPI

## Mode Films / Séries

Un toggle en haut de page permet de choisir "Films" ou "Séries" avant de
commencer sa recherche. Changer de mode réinitialise les champs en cours
(pas de mélange films/séries dans une même recherche).
```

## Direction de design

- **Palette** : anthracite profond (salle obscure), doré chaud (enseigne de
  cinéma), vert sourd (velours de fauteuil) — volontairement différente des
  looks "IA générique" (cream/terracotta, noir/vert acide).
- **Typographie** : Fraunces (display, titres) + Inter (interface, corps de texte).
- **Signature** : le score de compatibilité s'affiche en jauge circulaire
  plutôt qu'en simple pourcentage plat.

## Ce qui n'est pas encore branché (prochaines itérations)

- Filtres avancés (année, note) — les champs existent dans `lib/api.ts` (`SuggestFilters`) mais pas encore d'UI
- Bouton "Surprise moi"
- Partage social

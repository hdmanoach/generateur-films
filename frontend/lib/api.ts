/**
 * Client API — point unique de contact avec le backend FastAPI.
 *
 * Comme pour le backend qui centralise tous les appels TMDB dans un seul
 * fichier, ici tout appel réseau vers notre propre API passe par ce fichier.
 * Si l'URL du backend change (déploiement), on ne modifie qu'un seul endroit.
 */

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

/** "movie" ou "tv" — mode séparé choisi par l'utilisateur avant de chercher. */
export type MediaType = "movie" | "tv";

export type MovieSearchResult = {
  tmdb_id: number;
  title: string;
  year: number | null;
  poster_path: string | null;
};

export type MovieSuggestion = {
  tmdb_id: number;
  title: string;
  year: number | null;
  overview: string;
  poster_path: string | null;
  genres: string[];
  compatibility_score: number;
  explanation: string;
  trailer_key: string | null;
};

export type SuggestFilters = {
  minYear?: number;
  minRating?: number;
};

/** Autocomplétion : appelée avec debounce depuis MovieSearchInput. */
export async function searchMovies(
  query: string,
  mediaType: MediaType = "movie"
): Promise<MovieSearchResult[]> {
  if (!query.trim()) return [];
  const params = new URLSearchParams({ q: query, media_type: mediaType });
  const res = await fetch(`${API_BASE_URL}/search?${params.toString()}`);
  if (!res.ok) throw new Error("La recherche a échoué");
  return res.json();
}

/** Génère la suggestion à partir des 2 titres choisis (par leur ID TMDB). */
export async function getSuggestions(
  movieId1: number,
  movieId2: number,
  mediaType: MediaType = "movie",
  filters: SuggestFilters = {}
): Promise<MovieSuggestion[]> {
  const res = await fetch(`${API_BASE_URL}/suggest`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      media_type: mediaType,
      movie_id_1: movieId1,
      movie_id_2: movieId2,
      min_year: filters.minYear ?? null,
      min_rating: filters.minRating ?? null,
    }),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new Error(body?.detail ?? "La génération de suggestion a échoué");
  }
  const data = await res.json();
  return data.suggestions;
}

/** Construit l'URL complète d'une affiche TMDB à partir de son poster_path. */
export function posterUrl(posterPath: string | null, size: "w200" | "w500" = "w200") {
  if (!posterPath) return null;
  return `https://image.tmdb.org/t/p/${size}${posterPath}`;
}
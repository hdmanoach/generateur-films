"use client";

import { useEffect, useState } from "react";
import { MovieSearchInput } from "@/components/MovieSearchInput";
import { SuggestionCarousel } from "@/components/SuggestionCarousel";
import {
  getSuggestions,
  type MediaType,
  type MovieSearchResult,
  type MovieSuggestion,
} from "@/lib/api";

type Status = "idle" | "loading" | "error" | "done";

export default function Home() {
  const [mediaType, setMediaType] = useState<MediaType>("movie");
  const [movie1, setMovie1] = useState<MovieSearchResult | null>(null);
  const [movie2, setMovie2] = useState<MovieSearchResult | null>(null);
  const [status, setStatus] = useState<Status>("idle");
  const [errorMessage, setErrorMessage] = useState("");
  const [suggestions, setSuggestions] = useState<MovieSuggestion[]>([]);

  // hasSearched déclenche la transition dès le clic sur le bouton (pas
  // besoin d'attendre la réponse de l'API) : le formulaire glisse vers la
  // gauche immédiatement, et la zone de résultat apparaît à droite.
  const [hasSearched, setHasSearched] = useState(false);
  // "mounted" permet un fondu/glissement d'entrée propre pour la colonne de
  // droite : elle démarre décalée + transparente, puis s'anime vers sa
  // position finale une fois montée dans le DOM.
  const [resultMounted, setResultMounted] = useState(false);

  useEffect(() => {
    if (!hasSearched) {
      setResultMounted(false);
      return;
    }
    const id = setTimeout(() => setResultMounted(true), 20);
    return () => clearTimeout(id);
  }, [hasSearched]);

  const canSubmit = movie1 && movie2 && status !== "loading";
  const isMovie = mediaType === "movie";

  function handleModeChange(next: MediaType) {
    if (next === mediaType) return;
    setMediaType(next);
    setMovie1(null);
    setMovie2(null);
    setSuggestions([]);
    setStatus("idle");
    setHasSearched(false);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!movie1 || !movie2) return;

    setHasSearched(true); // déclenche la transition tout de suite
    setStatus("loading");
    setErrorMessage("");

    try {
      const results = await getSuggestions(movie1.tmdb_id, movie2.tmdb_id, mediaType);
      setSuggestions(results);
      setStatus("done");
    } catch (err) {
      setErrorMessage(
        err instanceof Error ? err.message : "Une erreur inattendue est survenue"
      );
      setStatus("error");
    }
  }

  return (
    <main className="relative z-10 mx-auto min-h-screen max-w-5xl px-6 py-16 sm:py-24">
      <header className="mb-10 text-center">
        <p className="mb-3 font-body text-xs uppercase tracking-[0.2em] text-[var(--color-gold-dim)]">
          Deux {isMovie ? "films" : "séries"} que tu aimes
        </p>
        <h1 className="font-display text-4xl font-black leading-tight text-[var(--color-ink)] sm:text-5xl">
          Croise tes goûts,
          <br />
          trouve ta prochaine {isMovie ? "séance" : "série"}.
        </h1>
      </header>

      {/* Conteneur à deux zones : centré avec le seul formulaire au départ,
          puis formulaire + résultat côte à côte une fois la recherche lancée.
          Sur petits écrans, la zone de résultat passe sous le formulaire
          plutôt qu'à droite (lg:flex-row). */}
      <div className="flex flex-col items-center gap-8 lg:flex-row lg:items-start lg:justify-center">
        <div className="flex w-full max-w-xl flex-shrink-0 flex-col gap-5">
          {/* Mode séparé : Films OU Séries, jamais mélangés dans une même recherche */}
          <div
            role="radiogroup"
            aria-label="Type de contenu"
            className="flex justify-center gap-2"
          >
            {(["movie", "tv"] as MediaType[]).map((type) => (
              <button
                key={type}
                type="button"
                role="radio"
                aria-checked={mediaType === type}
                onClick={() => handleModeChange(type)}
                className={`rounded-full px-5 py-2 font-body text-sm font-medium transition ${
                  mediaType === type
                    ? "bg-[var(--color-gold)] text-[var(--color-bg)]"
                    : "border border-[var(--color-line)] text-[var(--color-ink-muted)] hover:border-[var(--color-gold-dim)]"
                }`}
              >
                {type === "movie" ? "Films" : "Séries"}
              </button>
            ))}
          </div>

          <form
            onSubmit={handleSubmit}
            className="flex flex-col gap-5 rounded-2xl border border-[var(--color-line)]
                       bg-[var(--color-bg-raised)]/40 p-6 sm:p-8"
          >
            <MovieSearchInput
              label={`Premier·e ${isMovie ? "film" : "série"}`}
              placeholder={isMovie ? "Ex. Interstellar" : "Ex. Breaking Bad"}
              mediaType={mediaType}
              onSelect={setMovie1}
            />
            <MovieSearchInput
              label={`Deuxième ${isMovie ? "film" : "série"}`}
              placeholder={isMovie ? "Ex. Blade Runner 2049" : "Ex. Dark"}
              mediaType={mediaType}
              onSelect={setMovie2}
            />

            <button
              type="submit"
              disabled={!canSubmit}
              className="mt-2 rounded-lg bg-[var(--color-gold)] px-6 py-3 font-display text-lg font-semibold
                         text-[var(--color-bg)] transition hover:brightness-110
                         disabled:cursor-not-allowed disabled:bg-[var(--color-line)] disabled:text-[var(--color-ink-muted)]"
            >
              {status === "loading"
                ? "On croise les pellicules…"
                : `Trouver ma prochaine ${isMovie ? "séance" : "série"}`}
            </button>
          </form>
        </div>

        {/* Zone de résultat : montée seulement après le premier clic sur
            "Trouver", avec une transition d'entrée (fondu + léger glissement
            depuis la droite) pilotée par resultMounted. */}
        {hasSearched && (
          <div
            className={`w-full max-w-md transition-all duration-700 ease-out ${
              resultMounted ? "translate-x-0 opacity-100" : "translate-x-6 opacity-0"
            }`}
          >
            {status === "loading" && (
              <div className="flex items-center justify-center rounded-2xl border border-[var(--color-line)] bg-[var(--color-bg-raised)]/40 p-10">
                <p className="font-body text-sm text-[var(--color-ink-muted)]">
                  On croise les pellicules…
                </p>
              </div>
            )}

            {status === "error" && (
              <p
                role="alert"
                className="rounded-lg border border-red-900/50 bg-red-950/30 px-4 py-3 text-sm text-red-300"
              >
                {errorMessage} — vérifie ta sélection ou réessaie dans un instant.
              </p>
            )}

            {status === "done" && <SuggestionCarousel suggestions={suggestions} />}
          </div>
        )}
      </div>
    </main>
  );
}
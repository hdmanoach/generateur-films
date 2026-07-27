"use client";

import { useState } from "react";
import { SuggestionCard } from "./SuggestionCard";
import type { MovieSuggestion } from "@/lib/api";

type Props = {
  suggestions: MovieSuggestion[];
};

/**
 * Affiche une suggestion à la fois, avec des flèches pour naviguer entre
 * les résultats (plutôt qu'une longue liste empilée). Les points en bas
 * indiquent la position courante dans le carrousel.
 */
export function SuggestionCarousel({ suggestions }: Props) {
  const [index, setIndex] = useState(0);

  if (suggestions.length === 0) {
    return (
      <p className="text-center text-[var(--color-ink-muted)]">
        Aucune suggestion trouvée pour cette combinaison — essaie deux autres
        titres.
      </p>
    );
  }

  const current = suggestions[index];

  function goPrev() {
    setIndex((i) => (i - 1 + suggestions.length) % suggestions.length);
  }

  function goNext() {
    setIndex((i) => (i + 1) % suggestions.length);
  }

  return (
    <div className="w-full">
      {/* key force un re-render propre à chaque changement, avec un léger
          fondu pour adoucir la transition entre deux suggestions */}
      <div key={current.tmdb_id} className="animate-[fadeIn_0.35s_ease-out]">
        <SuggestionCard suggestion={current} rank={index + 1} />
      </div>

      {suggestions.length > 1 && (
        <div className="mt-4 flex items-center justify-center gap-4">
          <button
            type="button"
            onClick={goPrev}
            aria-label="Suggestion précédente"
            className="flex h-9 w-9 items-center justify-center rounded-full border border-[var(--color-line)]
                       text-[var(--color-ink)] transition hover:border-[var(--color-gold)] hover:text-[var(--color-gold)]"
          >
            ←
          </button>

          <div className="flex gap-1.5" role="tablist" aria-label="Position dans le carrousel">
            {suggestions.map((s, i) => (
              <button
                key={s.tmdb_id}
                type="button"
                role="tab"
                aria-selected={i === index}
                aria-label={`Voir la suggestion ${i + 1}`}
                onClick={() => setIndex(i)}
                className={`h-1.5 w-1.5 rounded-full transition ${
                  i === index ? "bg-[var(--color-gold)]" : "bg-[var(--color-line)]"
                }`}
              />
            ))}
          </div>

          <button
            type="button"
            onClick={goNext}
            aria-label="Suggestion suivante"
            className="flex h-9 w-9 items-center justify-center rounded-full border border-[var(--color-line)]
                       text-[var(--color-ink)] transition hover:border-[var(--color-gold)] hover:text-[var(--color-gold)]"
          >
            →
          </button>
        </div>
      )}
    </div>
  );
}
"use client";

import { useEffect, useRef, useState } from "react";
import { searchMovies, posterUrl, type MovieSearchResult, type MediaType } from "@/lib/api";

type Props = {
  label: string;
  placeholder: string;
  mediaType: MediaType;
  onSelect: (movie: MovieSearchResult | null) => void;
};

/**
 * Champ de saisie avec autocomplétion.
 *
 * Point important (comme discuté dans le cadrage du projet) : ce composant
 * ne renvoie jamais le texte tapé au parent, seulement l'objet complet
 * (avec son tmdb_id) une fois que l'utilisateur a cliqué un résultat.
 * Ça élimine toute ambiguïté de titre côté backend.
 *
 * Le mediaType ("movie" ou "tv") vient du mode choisi par l'utilisateur
 * (Films OU Séries) avant de commencer sa recherche — voir page.tsx.
 *
 * Le debounce de 300ms évite d'appeler l'API à chaque frappe de touche.
 */
export function MovieSearchInput({ label, placeholder, mediaType, onSelect }: Props) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<MovieSearchResult[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [selected, setSelected] = useState<MovieSearchResult | null>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Si l'utilisateur change de mode (Films <-> Séries), la sélection en
  // cours n'a plus de sens : on réinitialise le champ.
  useEffect(() => {
    setQuery("");
    setSelected(null);
    setResults([]);
    onSelect(null);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mediaType]);

  useEffect(() => {
    // Si un titre est déjà sélectionné et que l'utilisateur retape, on
    // considère la sélection annulée tant qu'il n'en reprend pas une nouvelle.
    if (selected && query !== selected.title) {
      setSelected(null);
      onSelect(null);
    }

    if (debounceRef.current) clearTimeout(debounceRef.current);

    if (!query.trim() || (selected && query === selected.title)) {
      setResults([]);
      return;
    }

    debounceRef.current = setTimeout(async () => {
      setIsLoading(true);
      try {
        const data = await searchMovies(query, mediaType);
        setResults(data);
        setIsOpen(true);
      } catch {
        setResults([]);
      } finally {
        setIsLoading(false);
      }
    }, 300); // debounce ~300ms, cf. cadrage du projet

    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [query, mediaType]);

  // Ferme le menu déroulant si on clique en dehors du composant
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (
        containerRef.current &&
        !containerRef.current.contains(e.target as Node)
      ) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  function handlePick(movie: MovieSearchResult) {
    setSelected(movie);
    setQuery(movie.title);
    setIsOpen(false);
    onSelect(movie);
  }

  return (
    <div ref={containerRef} className="relative">
      <label className="mb-2 block font-body text-sm tracking-wide text-[var(--color-ink-muted)]">
        {label}
      </label>

      <div className="relative">
        <input
          type="text"
          value={query}
          placeholder={placeholder}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => results.length > 0 && setIsOpen(true)}
          className="w-full rounded-lg border border-[var(--color-line)] bg-[var(--color-bg-raised)]
                     px-4 py-3 font-body text-base text-[var(--color-ink)] placeholder:text-[var(--color-ink-muted)]/60
                     outline-none transition focus:border-[var(--color-gold)] focus:ring-1 focus:ring-[var(--color-gold)]"
        />
        {selected && (
          <span
            aria-hidden
            className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--color-velvet-bright)]"
            title="Film reconnu"
          >
            ✓
          </span>
        )}
      </div>

      {isOpen && (isLoading || results.length > 0) && (
        <ul
          className="absolute z-20 mt-2 w-full overflow-hidden rounded-lg border border-[var(--color-line)]
                     bg-[var(--color-bg-raised)] shadow-xl"
          role="listbox"
        >
          {isLoading && (
            <li className="px-4 py-3 text-sm text-[var(--color-ink-muted)]">
              Recherche…
            </li>
          )}
          {!isLoading &&
            results.map((movie) => (
              <li key={movie.tmdb_id}>
                <button
                  type="button"
                  role="option"
                  onClick={() => handlePick(movie)}
                  className="flex w-full items-center gap-3 px-4 py-2.5 text-left transition
                             hover:bg-[var(--color-velvet)]/20 focus:bg-[var(--color-velvet)]/20 focus:outline-none"
                >
                  {posterUrl(movie.poster_path) ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img
                      src={posterUrl(movie.poster_path)!}
                      alt=""
                      className="h-12 w-8 flex-shrink-0 rounded object-cover"
                    />
                  ) : (
                    <div className="h-12 w-8 flex-shrink-0 rounded bg-[var(--color-line)]" />
                  )}
                  <span className="text-sm text-[var(--color-ink)]">
                    {movie.title}
                    {movie.year && (
                      <span className="text-[var(--color-ink-muted)]">
                        {" "}
                        · {movie.year}
                      </span>
                    )}
                  </span>
                </button>
              </li>
            ))}
        </ul>
      )}
    </div>
  );
}

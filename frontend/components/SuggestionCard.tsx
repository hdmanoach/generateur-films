import { posterUrl, type MovieSuggestion } from "@/lib/api";
import { MatchDial } from "./MatchDial";

export function SuggestionCard({
  suggestion,
  rank,
}: {
  suggestion: MovieSuggestion;
  rank: number;
}) {
  const poster = posterUrl(suggestion.poster_path, "w500");

  return (
    <article
      className="flex gap-4 rounded-xl border border-[var(--color-line)] bg-[var(--color-bg-raised)]
                 p-4 sm:gap-5 sm:p-5"
    >
      <div className="w-20 flex-shrink-0 sm:w-28">
        {poster ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={poster}
            alt={`Affiche de ${suggestion.title}`}
            className="aspect-[2/3] w-full rounded-lg object-cover"
          />
        ) : (
          <div className="aspect-[2/3] w-full rounded-lg bg-[var(--color-line)]" />
        )}
      </div>

      <div className="flex flex-1 flex-col gap-2">
        <div className="flex items-start justify-between gap-3">
          <div>
            <span className="font-body text-xs uppercase tracking-widest text-[var(--color-gold-dim)]">
              Trouvaille n°{rank}
            </span>
            <h3 className="font-display text-xl font-semibold leading-tight text-[var(--color-ink)] sm:text-2xl">
              {suggestion.title}
              {suggestion.year && (
                <span className="ml-2 font-body text-sm font-normal text-[var(--color-ink-muted)]">
                  {suggestion.year}
                </span>
              )}
            </h3>
          </div>
          <MatchDial score={suggestion.compatibility_score} />
        </div>

        <p className="font-body text-sm leading-relaxed text-[var(--color-ink-muted)]">
          {suggestion.explanation}
        </p>

        {suggestion.overview && (
          <p className="font-body text-sm leading-relaxed text-[var(--color-ink)]/80 line-clamp-3">
            {suggestion.overview}
          </p>
        )}

        {suggestion.trailer_key && (
          <div className="mt-1 aspect-video w-full overflow-hidden rounded-lg border border-[var(--color-line)]">
            <iframe
              src={`https://www.youtube.com/embed/${suggestion.trailer_key}`}
              title={`Bande-annonce de ${suggestion.title}`}
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
              className="h-full w-full"
              loading="lazy"
            />
          </div>
        )}
      </div>
    </article>
  );
}
type Props = {
  score: number; // 0-100
};

/**
 * Élément signature du design : une jauge circulaire façon bobine de
 * pellicule, plutôt qu'un simple pourcentage plat. Le score se lit d'un
 * coup d'œil, et le motif rappelle visuellement l'univers du cinéma.
 */
export function MatchDial({ score }: Props) {
  const radius = 34;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;

  return (
    <div className="relative flex h-20 w-20 flex-shrink-0 items-center justify-center">
      <svg width="80" height="80" viewBox="0 0 80 80" className="-rotate-90">
        <circle
          cx="40"
          cy="40"
          r={radius}
          fill="none"
          stroke="var(--color-line)"
          strokeWidth="6"
        />
        <circle
          cx="40"
          cy="40"
          r={radius}
          fill="none"
          stroke="var(--color-gold)"
          strokeWidth="6"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
        />
      </svg>
      <span className="absolute font-display text-lg font-semibold text-[var(--color-ink)]">
        {score}
      </span>
    </div>
  );
}

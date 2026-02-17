import type { KeyFigure } from "@/types";

type KeyFigureCardProps = {
  figure: KeyFigure;
  accentColor: string;
};

export function KeyFigureCard({ figure, accentColor }: KeyFigureCardProps) {
  const yearRange =
    figure.birthYear || figure.deathYear
      ? `${figure.birthYear ?? "?"}–${figure.deathYear ?? "?"}`
      : null;

  return (
    <div
      className="rounded-lg border-2 bg-[hsl(var(--card))] p-4 transition-all duration-200 hover:shadow-md"
      style={{ borderLeftColor: accentColor, borderLeftWidth: "4px" }}
    >
      <div className="flex flex-col gap-2">
        <div>
          <h4 className="font-heading text-lg font-bold text-[hsl(var(--foreground))]">
            {figure.name}
          </h4>
          {yearRange && (
            <p
              className="text-xs font-medium mt-0.5"
              style={{ color: accentColor }}
            >
              {yearRange}
            </p>
          )}
        </div>
        <p className="text-sm font-medium text-[hsl(var(--muted-foreground))]">
          {figure.title}
        </p>
        <p className="text-sm text-[hsl(var(--foreground))] leading-relaxed">
          {figure.description}
        </p>
      </div>
    </div>
  );
}

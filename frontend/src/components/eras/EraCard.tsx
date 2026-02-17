import { useNavigate } from "react-router-dom";
import type { Era } from "@/types";
import { cn } from "@/lib/utils";

type EraCardProps = {
  era: Era;
  onClick?: () => void;
};

export function EraCard({ era, onClick }: EraCardProps) {
  const navigate = useNavigate();

  const handleClick = () => {
    if (onClick) {
      onClick();
    } else {
      navigate(`/eras/${era.slug}`);
    }
  };

  return (
    <button
      onClick={handleClick}
      className={cn(
        "w-full text-left rounded-lg border-2 bg-[hsl(var(--card))] p-6 transition-all duration-200",
        "hover:shadow-lg hover:scale-[1.02] focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
      )}
      style={{ borderTopColor: era.color }}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <h3 className="font-heading text-xl font-bold text-[hsl(var(--foreground))] mb-1">
            {era.name}
          </h3>
          <p className="text-sm text-[hsl(var(--muted-foreground))] mb-3">
            {era.startYear}–{era.endYear ?? "present"}
          </p>
          <p className="text-sm text-[hsl(var(--foreground))] leading-relaxed">
            {era.summary}
          </p>
        </div>
        <div
          className="w-1 h-full rounded-full"
          style={{ backgroundColor: era.color }}
        />
      </div>
    </button>
  );
}

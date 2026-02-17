import type { KeyEvent } from "@/types";

type KeyEventTimelineProps = {
  events: KeyEvent[];
  accentColor: string;
};

export function KeyEventTimeline({ events, accentColor }: KeyEventTimelineProps) {
  if (!events || events.length === 0) {
    return (
      <p className="text-sm text-[hsl(var(--muted-foreground))] italic">
        No key events recorded for this era.
      </p>
    );
  }

  const sortedEvents = [...events].sort((a, b) => a.year - b.year);

  return (
    <div className="relative">
      {/* Vertical line */}
      <div
        className="absolute left-0 top-0 bottom-0 w-0.5 rounded-full"
        style={{ backgroundColor: `${accentColor}40` }}
      />

      <div className="space-y-6 pl-8">
        {sortedEvents.map((event) => (
          <div key={event.id} className="relative">
            {/* Dot */}
            <div
              className="absolute -left-8 top-1 w-3 h-3 rounded-full border-2 border-[hsl(var(--background))]"
              style={{ backgroundColor: accentColor }}
            />

            <div>
              <div className="flex items-baseline gap-2 mb-1">
                <span
                  className="text-sm font-semibold"
                  style={{ color: accentColor }}
                >
                  {event.year}
                </span>
                <h4 className="font-heading font-bold text-[hsl(var(--foreground))]">
                  {event.title}
                </h4>
              </div>
              <p className="text-sm text-[hsl(var(--muted-foreground))] leading-relaxed">
                {event.description}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

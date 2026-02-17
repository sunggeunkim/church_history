import { useEffect } from "react";
import { useEraStore } from "@/stores/eraStore";
import { Timeline } from "@/components/eras/Timeline";
import { EraCard } from "@/components/eras/EraCard";
import { KeyEventTimeline } from "@/components/eras/KeyEventTimeline";
import { KeyFigureCard } from "@/components/eras/KeyFigureCard";

export function ErasPage() {
  const { eras, selectedEra, isLoading, error, fetchEras, selectEra } =
    useEraStore();

  useEffect(() => {
    fetchEras();
  }, [fetchEras]);

  if (isLoading && eras.length === 0) {
    return (
      <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto">
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-primary-600 border-r-transparent" />
            <p className="mt-4 text-sm text-[hsl(var(--muted-foreground))]">
              Loading eras...
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto">
        <div className="rounded-lg border border-red-200 bg-red-50 dark:border-red-900 dark:bg-red-950 p-6">
          <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
        </div>
      </div>
    );
  }

  const sortedEras = [...eras].sort((a, b) => a.order - b.order);

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="font-heading text-3xl font-bold tracking-tight mb-2">
          Church History Eras
        </h1>
        <p className="text-[hsl(var(--muted-foreground))]">
          Explore the major periods of Christian history from the early church
          to the present day.
        </p>
      </div>

      {/* Timeline */}
      <div className="mb-12 rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-6">
        <h2 className="font-heading text-lg font-semibold mb-6 text-[hsl(var(--foreground))]">
          Historical Timeline
        </h2>
        <Timeline
          eras={sortedEras}
          selectedEra={selectedEra}
          onEraClick={selectEra}
        />
      </div>

      {/* Selected Era Detail Panel */}
      {selectedEra && (
        <div
          className="mb-12 rounded-lg border-2 bg-[hsl(var(--card))] p-6 shadow-lg transition-all duration-300"
          style={{ borderTopColor: selectedEra.color, borderTopWidth: "4px" }}
        >
          <div className="flex items-start justify-between mb-4">
            <div>
              <h2 className="font-heading text-2xl font-bold text-[hsl(var(--foreground))]">
                {selectedEra.name}
              </h2>
              <p
                className="text-sm font-medium mt-1"
                style={{ color: selectedEra.color }}
              >
                {selectedEra.startYear}–
                {selectedEra.endYear ?? "present"}
              </p>
            </div>
            <button
              onClick={() => selectEra(null)}
              className="text-sm text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))] transition-colors"
              aria-label="Close details"
            >
              ✕
            </button>
          </div>

          <p className="text-[hsl(var(--foreground))] leading-relaxed mb-8">
            {selectedEra.description}
          </p>

          <div className="grid md:grid-cols-2 gap-8">
            {/* Key Events */}
            <div>
              <h3 className="font-heading text-lg font-semibold mb-4 text-[hsl(var(--foreground))]">
                Key Events
              </h3>
              <KeyEventTimeline
                events={selectedEra.keyEvents || []}
                accentColor={selectedEra.color}
              />
            </div>

            {/* Key Figures */}
            <div>
              <h3 className="font-heading text-lg font-semibold mb-4 text-[hsl(var(--foreground))]">
                Key Figures
              </h3>
              {selectedEra.keyFigures && selectedEra.keyFigures.length > 0 ? (
                <div className="space-y-4">
                  {selectedEra.keyFigures.map((figure) => (
                    <KeyFigureCard
                      key={figure.id}
                      figure={figure}
                      accentColor={selectedEra.color}
                    />
                  ))}
                </div>
              ) : (
                <p className="text-sm text-[hsl(var(--muted-foreground))] italic">
                  No key figures recorded for this era.
                </p>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Era Cards Grid */}
      <div>
        <h2 className="font-heading text-lg font-semibold mb-6 text-[hsl(var(--foreground))]">
          All Eras
        </h2>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {sortedEras.map((era) => (
            <EraCard key={era.id} era={era} />
          ))}
        </div>
      </div>
    </div>
  );
}

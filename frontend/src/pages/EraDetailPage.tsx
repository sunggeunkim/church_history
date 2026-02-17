import { useEffect, useMemo } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { useEraStore } from "@/stores/eraStore";
import { KeyEventTimeline } from "@/components/eras/KeyEventTimeline";
import { KeyFigureCard } from "@/components/eras/KeyFigureCard";

export function EraDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();
  const { eras, selectedEra, isLoading, error, fetchEra, fetchEras } =
    useEraStore();

  useEffect(() => {
    if (slug) {
      fetchEra(slug);
    }
    if (eras.length === 0) {
      fetchEras();
    }
  }, [slug, fetchEra, fetchEras, eras.length]);

  const { previousEra, nextEra } = useMemo(() => {
    if (!selectedEra || eras.length === 0) {
      return { previousEra: null, nextEra: null };
    }

    const sortedEras = [...eras].sort((a, b) => a.order - b.order);
    const currentIndex = sortedEras.findIndex(
      (era) => era.id === selectedEra.id
    );

    return {
      previousEra: currentIndex > 0 ? sortedEras[currentIndex - 1] : null,
      nextEra:
        currentIndex < sortedEras.length - 1
          ? sortedEras[currentIndex + 1]
          : null,
    };
  }, [selectedEra, eras]);

  if (isLoading) {
    return (
      <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto">
        <div className="flex items-center justify-center py-12">
          <div className="text-center">
            <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-primary-600 border-r-transparent" />
            <p className="mt-4 text-sm text-[hsl(var(--muted-foreground))]">
              Loading era details...
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (error || !selectedEra) {
    return (
      <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto">
        <div className="rounded-lg border border-red-200 bg-red-50 dark:border-red-900 dark:bg-red-950 p-6">
          <p className="text-sm text-red-800 dark:text-red-200 mb-4">
            {error || "Era not found"}
          </p>
          <Link
            to="/eras"
            className="text-sm font-medium text-red-800 dark:text-red-200 underline hover:no-underline"
          >
            ← Back to all eras
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto">
      {/* Navigation */}
      <div className="mb-6">
        <Link
          to="/eras"
          className="inline-flex items-center gap-2 text-sm text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))] transition-colors"
        >
          <ChevronLeft className="h-4 w-4" />
          Back to all eras
        </Link>
      </div>

      {/* Hero Section */}
      <div
        className="mb-8 rounded-lg border-2 bg-gradient-to-br from-[hsl(var(--card))] to-[hsl(var(--muted))] p-8 shadow-lg"
        style={{ borderTopColor: selectedEra.color, borderTopWidth: "4px" }}
      >
        <h1 className="font-heading text-4xl font-bold text-[hsl(var(--foreground))] mb-2">
          {selectedEra.name}
        </h1>
        <p
          className="text-lg font-semibold mb-4"
          style={{ color: selectedEra.color }}
        >
          {selectedEra.startYear}–{selectedEra.endYear ?? "present"}
        </p>
        <p className="text-[hsl(var(--foreground))] leading-relaxed max-w-4xl">
          {selectedEra.description}
        </p>
      </div>

      {/* Content Grid */}
      <div className="grid lg:grid-cols-2 gap-8 mb-8">
        {/* Key Events */}
        <div className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-6">
          <h2 className="font-heading text-2xl font-bold mb-6 text-[hsl(var(--foreground))]">
            Key Events
          </h2>
          <KeyEventTimeline
            events={selectedEra.keyEvents || []}
            accentColor={selectedEra.color}
          />
        </div>

        {/* Key Figures */}
        <div className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-6">
          <h2 className="font-heading text-2xl font-bold mb-6 text-[hsl(var(--foreground))]">
            Key Figures
          </h2>
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

      {/* Previous/Next Navigation */}
      <div className="flex items-center justify-between border-t border-[hsl(var(--border))] pt-6">
        <div className="flex-1">
          {previousEra ? (
            <button
              onClick={() => navigate(`/eras/${previousEra.slug}`)}
              className="group inline-flex items-center gap-2 text-sm text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))] transition-colors"
            >
              <ChevronLeft className="h-4 w-4 transition-transform group-hover:-translate-x-1" />
              <div className="text-left">
                <p className="text-xs">Previous Era</p>
                <p className="font-medium">{previousEra.name}</p>
              </div>
            </button>
          ) : (
            <div />
          )}
        </div>

        <div className="flex-1 text-right">
          {nextEra ? (
            <button
              onClick={() => navigate(`/eras/${nextEra.slug}`)}
              className="group inline-flex items-center gap-2 text-sm text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))] transition-colors"
            >
              <div className="text-right">
                <p className="text-xs">Next Era</p>
                <p className="font-medium">{nextEra.name}</p>
              </div>
              <ChevronRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
            </button>
          ) : (
            <div />
          )}
        </div>
      </div>
    </div>
  );
}

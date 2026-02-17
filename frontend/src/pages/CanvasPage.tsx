import { useEffect, useState } from "react";
import { Loader2, MessageSquare, X } from "lucide-react";
import { useSearchParams } from "react-router-dom";
import { useEraStore } from "@/stores/eraStore";
import { useMediaQuery } from "@/hooks/useMediaQuery";
import { CanvasOverviewBar } from "@/components/canvas/CanvasOverviewBar";
import { CanvasTimeline } from "@/components/canvas/CanvasTimeline";
import { CanvasChatPanel } from "@/components/canvas/CanvasChatPanel";
import { cn } from "@/lib/utils";
import type { Era } from "@/types";

export function CanvasPage() {
  const {
    timelineData,
    isLoadingTimeline,
    expandedEraId,
    error,
    fetchTimeline,
    toggleExpanded,
    setExpandedEra,
  } = useEraStore();

  const isDesktop = useMediaQuery("(min-width: 1024px)");
  const [selectedEra, setSelectedEra] = useState<Era | null>(null);
  const [chatOpen, setChatOpen] = useState(false);
  const [searchParams] = useSearchParams();

  // Fetch timeline data on mount
  useEffect(() => {
    fetchTimeline();
  }, [fetchTimeline]);

  // Handle ?era=slug query parameter
  useEffect(() => {
    const eraSlug = searchParams.get("era");
    if (eraSlug && timelineData) {
      const era = timelineData.find((e) => e.slug === eraSlug);
      if (era) {
        setSelectedEra(era);
        setExpandedEra(era.id);
        if (isDesktop) setChatOpen(true);
      }
    }
  }, [searchParams, timelineData, setExpandedEra, isDesktop]);

  const handleEraOverviewClick = (era: Era) => {
    setExpandedEra(era.id);
    setSelectedEra(era);
    // Scroll to the era block
    const element = document.getElementById(`era-block-${era.id}`);
    element?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  const handleChatClick = (era: Era) => {
    setSelectedEra(era);
    setChatOpen(true);
  };

  if (isLoadingTimeline && !timelineData) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="text-center">
          <Loader2 className="mx-auto h-8 w-8 animate-spin text-[hsl(var(--muted-foreground))]" />
          <p className="mt-4 text-sm text-[hsl(var(--muted-foreground))]">
            Loading timeline...
          </p>
        </div>
      </div>
    );
  }

  if (error && !timelineData) {
    return (
      <div className="flex h-full items-center justify-center px-4">
        <div className="rounded-lg border border-red-200 bg-red-50 dark:border-red-900 dark:bg-red-950 p-6 text-center">
          <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
        </div>
      </div>
    );
  }

  const eras = timelineData || [];

  return (
    <div className="flex h-full flex-col overflow-hidden">
      {/* Overview bar */}
      {eras.length > 0 && (
        <CanvasOverviewBar
          eras={eras}
          selectedEraId={selectedEra?.id ?? null}
          onEraClick={handleEraOverviewClick}
        />
      )}

      {/* Split panel */}
      <div className="flex flex-1 overflow-hidden">
        {/* Timeline panel */}
        <div
          className={cn(
            "overflow-y-auto",
            isDesktop && chatOpen ? "w-[55%] border-r border-[hsl(var(--border))]" : "w-full",
          )}
        >
          <CanvasTimeline
            eras={eras}
            expandedEraId={expandedEraId}
            selectedEraId={selectedEra?.id ?? null}
            onToggleExpand={(eraId) => {
              toggleExpanded(eraId);
              const era = eras.find((e) => e.id === eraId);
              if (era) setSelectedEra(era);
            }}
            onChatClick={handleChatClick}
          />
        </div>

        {/* Chat panel - desktop */}
        {isDesktop && chatOpen && (
          <div className="flex w-[45%] flex-col overflow-hidden">
            <CanvasChatPanel selectedEra={selectedEra} />
          </div>
        )}
      </div>

      {/* Mobile floating chat button */}
      {!isDesktop && selectedEra && !chatOpen && (
        <button
          onClick={() => setChatOpen(true)}
          className={cn(
            "fixed bottom-20 right-4 z-30 flex items-center gap-2 rounded-full px-4 py-3 text-sm font-medium text-white shadow-lg",
            "transition-transform hover:scale-105",
            "focus:outline-none focus:ring-2 focus:ring-[hsl(var(--ring))] focus:ring-offset-2",
          )}
          style={{ backgroundColor: selectedEra.color }}
        >
          <MessageSquare className="h-4 w-4" />
          Chat about {selectedEra.name}
        </button>
      )}

      {/* Mobile chat overlay */}
      {!isDesktop && chatOpen && (
        <div className="fixed inset-0 z-40 flex flex-col bg-[hsl(var(--background))]">
          <div className="flex items-center justify-between border-b border-[hsl(var(--border))] px-4 py-3">
            <h2 className="font-heading text-lg font-semibold text-[hsl(var(--foreground))]">
              Chat
            </h2>
            <button
              onClick={() => setChatOpen(false)}
              className="rounded-lg p-1.5 text-[hsl(var(--muted-foreground))] hover:bg-[hsl(var(--muted))] hover:text-[hsl(var(--foreground))]"
              aria-label="Close chat"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
          <div className="flex-1 overflow-hidden">
            <CanvasChatPanel selectedEra={selectedEra} />
          </div>
        </div>
      )}
    </div>
  );
}

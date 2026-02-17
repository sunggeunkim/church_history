import { motion } from "motion/react";
import type { KeyEvent } from "@/types";

type CanvasEventListProps = {
  events: KeyEvent[];
  accentColor: string;
};

const containerVariants = {
  hidden: {},
  visible: {
    transition: { staggerChildren: 0.05 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, x: -12 },
  visible: { opacity: 1, x: 0 },
};

export function CanvasEventList({ events, accentColor }: CanvasEventListProps) {
  if (!events || events.length === 0) return null;

  const sorted = [...events].sort((a, b) => a.year - b.year);

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="relative"
    >
      {/* Vertical line */}
      <div
        className="absolute left-0 top-0 bottom-0 w-0.5 rounded-full"
        style={{ backgroundColor: `${accentColor}40` }}
      />
      <div className="space-y-4 pl-6">
        {sorted.map((event) => (
          <motion.div key={event.id} variants={itemVariants} className="relative">
            <div
              className="absolute -left-6 top-1.5 h-2.5 w-2.5 rounded-full border-2 border-[hsl(var(--background))]"
              style={{ backgroundColor: accentColor }}
            />
            <div>
              <div className="flex items-baseline gap-2">
                <span
                  className="text-xs font-bold"
                  style={{ color: accentColor }}
                >
                  {event.year}
                </span>
                <h4 className="text-sm font-semibold text-[hsl(var(--foreground))]">
                  {event.title}
                </h4>
              </div>
              {event.description && (
                <p className="mt-0.5 text-xs text-[hsl(var(--muted-foreground))] leading-relaxed">
                  {event.description}
                </p>
              )}
            </div>
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}

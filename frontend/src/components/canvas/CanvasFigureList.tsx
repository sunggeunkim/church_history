import { motion } from "motion/react";
import type { KeyFigure } from "@/types";

type CanvasFigureListProps = {
  figures: KeyFigure[];
  accentColor: string;
};

const containerVariants = {
  hidden: {},
  visible: {
    transition: { staggerChildren: 0.07 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 8 },
  visible: { opacity: 1, y: 0 },
};

export function CanvasFigureList({
  figures,
  accentColor,
}: CanvasFigureListProps) {
  if (!figures || figures.length === 0) return null;

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="grid gap-3 sm:grid-cols-2"
    >
      {figures.map((figure) => {
        const yearRange =
          figure.birthYear || figure.deathYear
            ? `${figure.birthYear ?? "?"}–${figure.deathYear ?? "?"}`
            : null;

        return (
          <motion.div
            key={figure.id}
            variants={itemVariants}
            className="rounded-lg border bg-[hsl(var(--card))] p-3"
            style={{ borderLeftColor: accentColor, borderLeftWidth: "3px" }}
          >
            <h4 className="text-sm font-semibold text-[hsl(var(--foreground))]">
              {figure.name}
            </h4>
            {yearRange && (
              <span
                className="text-[10px] font-medium"
                style={{ color: accentColor }}
              >
                {yearRange}
              </span>
            )}
            {figure.title && (
              <p className="text-xs text-[hsl(var(--muted-foreground))]">
                {figure.title}
              </p>
            )}
          </motion.div>
        );
      })}
    </motion.div>
  );
}

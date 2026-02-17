import { motion } from "motion/react";

type ProgressRingProps = {
  percentage: number;
  size?: number;
};

export function ProgressRing({ percentage, size = 200 }: ProgressRingProps) {
  const strokeWidth = 12;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (percentage / 100) * circumference;

  // Color based on percentage
  const getColor = () => {
    if (percentage < 33) return "rgb(239, 68, 68)"; // red
    if (percentage < 66) return "rgb(251, 191, 36)"; // yellow
    return "rgb(34, 197, 94)"; // green
  };

  return (
    <div className="relative" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="transform -rotate-90">
        {/* Background circle */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke="hsl(var(--muted))"
          strokeWidth={strokeWidth}
        />

        {/* Progress circle */}
        <motion.circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={getColor()}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1.5, ease: "easeInOut" }}
        />
      </svg>

      {/* Center text */}
      <div className="absolute inset-0 flex items-center justify-center">
        <div className="text-center">
          <motion.div
            className="text-4xl font-bold text-[hsl(var(--foreground))]"
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.5, duration: 0.5 }}
          >
            {Math.round(percentage)}%
          </motion.div>
          <div className="text-sm text-[hsl(var(--muted-foreground))]">Complete</div>
        </div>
      </div>
    </div>
  );
}

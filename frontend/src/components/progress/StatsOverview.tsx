import { motion } from "motion/react";
import { Map, MessageSquare, Trophy, Target, Flame, Calendar } from "lucide-react";
import { useEffect, useState } from "react";

type StatsOverviewProps = {
  erasVisited: number;
  totalChatSessions: number;
  totalQuizzes: number;
  averageScore: number;
  currentStreak: number;
  accountAgeDays: number;
};

function StatCard({
  icon: Icon,
  label,
  value,
  delay,
}: {
  icon: React.ElementType;
  label: string;
  value: number;
  delay: number;
}) {
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    let current = 0;
    const increment = value / 30;
    const timer = setInterval(() => {
      current += increment;
      if (current >= value) {
        setDisplayValue(value);
        clearInterval(timer);
      } else {
        setDisplayValue(Math.floor(current));
      }
    }, 30);
    return () => clearInterval(timer);
  }, [value]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.5 }}
      className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-4"
    >
      <div className="flex items-center gap-3">
        <div className="rounded-lg bg-primary-100 dark:bg-primary-900 p-2">
          <Icon className="h-5 w-5 text-primary-700 dark:text-primary-300" />
        </div>
        <div className="flex-1">
          <div className="text-2xl font-bold text-[hsl(var(--foreground))]">{displayValue}</div>
          <div className="text-sm text-[hsl(var(--muted-foreground))]">{label}</div>
        </div>
      </div>
    </motion.div>
  );
}

export function StatsOverview({
  erasVisited,
  totalChatSessions,
  totalQuizzes,
  averageScore,
  currentStreak,
  accountAgeDays,
}: StatsOverviewProps) {
  return (
    <div className="grid grid-cols-2 gap-4 md:grid-cols-3">
      <StatCard icon={Map} label="Eras Explored" value={erasVisited} delay={0.1} />
      <StatCard icon={MessageSquare} label="Chat Sessions" value={totalChatSessions} delay={0.2} />
      <StatCard icon={Trophy} label="Quizzes Taken" value={totalQuizzes} delay={0.3} />
      <StatCard icon={Target} label="Average Score" value={Math.round(averageScore)} delay={0.4} />
      <StatCard icon={Flame} label="Current Streak" value={currentStreak} delay={0.5} />
      <StatCard icon={Calendar} label="Days Learning" value={accountAgeDays} delay={0.6} />
    </div>
  );
}

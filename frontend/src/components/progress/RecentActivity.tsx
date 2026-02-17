import { MapPin, MessageSquare, Trophy } from "lucide-react";
import type { ActivityItem } from "@/types";

type RecentActivityProps = {
  activities: ActivityItem[];
};

function getActivityIcon(type: string) {
  switch (type) {
    case "visit":
      return MapPin;
    case "chat":
      return MessageSquare;
    case "quiz":
      return Trophy;
    default:
      return MapPin;
  }
}

function formatTimestamp(timestamp: string) {
  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return "Just now";
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  return date.toLocaleDateString();
}

export function RecentActivity({ activities }: RecentActivityProps) {
  if (activities.length === 0) {
    return (
      <div className="rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-6 text-center">
        <p className="text-[hsl(var(--muted-foreground))]">No recent activity yet.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {activities.slice(0, 10).map((activity, index) => {
        const Icon = getActivityIcon(activity.type);
        return (
          <div key={index} className="flex items-start gap-3">
            {/* Timeline dot */}
            <div className="relative mt-1 flex-shrink-0">
              <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary-100 dark:bg-primary-900">
                <Icon className="h-4 w-4 text-primary-700 dark:text-primary-300" />
              </div>
              {index < activities.length - 1 && (
                <div className="absolute left-4 top-8 h-full w-0.5 bg-[hsl(var(--border))]" />
              )}
            </div>

            {/* Content */}
            <div className="flex-1 pt-1">
              <p className="text-sm text-[hsl(var(--foreground))]">
                <span className="font-semibold">{activity.eraName}</span>
                <span className="text-[hsl(var(--muted-foreground))]">
                  {" "}
                  - {activity.description}
                </span>
              </p>
              <p className="mt-0.5 text-xs text-[hsl(var(--muted-foreground))]">
                {formatTimestamp(activity.timestamp)}
              </p>
            </div>
          </div>
        );
      })}
    </div>
  );
}

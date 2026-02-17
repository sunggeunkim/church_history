import { Share2, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { useSharingStore } from "@/stores/sharingStore";

type ShareButtonProps = {
  shareType: "achievement" | "quiz_result" | "progress";
  achievementId?: number;
  quizId?: number;
  variant?: "icon" | "button";
  label?: string;
};

export function ShareButton({
  shareType,
  achievementId,
  quizId,
  variant = "icon",
  label = "Share",
}: ShareButtonProps) {
  const { createShareLink, isCreating } = useSharingStore();

  const handleClick = () => {
    createShareLink(shareType, achievementId, quizId);
  };

  if (variant === "icon") {
    return (
      <button
        onClick={handleClick}
        disabled={isCreating}
        className={cn(
          "rounded-full p-1.5",
          "text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))]",
          "hover:bg-[hsl(var(--muted))] transition-colors",
          "disabled:opacity-50",
        )}
        title={label}
      >
        {isCreating ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : (
          <Share2 className="h-4 w-4" />
        )}
      </button>
    );
  }

  return (
    <button
      onClick={handleClick}
      disabled={isCreating}
      className={cn(
        "inline-flex items-center gap-2 rounded-lg border",
        "border-[hsl(var(--border))] px-4 py-2 text-sm font-medium",
        "text-[hsl(var(--foreground))] hover:bg-[hsl(var(--muted))]",
        "transition-colors disabled:opacity-50",
      )}
    >
      {isCreating ? (
        <Loader2 className="h-4 w-4 animate-spin" />
      ) : (
        <Share2 className="h-4 w-4" />
      )}
      {label}
    </button>
  );
}

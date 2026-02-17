import { Link } from "react-router-dom";
import { MessageSquare, BarChart3, Clock } from "lucide-react";

export function HomePage() {
  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold tracking-tight mb-2">
        Welcome to Toledot
      </h1>
      <p className="text-[hsl(var(--muted-foreground))] mb-8">
        Your AI-powered guide to church history in the Reformed tradition.
      </p>

      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <Link
          to="/chat"
          className="group rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-6 transition-shadow hover:shadow-md"
        >
          <MessageSquare className="mb-4 h-8 w-8 text-primary-700 dark:text-primary-300" />
          <h2 className="text-xl font-semibold mb-2 font-heading">
            Start a Conversation
          </h2>
          <p className="text-sm text-[hsl(var(--muted-foreground))]">
            Ask questions about church history and learn through dialogue with
            an AI tutor.
          </p>
        </Link>

        <Link
          to="/eras"
          className="group rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-6 transition-shadow hover:shadow-md"
        >
          <Clock className="mb-4 h-8 w-8 text-accent-700 dark:text-accent-400" />
          <h2 className="text-xl font-semibold mb-2 font-heading">
            Explore Eras
          </h2>
          <p className="text-sm text-[hsl(var(--muted-foreground))]">
            Journey through six major periods of church history from the Early
            Church to the present.
          </p>
        </Link>

        <Link
          to="/progress"
          className="group rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--card))] p-6 transition-shadow hover:shadow-md"
        >
          <BarChart3 className="mb-4 h-8 w-8 text-[hsl(var(--success))]" />
          <h2 className="text-xl font-semibold mb-2 font-heading">
            Track Progress
          </h2>
          <p className="text-sm text-[hsl(var(--muted-foreground))]">
            See how far you have come. Earn badges and maintain your learning
            streak.
          </p>
        </Link>
      </div>
    </div>
  );
}

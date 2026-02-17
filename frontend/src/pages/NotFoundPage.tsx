import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center p-4 text-center">
      <h1 className="text-4xl font-bold font-heading mb-2">404</h1>
      <p className="text-[hsl(var(--muted-foreground))] mb-6">
        This page could not be found.
      </p>
      <Link
        to="/"
        className="rounded-md bg-primary-700 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-primary-800 dark:bg-primary-300 dark:text-primary-950 dark:hover:bg-primary-200"
      >
        Go Home
      </Link>
    </div>
  );
}

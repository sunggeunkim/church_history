import { useState } from "react";
import { Menu, Search, LogOut } from "lucide-react";
import { ThemeToggle } from "@/components/shared/ThemeToggle";
import { useAuthStore } from "@/stores/authStore";

type TopNavProps = {
  onMenuToggle: () => void;
};

export function TopNav({ onMenuToggle }: TopNavProps) {
  const { user, performLogout } = useAuthStore();
  const [showUserMenu, setShowUserMenu] = useState(false);

  const handleLogout = async () => {
    setShowUserMenu(false);
    await performLogout();
  };

  return (
    <header className="sticky top-0 z-[var(--z-header)] flex h-14 items-center gap-4 border-b border-[hsl(var(--border))] bg-[hsl(var(--card))] px-4 lg:px-6">
      <button
        onClick={onMenuToggle}
        className="inline-flex h-10 w-10 items-center justify-center rounded-md hover:bg-secondary-100 dark:hover:bg-secondary-500/20 transition-colors lg:hidden"
        aria-label="Toggle navigation menu"
      >
        <Menu className="h-5 w-5" />
      </button>

      <div className="flex items-center gap-2">
        <span className="font-heading text-xl font-bold text-primary-700 dark:text-primary-300">
          Toledot
        </span>
      </div>

      <div className="flex-1" />

      <div className="hidden md:flex items-center gap-2 rounded-md border border-[hsl(var(--input))] bg-[hsl(var(--background))] px-3 py-1.5 text-sm">
        <Search className="h-4 w-4 text-[hsl(var(--muted-foreground))]" />
        <span className="text-[hsl(var(--muted-foreground))]">Search...</span>
        <kbd className="ml-4 rounded bg-[hsl(var(--muted))] px-1.5 py-0.5 text-xs font-mono text-[hsl(var(--muted-foreground))]">
          Ctrl+K
        </kbd>
      </div>

      <div className="flex items-center gap-2">
        <ThemeToggle />
        {user && (
          <div className="relative">
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="flex items-center gap-2 rounded-md hover:bg-[hsl(var(--muted))] transition-colors p-1"
              aria-label="User menu"
            >
              {user.avatarUrl ? (
                <img
                  src={user.avatarUrl}
                  alt={user.displayName}
                  className="h-8 w-8 rounded-full"
                />
              ) : (
                <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary-700 text-sm font-medium text-white dark:bg-primary-300 dark:text-primary-950">
                  {user.displayName.charAt(0).toUpperCase()}
                </div>
              )}
            </button>

            {showUserMenu && (
              <>
                <div
                  className="fixed inset-0 z-10"
                  onClick={() => setShowUserMenu(false)}
                />
                <div className="absolute right-0 mt-2 w-56 rounded-md border border-[hsl(var(--border))] bg-[hsl(var(--card))] shadow-lg z-20">
                  <div className="border-b border-[hsl(var(--border))] px-4 py-3">
                    <p className="text-sm font-medium">{user.displayName}</p>
                    <p className="text-xs text-[hsl(var(--muted-foreground))] truncate">
                      {user.email}
                    </p>
                  </div>
                  <div className="py-1">
                    <button
                      onClick={handleLogout}
                      className="flex w-full items-center gap-2 px-4 py-2 text-sm hover:bg-[hsl(var(--muted))] transition-colors"
                    >
                      <LogOut className="h-4 w-4" />
                      Sign out
                    </button>
                  </div>
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </header>
  );
}

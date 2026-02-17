import { NavLink } from "react-router-dom";
import {
  Home,
  Clock,
  MessageSquare,
  HelpCircle,
  BarChart3,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  { to: "/", icon: Home, label: "Home" },
  { to: "/eras", icon: Clock, label: "Eras" },
  { to: "/chat", icon: MessageSquare, label: "Chat" },
  { to: "/quiz", icon: HelpCircle, label: "Quiz" },
  { to: "/progress", icon: BarChart3, label: "Progress" },
];

export function BottomNav() {
  return (
    <nav className="fixed bottom-0 left-0 right-0 z-[var(--z-header)] flex h-16 items-center justify-around border-t border-[hsl(var(--border))] bg-[hsl(var(--card))] md:hidden">
      {navItems.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          end={item.to === "/"}
          className={({ isActive }) =>
            cn(
              "flex flex-col items-center gap-1 px-3 py-1 text-xs transition-colors",
              isActive
                ? "text-primary-700 dark:text-primary-300"
                : "text-[hsl(var(--muted-foreground))]",
            )
          }
        >
          <item.icon className="h-5 w-5" />
          <span>{item.label}</span>
        </NavLink>
      ))}
    </nav>
  );
}

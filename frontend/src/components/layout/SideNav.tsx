import { NavLink } from "react-router-dom";
import {
  Home,
  Clock,
  MessageSquare,
  HelpCircle,
  BarChart3,
  Settings,
} from "lucide-react";
import { cn } from "@/lib/utils";

type SideNavProps = {
  collapsed?: boolean;
};

const navItems = [
  { to: "/", icon: Home, label: "Home" },
  { to: "/eras", icon: Clock, label: "Eras" },
  { to: "/chat", icon: MessageSquare, label: "Chat" },
  { to: "/quiz", icon: HelpCircle, label: "Quiz" },
  { to: "/progress", icon: BarChart3, label: "Progress" },
];

export function SideNav({ collapsed = false }: SideNavProps) {
  return (
    <nav
      className={cn(
        "flex h-full flex-col border-r border-[hsl(var(--border))] bg-[hsl(var(--card))] transition-all duration-300",
        collapsed ? "w-16" : "w-60",
      )}
    >
      <div className="flex flex-1 flex-col gap-1 p-2 pt-4">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === "/"}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary-50 text-primary-700 dark:bg-primary-950 dark:text-primary-300"
                  : "text-[hsl(var(--muted-foreground))] hover:bg-[hsl(var(--muted))] hover:text-[hsl(var(--foreground))]",
                collapsed && "justify-center px-2",
              )
            }
          >
            <item.icon className="h-5 w-5 shrink-0" />
            {!collapsed && <span>{item.label}</span>}
          </NavLink>
        ))}
      </div>
      <div className="border-t border-[hsl(var(--border))] p-2">
        <NavLink
          to="/settings"
          className={({ isActive }) =>
            cn(
              "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
              isActive
                ? "bg-primary-50 text-primary-700 dark:bg-primary-950 dark:text-primary-300"
                : "text-[hsl(var(--muted-foreground))] hover:bg-[hsl(var(--muted))] hover:text-[hsl(var(--foreground))]",
              collapsed && "justify-center px-2",
            )
          }
        >
          <Settings className="h-5 w-5 shrink-0" />
          {!collapsed && <span>Settings</span>}
        </NavLink>
      </div>
    </nav>
  );
}

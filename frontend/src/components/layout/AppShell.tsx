import { useState } from "react";
import { Outlet } from "react-router-dom";
import { TopNav } from "./TopNav";
import { SideNav } from "./SideNav";
import { BottomNav } from "./BottomNav";
import { useMediaQuery } from "@/hooks/useMediaQuery";

export function AppShell() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const isDesktop = useMediaQuery("(min-width: 768px)");
  const isLargeDesktop = useMediaQuery("(min-width: 1024px)");

  return (
    <div className="flex h-screen flex-col">
      <TopNav onMenuToggle={() => setSidebarOpen(!sidebarOpen)} />
      <div className="flex flex-1 overflow-hidden">
        {/* Desktop sidebar */}
        {isDesktop && <SideNav collapsed={!isLargeDesktop} />}

        {/* Mobile sidebar overlay */}
        {!isDesktop && sidebarOpen && (
          <>
            <div
              className="fixed inset-0 z-[var(--z-overlay)] bg-black/50"
              onClick={() => setSidebarOpen(false)}
            />
            <div className="fixed left-0 top-14 bottom-0 z-[var(--z-modal)] animate-fade-in">
              <SideNav />
            </div>
          </>
        )}

        {/* Main content */}
        <main className="flex-1 overflow-y-auto pb-16 md:pb-0">
          <Outlet />
        </main>
      </div>

      {/* Mobile bottom nav */}
      {!isDesktop && <BottomNav />}
    </div>
  );
}

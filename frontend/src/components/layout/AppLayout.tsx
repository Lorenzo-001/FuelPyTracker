import { useState } from "react"
import { Outlet } from "react-router-dom"
import { Sidebar } from "./Sidebar"
import { Navbar } from "./Navbar"
import { BottomBar } from "./BottomBar"

export function AppLayout() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)

  return (
    <div className="h-screen w-screen overflow-hidden bg-background text-foreground flex flex-row">
      {/* Desktop Sidebar (Fissa a tutta altezza, visibile da md in su) */}
      <div className="hidden md:flex shrink-0 h-full">
        <Sidebar
          collapsed={sidebarCollapsed}
          onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
        />
      </div>

      {/* Content Area (Contenitore indipendente a tutta altezza) */}
      <div className="flex flex-1 flex-col h-full min-w-0 overflow-hidden">
        <Navbar />

        {/* Main Content: l'unico elemento con overflow-y-auto per lo scroll interno */}
        <main className="flex-1 overflow-y-auto p-4 md:p-6 lg:p-8 max-w-7xl w-full mx-auto pb-24 md:pb-8 animate-fade-in">
          <Outlet />
        </main>

        <footer className="hidden md:block shrink-0 border-t border-border/60 py-3 px-6 text-center text-xs text-muted-foreground bg-card/30">
          FuelPyTracker v2.0 • Il tuo registro digitale di bordo
        </footer>
      </div>

      {/* Mobile Bottom Navigation Bar with Central Elevated FAB (Only on small screens) */}
      <BottomBar />
    </div>
  )
}

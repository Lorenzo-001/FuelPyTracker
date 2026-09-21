import { useState } from "react"
import { Outlet } from "react-router-dom"
import { Sidebar } from "./Sidebar"
import { Navbar } from "./Navbar"
import { BottomBar } from "./BottomBar"

export function AppLayout() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-row overflow-x-hidden">
      {/* Desktop Sidebar (Only visible on md screens and above) */}
      <div className="hidden md:flex shrink-0">
        <Sidebar
          collapsed={sidebarCollapsed}
          onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
        />
      </div>

      {/* Content Area */}
      <div className="flex flex-1 flex-col min-w-0">
        <Navbar />

        {/* Main Content with bottom padding for mobile BottomBar */}
        <main className="flex-1 p-4 md:p-6 lg:p-8 max-w-7xl w-full mx-auto pb-24 md:pb-8 animate-fade-in">
          <Outlet />
        </main>

        <footer className="hidden md:block border-t border-border/60 py-4 px-6 text-center text-xs text-muted-foreground">
          FuelPyTracker v2.0 • Architettura Decoupled Monorepo (FastAPI + React 19)
        </footer>
      </div>

      {/* Mobile Bottom Navigation Bar with Central Elevated FAB (Only on small screens) */}
      <BottomBar />
    </div>
  )
}

import { useLocation, Link } from "react-router-dom"
import {
  Plus,
  Server,
  User,
  Sparkles,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { useSystemHealth } from "@/hooks/useSystemHealth"
import { useCurrentUser } from "@/hooks/useAuth"
import { isPublicDemoMode } from "@/lib/demo"

const pageTitles: Record<string, { title: string; category: string }> = {
  "/": { title: "Dashboard Generale", category: "Panoramica" },
  "/fuel": { title: "Registro Rifornimenti", category: "Gestione Spese" },
  "/maintenance": { title: "Registro Manutenzioni", category: "Salute Veicolo" },
  "/reminders": { title: "Scadenze & Promemoria", category: "Pianificazione" },
  "/reports": { title: "Report & Analytics", category: "Analisi Dati" },
  "/settings": { title: "Impostazioni Sistema", category: "Configurazione" },
  "/login": { title: "Accesso Utente", category: "Autenticazione" },
}

export function Navbar() {
  const location = useLocation()
  const { data: healthData, isError, isLoading } = useSystemHealth()
  const { data: user } = useCurrentUser()
  const isDemo = isPublicDemoMode()

  const currentMeta = pageTitles[location.pathname] || {
    title: "FuelPyTracker",
    category: "Applicazione",
  }

  return (
    <header className="sticky top-0 z-20 flex h-16 w-full items-center justify-between border-b border-border/70 bg-background/80 px-4 md:px-6 backdrop-blur-md">
      {/* Left: Brand Icon (mobile) & Title / Breadcrumb */}
      <div className="flex items-center gap-3">
        {/* Mobile Brand Icon */}
        <img
          src="/logo.png"
          alt="FuelPyTracker Logo"
          className="md:hidden h-8 w-8 shrink-0 object-contain drop-shadow-[0_2px_8px_rgba(250,204,21,0.3)]"
        />

        <div className="flex flex-col">
          <div className="hidden md:flex items-center gap-1.5 text-xs text-muted-foreground">
            <span>FuelPyTracker</span>
            <span>/</span>
            <span className="text-emerald-400 font-medium">
              {currentMeta.category}
            </span>
          </div>
          <h1 className="text-base md:text-lg font-bold tracking-tight text-foreground truncate max-w-[200px] sm:max-w-none">
            {currentMeta.title}
          </h1>
        </div>
      </div>

      {/* Right: Live Backend Status, Desktop Quick Action, Profile */}
      <div className="flex items-center gap-2 sm:gap-3">
        {/* Backend Status Indicator */}
        {isLoading ? (
          <Badge
            variant="outline"
            className="flex items-center gap-1.5 py-1 px-2 text-xs text-muted-foreground"
          >
            <span className="h-2 w-2 rounded-full bg-muted-foreground/50 animate-pulse" />
            <Server className="h-3 w-3" />
            <span className="hidden sm:inline">Verifica backend...</span>
          </Badge>
        ) : isError ? (
          <Badge
            variant="destructive"
            className="flex items-center gap-1.5 py-1 px-2 text-xs bg-red-500/10 border-red-500/30 text-red-400"
            title="FastAPI non risponde sulla porta 8000"
          >
            <span className="h-2 w-2 rounded-full bg-red-500" />
            <Server className="h-3 w-3" />
            <span className="hidden sm:inline">FastAPI Offline</span>
          </Badge>
        ) : (
          <Badge
            variant="success"
            className="flex items-center gap-1.5 py-1 px-2 sm:px-2.5 text-xs bg-emerald-500/10 border-emerald-500/30 text-emerald-400"
            title={`FastAPI ${healthData?.app || "API"} Online`}
          >
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
            </span>
            <Server className="h-3 w-3" />
            <span className="hidden sm:inline">FastAPI Online</span>
          </Badge>
        )}

        {/* Public Demo Indicator */}
        {isDemo && (
          <Badge
            variant="outline"
            className="hidden sm:inline-flex items-center gap-1.5 py-1 px-2.5 text-xs border-amber-500/30 bg-amber-500/10 text-amber-400"
            title="Applicazione in modalità vetrina dimostrativa (Read-Only)"
          >
            <Sparkles className="h-3 w-3" />
            <span>Vetrina Demo</span>
          </Badge>
        )}

        {/* Desktop Quick Action: New Refueling (Hidden on mobile where FAB is present) */}
        <Button
          asChild
          variant="emerald"
          size="sm"
          className="hidden md:inline-flex h-9 text-xs font-semibold gap-1.5 shadow-sm shadow-emerald-500/20"
        >
          <Link to="/fuel?action=new">
            <Plus className="h-3.5 w-3.5" />
            <span>Nuovo Rifornimento</span>
          </Link>
        </Button>

        {/* User Pill / Profile */}
        <Link
          to={user || isDemo ? "/settings" : "/login"}
          title={user?.email ? `Profilo utente: ${user.email}` : "Accedi alla tua area"}
          className="flex items-center gap-2 rounded-lg border border-border/70 bg-card/60 px-2 sm:px-2.5 py-1.5 text-xs text-muted-foreground hover:border-border hover:text-foreground transition-all"
        >
          <div className="h-6 w-6 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold text-[10px]">
            {user?.email ? user.email.slice(0, 2).toUpperCase() : <User className="h-3.5 w-3.5" />}
          </div>
          <span className="hidden md:inline font-medium text-foreground truncate max-w-[120px]">
            {user?.email ? user.email.split("@")[0] : isDemo ? "Ospite Demo" : "Accedi"}
          </span>
        </Link>
      </div>
    </header>
  )
}

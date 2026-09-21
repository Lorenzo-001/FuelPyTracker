import { useLocation, Link } from "react-router-dom"
import {
  Menu,
  Plus,
  Server,
  User,
  ExternalLink,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { useSystemHealth } from "@/hooks/useSystemHealth"

interface NavbarProps {
  onMobileMenuToggle: () => void
}

const pageTitles: Record<string, { title: string; category: string }> = {
  "/": { title: "Dashboard Generale", category: "Panoramica" },
  "/fuel": { title: "Registro Rifornimenti", category: "Gestione Spese" },
  "/maintenance": { title: "Registro Manutenzioni", category: "Salute Veicolo" },
  "/reminders": { title: "Scadenze & Promemoria", category: "Pianificazione" },
  "/reports": { title: "Report & Analytics", category: "Analisi Dati" },
  "/settings": { title: "Impostazioni Sistema", category: "Configurazione" },
  "/login": { title: "Accesso Utente", category: "Autenticazione" },
}

export function Navbar({ onMobileMenuToggle }: NavbarProps) {
  const location = useLocation()
  const { data: healthData, isError, isLoading } = useSystemHealth()

  const currentMeta = pageTitles[location.pathname] || {
    title: "FuelPyTracker",
    category: "Applicazione",
  }

  return (
    <header className="sticky top-0 z-20 flex h-16 w-full items-center justify-between border-b border-border/70 bg-background/80 px-4 md:px-6 backdrop-blur-md">
      {/* Left: Mobile Toggle & Page Title/Breadcrumb */}
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={onMobileMenuToggle}
          className="md:hidden flex h-9 w-9 items-center justify-center rounded-lg border border-border/70 bg-card text-muted-foreground hover:text-foreground"
          aria-label="Apri menu di navigazione"
        >
          <Menu className="h-5 w-5" />
        </button>

        <div className="flex flex-col">
          <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <span>FuelPyTracker</span>
            <span>/</span>
            <span className="text-emerald-400 font-medium">
              {currentMeta.category}
            </span>
          </div>
          <h1 className="text-base md:text-lg font-bold tracking-tight text-foreground">
            {currentMeta.title}
          </h1>
        </div>
      </div>

      {/* Right: Backend Live Status, Actions, Profile */}
      <div className="flex items-center gap-2.5 md:gap-3.5">
        {/* Real-time Backend Status Indicator */}
        {isLoading ? (
          <Badge
            variant="outline"
            className="hidden sm:inline-flex items-center gap-1.5 py-1 px-2.5 text-xs text-muted-foreground"
          >
            <span className="h-2 w-2 rounded-full bg-muted-foreground/50 animate-pulse" />
            <Server className="h-3 w-3" />
            <span>Verifica backend...</span>
          </Badge>
        ) : isError ? (
          <Badge
            variant="destructive"
            className="hidden sm:inline-flex items-center gap-1.5 py-1 px-2.5 text-xs bg-red-500/10 border-red-500/30 text-red-400"
            title="FastAPI non risponde sulla porta 8000"
          >
            <span className="h-2 w-2 rounded-full bg-red-500" />
            <Server className="h-3 w-3" />
            <span>FastAPI Offline</span>
          </Badge>
        ) : (
          <Badge
            variant="success"
            className="hidden sm:inline-flex items-center gap-1.5 py-1 px-2.5 text-xs bg-emerald-500/10 border-emerald-500/30 text-emerald-400"
            title={`FastAPI ${healthData?.app || "API"} Online`}
          >
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
            </span>
            <Server className="h-3 w-3" />
            <span>FastAPI Online</span>
          </Badge>
        )}

        {/* Quick Action: New Refueling */}
        <Button
          asChild
          variant="emerald"
          size="sm"
          className="h-8 md:h-9 text-xs font-semibold gap-1.5"
        >
          <Link to="/fuel">
            <Plus className="h-3.5 w-3.5" />
            <span className="hidden sm:inline">Nuovo Rifornimento</span>
            <span className="sm:hidden">Nuovo</span>
          </Link>
        </Button>

        {/* User Pill / Login */}
        <Link
          to="/login"
          className="flex items-center gap-2 rounded-lg border border-border/70 bg-card/60 px-2.5 py-1.5 text-xs text-muted-foreground hover:border-border hover:text-foreground transition-all"
        >
          <div className="h-6 w-6 rounded-full bg-muted/60 flex items-center justify-center text-foreground font-medium">
            <User className="h-3.5 w-3.5" />
          </div>
          <span className="hidden md:inline font-medium">Lorenzo</span>
          <ExternalLink className="h-3 w-3 opacity-60 hidden md:inline" />
        </Link>
      </div>
    </header>
  )
}

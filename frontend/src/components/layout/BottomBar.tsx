import { useState } from "react"
import { NavLink, useNavigate, useLocation } from "react-router-dom"
import {
  Gauge,
  Fuel,
  Plus,
  Wrench,
  Grid,
  CalendarClock,
  BarChart3,
  Settings,
  User,
  Car,
  ChevronRight,
} from "lucide-react"
import { cn } from "@/lib/utils"
import { Badge } from "@/components/ui/badge"
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from "@/components/ui/sheet"

export function BottomBar() {
  const [moreOpen, setMoreOpen] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()

  const isMoreActive = ["/reminders", "/reports", "/settings", "/login"].includes(
    location.pathname
  )

  const handleQuickAdd = () => {
    // Navigate to fuel section with intent to add new refueling
    navigate("/fuel")
  }

  return (
    <>
      <nav
        aria-label="Navigazione Mobile"
        className="fixed bottom-0 inset-x-0 z-40 h-16 border-t border-border/80 bg-card/90 backdrop-blur-lg px-2 flex items-center justify-around md:hidden pb-safe select-none shadow-[0_-4px_20px_rgba(0,0,0,0.3)]"
      >
        {/* Tab 1: Dashboard */}
        <NavLink
          to="/"
          end
          className={({ isActive }) =>
            cn(
              "flex flex-col items-center justify-center flex-1 py-1 text-[10px] font-medium transition-colors",
              isActive
                ? "text-emerald-400 font-semibold"
                : "text-muted-foreground hover:text-foreground"
            )
          }
        >
          {({ isActive }) => (
            <>
              <Gauge className={cn("h-5 w-5 mb-0.5", isActive && "text-emerald-400")} />
              <span>Dashboard</span>
            </>
          )}
        </NavLink>

        {/* Tab 2: Rifornimenti */}
        <NavLink
          to="/fuel"
          className={({ isActive }) =>
            cn(
              "flex flex-col items-center justify-center flex-1 py-1 text-[10px] font-medium transition-colors",
              isActive
                ? "text-emerald-400 font-semibold"
                : "text-muted-foreground hover:text-foreground"
            )
          }
        >
          {({ isActive }) => (
            <>
              <Fuel className={cn("h-5 w-5 mb-0.5", isActive && "text-emerald-400")} />
              <span>Pieni</span>
            </>
          )}
        </NavLink>

        {/* Center: Floating Action Button (FAB) */}
        <div className="flex-1 flex justify-center -mt-5">
          <button
            type="button"
            onClick={handleQuickAdd}
            aria-label="Registra nuovo rifornimento"
            className="group relative flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-emerald-400 to-emerald-600 text-slate-950 shadow-lg shadow-emerald-500/40 ring-4 ring-background active:scale-95 transition-all duration-150"
          >
            <Plus className="h-6 w-6 stroke-[2.5] transition-transform duration-200 group-hover:rotate-90" />
            <span className="sr-only">Nuovo Rifornimento</span>
          </button>
        </div>

        {/* Tab 3: Manutenzioni */}
        <NavLink
          to="/maintenance"
          className={({ isActive }) =>
            cn(
              "flex flex-col items-center justify-center flex-1 py-1 text-[10px] font-medium transition-colors",
              isActive
                ? "text-emerald-400 font-semibold"
                : "text-muted-foreground hover:text-foreground"
            )
          }
        >
          {({ isActive }) => (
            <>
              <Wrench className={cn("h-5 w-5 mb-0.5", isActive && "text-emerald-400")} />
              <span>Officina</span>
            </>
          )}
        </NavLink>

        {/* Tab 4: Altro (Apre Bottom Sheet) */}
        <button
          type="button"
          onClick={() => setMoreOpen(true)}
          className={cn(
            "flex flex-col items-center justify-center flex-1 py-1 text-[10px] font-medium transition-colors relative",
            isMoreActive
              ? "text-emerald-400 font-semibold"
              : "text-muted-foreground hover:text-foreground"
          )}
        >
          <div className="relative">
            <Grid className={cn("h-5 w-5 mb-0.5", isMoreActive && "text-emerald-400")} />
            {/* Notification dot for active reminders */}
            <span className="absolute -top-0.5 -right-0.5 h-2 w-2 rounded-full bg-amber-400 ring-2 ring-background" />
          </div>
          <span>Altro</span>
        </button>
      </nav>

      {/* Bottom Sheet "Altro" per smartphone */}
      <Sheet open={moreOpen} onOpenChange={setMoreOpen}>
        <SheetContent side="bottom" className="p-5 max-h-[85vh] overflow-y-auto">
          {/* Grab handle indicator */}
          <div className="w-12 h-1.5 bg-muted-foreground/30 rounded-full mx-auto -mt-2 mb-4" />

          <SheetHeader className="text-left pb-2">
            <SheetTitle className="text-base font-bold">Funzionalità Aggiuntive</SheetTitle>
            <SheetDescription className="text-xs">
              Sezioni secondarie, gestione scadenze e preferenze dell'applicazione.
            </SheetDescription>
          </SheetHeader>

          {/* Active Vehicle Snippet */}
          <div className="p-3 rounded-xl border border-border/70 bg-muted/20 flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="h-9 w-9 rounded-lg bg-emerald-500/15 text-emerald-400 flex items-center justify-center">
                <Car className="h-5 w-5" />
              </div>
              <div>
                <div className="text-xs font-semibold text-foreground">BMW Serie 1 (118d)</div>
                <div className="text-[11px] text-muted-foreground">AB 123 CD • Diesel</div>
              </div>
            </div>
            <Badge variant="success" className="text-[10px] py-0.5">Attivo</Badge>
          </div>

          {/* Navigation Links Grid */}
          <div className="space-y-2">
            <button
              type="button"
              onClick={() => {
                setMoreOpen(false)
                navigate("/reminders")
              }}
              className="w-full flex items-center justify-between p-3 rounded-xl border border-border/60 bg-card/60 hover:bg-muted/40 transition-colors text-left"
            >
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-rose-500/10 text-rose-400">
                  <CalendarClock className="h-4 w-4" />
                </div>
                <div>
                  <div className="text-xs font-semibold text-foreground">Scadenze & Promemoria</div>
                  <div className="text-[10px] text-muted-foreground">Controllo olio, bollo, revisione</div>
                </div>
              </div>
              <div className="flex items-center gap-1.5">
                <Badge variant="warning" className="text-[10px] px-1.5 py-0 h-4">2 Scadenze</Badge>
                <ChevronRight className="h-4 w-4 text-muted-foreground" />
              </div>
            </button>

            <button
              type="button"
              onClick={() => {
                setMoreOpen(false)
                navigate("/reports")
              }}
              className="w-full flex items-center justify-between p-3 rounded-xl border border-border/60 bg-card/60 hover:bg-muted/40 transition-colors text-left"
            >
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-sky-500/10 text-sky-400">
                  <BarChart3 className="h-4 w-4" />
                </div>
                <div>
                  <div className="text-xs font-semibold text-foreground">Report & Esportazioni</div>
                  <div className="text-[10px] text-muted-foreground">Download Excel, CSV e Libretto PDF</div>
                </div>
              </div>
              <ChevronRight className="h-4 w-4 text-muted-foreground" />
            </button>

            <button
              type="button"
              onClick={() => {
                setMoreOpen(false)
                navigate("/settings")
              }}
              className="w-full flex items-center justify-between p-3 rounded-xl border border-border/60 bg-card/60 hover:bg-muted/40 transition-colors text-left"
            >
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-muted text-foreground">
                  <Settings className="h-4 w-4" />
                </div>
                <div>
                  <div className="text-xs font-semibold text-foreground">Impostazioni Sistema</div>
                  <div className="text-[10px] text-muted-foreground">Soglie carburante, categorie e parametri</div>
                </div>
              </div>
              <ChevronRight className="h-4 w-4 text-muted-foreground" />
            </button>

            <button
              type="button"
              onClick={() => {
                setMoreOpen(false)
                navigate("/login")
              }}
              className="w-full flex items-center justify-between p-3 rounded-xl border border-border/60 bg-card/60 hover:bg-muted/40 transition-colors text-left"
            >
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-muted text-foreground">
                  <User className="h-4 w-4" />
                </div>
                <div>
                  <div className="text-xs font-semibold text-foreground">Profilo Utente & Accesso</div>
                  <div className="text-[10px] text-muted-foreground">Autenticazione JWT / Modalità Demo</div>
                </div>
              </div>
              <ChevronRight className="h-4 w-4 text-muted-foreground" />
            </button>
          </div>
        </SheetContent>
      </Sheet>
    </>
  )
}

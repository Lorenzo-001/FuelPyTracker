import { useEffect } from "react"
import { Navigate, Outlet, useLocation } from "react-router-dom"
import { authStorage } from "@/services/api/client"
import { isPublicDemoMode, setRuntimeDemoMode } from "@/lib/demo"
import { useSystemHealth } from "@/hooks/useSystemHealth"
import { Loader2 } from "lucide-react"

/**
 * Route Guard che protegge le sezioni private dell'applicazione.
 * - In modalità Privata: richiede obbligatoriamente un token JWT valido in localStorage.
 * - In modalità Demo Vetrina (rilevata dal backend o configurata in build): consente l'accesso diretto.
 */
export function ProtectedRoute() {
  const location = useLocation()
  const token = authStorage.getToken()
  const { data: health, isLoading } = useSystemHealth()

  useEffect(() => {
    if (health?.demo_mode !== undefined) {
      setRuntimeDemoMode(health.demo_mode)
    }
  }, [health?.demo_mode])

  const isDemo = isPublicDemoMode() || Boolean(health?.demo_mode)

  // Se non c'è token e il backend sta ancora rispondendo al primo health-check, attendiamo
  if (!token && !isPublicDemoMode() && isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="h-7 w-7 text-emerald-400 animate-spin" />
          <span className="text-xs text-muted-foreground font-medium">Inizializzazione applicazione...</span>
        </div>
      </div>
    )
  }

  if (token || isDemo) {
    return <Outlet />
  }

  // Reindirizza al login privato ricordando la rotta di destinazione
  return <Navigate to="/login" replace state={{ from: location }} />
}

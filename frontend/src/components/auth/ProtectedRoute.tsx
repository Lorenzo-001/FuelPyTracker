import { Navigate, Outlet, useLocation } from "react-router-dom"
import { authStorage } from "@/services/api/client"
import { isPublicDemoMode } from "@/lib/demo"

/**
 * Route Guard che protegge le sezioni private dell'applicazione.
 * - In modalità Privata: richiede obbligatoriamente un token JWT valido in localStorage.
 * - In modalità Demo Vetrina (?demo=true o VITE_PUBLIC_DEMO=true): consente l'accesso diretto read-only.
 */
export function ProtectedRoute() {
  const location = useLocation()
  const token = authStorage.getToken()
  const isDemo = isPublicDemoMode()

  if (token || isDemo) {
    return <Outlet />
  }

  // Reindirizza al login privato ricordando la rotta di destinazione
  return <Navigate to="/login" replace state={{ from: location }} />
}

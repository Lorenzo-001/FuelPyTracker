/**
 * Helper per la gestione della Modalità Demo Vetrina Pubblica (Read-Only).
 * Consente di visualizzare l'applicazione senza autenticazione ma con azioni di scrittura bloccate.
 */
import { toast } from "sonner"

/**
 * Rileva se l'applicazione è in esecuzione in modalità Demo Vetrina.
 * Attivo se:
 * 1. È presente il parametro URL '?demo=true'
 * 2. È impostata la variabile d'ambiente VITE_PUBLIC_DEMO === 'true'
 */
export function isPublicDemoMode(): boolean {
  if (typeof window !== "undefined") {
    try {
      const searchParams = new URLSearchParams(window.location.search)
      if (searchParams.get("demo") === "true") {
        return true
      }
    } catch {
      // Ignora errori di parsing URL
    }
  }
  return import.meta.env.VITE_PUBLIC_DEMO === "true"
}

/**
 * Restituisce true se le scritture e cancellazioni devono essere bloccate (come writes_disabled in V1).
 */
export function isWritesDisabled(): boolean {
  return isPublicDemoMode()
}

/**
 * Mostra un toast informativo quando un visitatore tenta una scrittura nella demo pubblica.
 */
export function showDemoReadOnlyNotice(actionName = "Questa operazione"): boolean {
  if (isWritesDisabled()) {
    toast.info("Modalità Vetrina Read-Only", {
      description: `${actionName} è disabilitata nella demo pubblica per preservare i dati di esempio.`,
    })
    return true
  }
  return false
}

/**
 * Helper per la gestione della Modalità Demo Vetrina Pubblica (Read-Only).
 * Consente di visualizzare l'applicazione senza autenticazione ma con azioni di scrittura bloccate.
 * Lo stato è determinato esclusivamente dalla configurazione del backend (health.demo_mode)
 * o dalla variabile d'ambiente di deploy (VITE_PUBLIC_DEMO).
 */
import { toast } from "sonner"

let _runtimeDemoMode: boolean | null = null

/**
 * Imposta lo stato demo rilevato a runtime dal backend.
 */
export function setRuntimeDemoMode(isDemo: boolean): void {
  _runtimeDemoMode = isDemo
}

/**
 * Rileva se l'applicazione è in esecuzione in modalità Demo Vetrina.
 * Priorità:
 * 1. Risposta live del backend (/health -> demo_mode)
 * 2. Variabile d'ambiente VITE_PUBLIC_DEMO === 'true'
 */
export function isPublicDemoMode(): boolean {
  if (_runtimeDemoMode !== null) {
    return _runtimeDemoMode
  }
  return import.meta.env.VITE_PUBLIC_DEMO === "true"
}

/**
 * Restituisce true se le scritture e cancellazioni devono essere bloccate.
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

import { useEffect, useState, useRef, useCallback } from "react"
import { useNavigate, useLocation } from "react-router-dom"
import { useQueryClient } from "@tanstack/react-query"
import { Loader2 } from "lucide-react"

/** Soglia di inattività per il riavvio della sessione (30 minuti in millisecondi) */
const INACTIVITY_THRESHOLD_MS = 30 * 60 * 1000
const STORAGE_KEY = "fpt_last_active_ts"
const THROTTLE_ACTIVITY_INTERVAL_MS = 60 * 1000

export function SessionResumeManager() {
  const [isResuming, setIsResuming] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()
  const queryClient = useQueryClient()

  const lastRecordedRef = useRef<number>(0)
  const isCheckingRef = useRef<boolean>(false)

  // Aggiorna l'orario di ultima attività con throttling (max 1 volta al minuto)
  const recordActivity = useCallback((force = false) => {
    const now = Date.now()
    if (force || now - lastRecordedRef.current > THROTTLE_ACTIVITY_INTERVAL_MS) {
      lastRecordedRef.current = now
      try {
        localStorage.setItem(STORAGE_KEY, String(now))
      } catch {
        // Ignora eventuali blocchi localStorage (es. modalità incognito restrittiva)
      }
    }
  }, [])

  // Controlla se è trascorso più tempo della soglia di inattività
  const checkInactivityAndResume = useCallback(() => {
    if (isCheckingRef.current) return
    isCheckingRef.current = true

    try {
      const stored = localStorage.getItem(STORAGE_KEY)
      const now = Date.now()

      if (stored) {
        const lastActive = parseInt(stored, 10)
        if (!isNaN(lastActive)) {
          const elapsed = now - lastActive
          if (elapsed >= INACTIVITY_THRESHOLD_MS) {
            // Inattività prolungata rilevata: attiva intro di benvenuto e riavvio
            setIsResuming(true)

            // Reindirizza alla dashboard se ci si trovava in sezioni secondarie
            if (location.pathname !== "/") {
              navigate("/", { replace: true })
            }

            // Sincronizza ed invalida le cache TanStack Query per scaricare dati freschi
            queryClient.invalidateQueries()

            // Aggiorna subito il timestamp
            recordActivity(true)

            // Chiudi la schermata di benvenuto dopo 1.5 secondi
            setTimeout(() => {
              setIsResuming(false)
              isCheckingRef.current = false
            }, 1500)
            return
          }
        }
      }

      // Prima esecuzione o inattività inferiore alla soglia: aggiorna timestamp
      recordActivity(true)
    } finally {
      if (!isResuming) {
        setTimeout(() => {
          isCheckingRef.current = false
        }, 500)
      }
    }
  }, [location.pathname, navigate, queryClient, recordActivity, isResuming])

  // Verifica all'avvio del componente
  useEffect(() => {
    checkInactivityAndResume()
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  // Ascolta eventi del ciclo di vita del browser (BFCache, cambio tab, app resume su smartphone)
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === "hidden") {
        recordActivity(true)
      } else if (document.visibilityState === "visible") {
        checkInactivityAndResume()
      }
    }

    const handlePageShow = () => {
      checkInactivityAndResume()
    }

    const handleUserInteraction = () => {
      recordActivity(false)
    }

    document.addEventListener("visibilitychange", handleVisibilityChange)
    window.addEventListener("pageshow", handlePageShow)
    window.addEventListener("pointerdown", handleUserInteraction, { passive: true })
    window.addEventListener("keydown", handleUserInteraction, { passive: true })
    window.addEventListener("touchstart", handleUserInteraction, { passive: true })

    return () => {
      document.removeEventListener("visibilitychange", handleVisibilityChange)
      window.removeEventListener("pageshow", handlePageShow)
      window.removeEventListener("pointerdown", handleUserInteraction)
      window.removeEventListener("keydown", handleUserInteraction)
      window.removeEventListener("touchstart", handleUserInteraction)
    }
  }, [checkInactivityAndResume, recordActivity])

  // Registra attività ad ogni navigazione tra rotte
  useEffect(() => {
    recordActivity(false)
  }, [location.pathname, recordActivity])

  if (!isResuming) return null

  return (
    <div
      role="status"
      aria-live="polite"
      className="fixed inset-0 z-[100] flex flex-col items-center justify-center bg-background/95 backdrop-blur-xl animate-in fade-in duration-300 select-none px-4"
    >
      <div className="flex flex-col items-center text-center max-w-sm mx-auto">
        {/* Logo con aureola ed effetto respiro */}
        <div className="relative mb-6 flex items-center justify-center">
          <div className="absolute -inset-4 bg-emerald-500/25 rounded-full blur-2xl animate-pulse" />
          <img
            src="/logo.png"
            alt="FuelPyTracker Logo"
            className="relative h-20 w-20 object-contain drop-shadow-[0_4px_24px_rgba(16,185,129,0.45)] animate-in zoom-in-75 duration-500"
          />
        </div>

        {/* Testo di benvenuto */}
        <h2 className="text-2xl font-black tracking-tight text-foreground sm:text-3xl">
          Bentornato!
        </h2>
        <p className="text-xs text-muted-foreground mt-2 max-w-[270px] leading-relaxed">
          Riavvio sessione e sincronizzazione dei dati di bordo in corso...
        </p>

        {/* Pill di caricamento */}
        <div className="mt-6 flex items-center gap-2 px-4 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold shadow-sm">
          <Loader2 className="h-3.5 w-3.5 animate-spin" />
          <span>Caricamento Dashboard</span>
        </div>
      </div>
    </div>
  )
}

import {
  AlertCircle,
  AlertTriangle,
  CheckCircle2,
  Calendar,
  Gauge,
  Sparkles,
} from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { useMaintenanceDeadlines } from "@/hooks/useMaintenance"

export function DeadlineBanner() {
  const { data: deadlines, isLoading } = useMaintenanceDeadlines()

  if (isLoading || !deadlines || deadlines.length === 0) {
    return null
  }

  const urgentCount = deadlines.filter((d) => d.priority <= 2).length
  const hasExpired = deadlines.some((d) => d.priority === 1)

  return (
    <div
      className={`rounded-2xl border p-4 sm:p-5 transition-all shadow-sm ${
        hasExpired
          ? "border-rose-500/30 bg-rose-500/10"
          : urgentCount > 0
            ? "border-amber-500/30 bg-amber-500/10"
            : "border-emerald-500/20 bg-emerald-500/5"
      }`}
    >
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-3 border-b border-border/40">
        <div className="flex items-center gap-2.5">
          {hasExpired ? (
            <div className="p-2 rounded-xl bg-rose-500/20 text-rose-400 shrink-0">
              <AlertCircle className="h-5 w-5" />
            </div>
          ) : urgentCount > 0 ? (
            <div className="p-2 rounded-xl bg-amber-500/20 text-amber-400 shrink-0">
              <AlertTriangle className="h-5 w-5" />
            </div>
          ) : (
            <div className="p-2 rounded-xl bg-emerald-500/20 text-emerald-400 shrink-0">
              <CheckCircle2 className="h-5 w-5" />
            </div>
          )}

          <div>
            <h3 className="text-sm font-bold text-foreground flex items-center gap-2">
              <span>Semaforo Scadenze Manutentive</span>
              {urgentCount > 0 ? (
                <Badge
                  variant="outline"
                  className={
                    hasExpired
                      ? "border-rose-500/40 text-rose-400 bg-rose-500/10 text-[10px]"
                      : "border-amber-500/40 text-amber-400 bg-amber-500/10 text-[10px]"
                  }
                >
                  {urgentCount} in attenzione
                </Badge>
              ) : (
                <Badge
                  variant="outline"
                  className="border-emerald-500/40 text-emerald-400 bg-emerald-500/10 text-[10px]"
                >
                  Tutto in regola
                </Badge>
              )}
            </h3>
            <p className="text-xs text-muted-foreground mt-0.5">
              Monitoraggio predittivo basato su date limite, soglie chilometriche e ritmo d&apos;uso reale.
            </p>
          </div>
        </div>
      </div>

      {/* Deadlines Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 pt-3.5">
        {deadlines.map((item) => {
          const isExpired = item.priority === 1
          const isUrgent = item.priority === 2

          return (
            <div
              key={item.id}
              className="p-3.5 rounded-xl bg-background/60 border border-border/50 flex flex-col justify-between space-y-2 hover:border-border transition-all"
            >
              <div className="flex items-center justify-between">
                <span className="font-bold text-xs text-foreground">
                  {item.expense_type}
                </span>
                <Badge
                  variant="outline"
                  className={`text-[10px] font-semibold ${
                    isExpired
                      ? "border-rose-500/40 text-rose-400 bg-rose-500/10"
                      : isUrgent
                        ? "border-amber-500/40 text-amber-400 bg-amber-500/10"
                        : "border-emerald-500/40 text-emerald-400 bg-emerald-500/10"
                  }`}
                >
                  {isExpired ? "Scaduto" : isUrgent ? "Imminente" : "In Regola"}
                </Badge>
              </div>

              {/* Status details */}
              <div className="space-y-1 text-xs">
                {item.km_left !== null && (
                  <div className="flex items-center gap-1.5 font-mono text-muted-foreground">
                    <Gauge className="h-3.5 w-3.5 text-muted-foreground/70" />
                    <span>
                      {item.km_left < 0
                        ? `Superato da ${Math.abs(item.km_left).toLocaleString("it-IT")} km`
                        : `Mancano ${item.km_left.toLocaleString("it-IT")} km`}
                    </span>
                  </div>
                )}

                {item.days_left !== null && (
                  <div className="flex items-center gap-1.5 font-mono text-muted-foreground">
                    <Calendar className="h-3.5 w-3.5 text-muted-foreground/70" />
                    <span>
                      {item.days_left < 0
                        ? `Scaduto da ${Math.abs(item.days_left)} giorni`
                        : `Scadenza tra ${item.days_left} giorni`}
                    </span>
                  </div>
                )}

                {item.predicted_date && (
                  <div className="flex items-center gap-1.5 text-[11px] text-emerald-400/90 pt-1">
                    <Sparkles className="h-3 w-3" />
                    <span>Stima raggiungimento: {item.predicted_date}</span>
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

import { CalendarClock, Plus, AlertCircle, CheckCircle2 } from "lucide-react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"

export default function RemindersPage() {
  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-extrabold tracking-tight flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-rose-500/10 text-rose-400">
              <CalendarClock className="h-5 w-5" />
            </div>
            Scadenze & Promemoria
          </h2>
          <p className="text-sm text-muted-foreground mt-1">
            Notifiche temporali e chilometriche per bollo, assicurazione, revisione e tagliando.
          </p>
        </div>

        <Button variant="emerald" size="sm" className="gap-1.5">
          <Plus className="h-4 w-4" />
          <span>Nuovo Promemoria</span>
        </Button>
      </div>

      {/* Urgent Alert Banner */}
      <div className="rounded-xl border border-amber-500/40 bg-amber-500/10 p-4 flex items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <AlertCircle className="h-5 w-5 text-amber-400 shrink-0" />
          <div className="text-sm">
            <span className="font-semibold text-amber-300">2 Promemoria richiedono attenzione: </span>
            <span className="text-amber-200/90">
              Assicurazione RCA in scadenza entro 14 giorni e Tagliando previsto a breve.
            </span>
          </div>
        </div>
        <Badge variant="warning" className="shrink-0">
          Priorità Alta
        </Badge>
      </div>

      {/* Reminders List Skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {[1, 2, 3, 4].map((item) => (
          <Card key={item} className="p-5 space-y-4">
            <div className="flex items-start justify-between">
              <div className="space-y-2 flex-1">
                <Skeleton className="h-5 w-40" />
                <Skeleton className="h-4 w-56" />
              </div>
              <Skeleton className="h-6 w-20 rounded-full" />
            </div>

            <div className="pt-2 border-t border-border/60 flex items-center justify-between text-xs text-muted-foreground">
              <Skeleton className="h-4 w-28" />
              <div className="flex gap-2">
                <Button variant="ghost" size="sm" className="h-7 text-xs">
                  <CheckCircle2 className="h-3.5 w-3.5 mr-1 text-emerald-400" />
                  Risolvi
                </Button>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  )
}

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { History, Gauge, CheckCircle2 } from "lucide-react"
import { useReminderHistory } from "@/hooks/useReminders"

interface ReminderHistoryModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function ReminderHistoryModal({
  open,
  onOpenChange,
}: ReminderHistoryModalProps) {
  const { data: history, isLoading } = useReminderHistory(30)

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg max-h-[85vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-lg font-bold">
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
              <History className="h-5 w-5" />
            </div>
            Storico Esecuzioni Promemoria
          </DialogTitle>
          <DialogDescription>
            Log immutabile dei controlli di routine contrassegnati come completati (&quot;Mark as Done&quot;).
          </DialogDescription>
        </DialogHeader>

        <div className="py-2 space-y-2.5">
          {isLoading ? (
            <p className="text-xs text-muted-foreground text-center py-6">
              Caricamento storico in corso...
            </p>
          ) : !history || history.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground space-y-2">
              <CheckCircle2 className="h-8 w-8 mx-auto opacity-40 text-emerald-400" />
              <p className="text-xs">Nessun controllo ancora completato.</p>
              <p className="text-[11px] text-muted-foreground/70">
                Clicca su &quot;Segna come Eseguito&quot; su una card per archiviare la prima verifica.
              </p>
            </div>
          ) : (
            <div className="divide-y divide-border/40">
              {history.map((item) => {
                const dateVal = item.date_checked || (item as unknown as { check_date?: string }).check_date || "—"
                const kmVal = item.km_checked ?? (item as unknown as { check_km?: number }).check_km ?? 0

                return (
                  <div key={item.id} className="py-3 flex items-start justify-between gap-3">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-foreground">
                          Promemoria #{item.reminder_id}
                        </span>
                        <span className="text-[11px] font-mono text-muted-foreground">
                          {dateVal}
                        </span>
                      </div>

                      <div className="flex items-center gap-2 text-[11px] text-muted-foreground font-mono">
                        <span className="flex items-center gap-1">
                          <Gauge className="h-3 w-3 text-muted-foreground/60" />
                          {typeof kmVal === "number" ? kmVal.toLocaleString("it-IT") : kmVal} km
                        </span>
                      </div>

                      {item.notes && (
                        <p className="text-xs text-foreground/80 pt-0.5">
                          {item.notes}
                        </p>
                      )}
                    </div>

                    <span className="text-[10px] text-muted-foreground/60 font-mono shrink-0">
                      {dateVal}
                    </span>
                  </div>
                )
              })}
            </div>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" size="sm" onClick={() => onOpenChange(false)}>
            Chiudi
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

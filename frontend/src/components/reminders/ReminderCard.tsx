import { useState } from "react"
import {
  CheckCircle2,
  AlertCircle,
  Clock,
  Gauge,
  Edit3,
  Trash2,
  Loader2,
} from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog"
import { useCompleteReminder, useDeleteReminder } from "@/hooks/useReminders"
import type { ReminderResponse } from "@/types"
import { toast } from "sonner"

interface ReminderCardProps {
  reminder: ReminderResponse
  onEdit: (reminder: ReminderResponse) => void
}

export function ReminderCard({ reminder, onEdit }: ReminderCardProps) {
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const completeMutation = useCompleteReminder()
  const deleteMutation = useDeleteReminder()

  const pct = Math.min(100, Math.max(0, Math.round(reminder.progress * 100)))
  const isUrgent = reminder.progress >= 0.7 && !reminder.is_overdue

  const handleMarkAsDone = async () => {
    try {
      await completeMutation.mutateAsync({
        id: reminder.id,
        data: {
          check_date: new Date().toISOString().split("T")[0],
          notes: "Eseguito manualmente dall'interfaccia",
        },
      })
      toast.success(`"${reminder.title}" segnato come eseguito! Ciclo azzerato.`)
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Errore durante il salvataggio"
      toast.error(msg)
    }
  }

  const handleDelete = async () => {
    try {
      await deleteMutation.mutateAsync(reminder.id)
      toast.success("Promemoria eliminato")
      setDeleteDialogOpen(false)
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Errore durante l'eliminazione"
      toast.error(msg)
    }
  }

  return (
    <>
      <Card className="border-border/60 hover:border-border transition-all shadow-sm overflow-hidden flex flex-col justify-between">
        <CardContent className="p-5 space-y-4">
          {/* Top Row: Title, Status Badge & Action Menu */}
          <div className="flex items-start justify-between gap-2">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <h3 className="font-bold text-sm sm:text-base text-foreground">
                  {reminder.title}
                </h3>
              </div>

              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                {reminder.frequency_km && (
                  <span className="flex items-center gap-1 font-mono">
                    <Gauge className="h-3 w-3 text-muted-foreground/70" />
                    Ogni {reminder.frequency_km.toLocaleString("it-IT")} km
                  </span>
                )}
                {reminder.frequency_days && (
                  <span className="flex items-center gap-1 font-mono">
                    <Clock className="h-3 w-3 text-muted-foreground/70" />
                    Ogni {reminder.frequency_days} giorni
                  </span>
                )}
              </div>
            </div>

            <div className="flex items-center gap-1.5 shrink-0">
              <Badge
                variant="outline"
                className={`text-[10px] font-semibold py-0.5 px-2 ${
                  reminder.is_overdue
                    ? "border-rose-500/40 text-rose-400 bg-rose-500/10"
                    : isUrgent
                      ? "border-amber-500/40 text-amber-400 bg-amber-500/10"
                      : "border-emerald-500/40 text-emerald-400 bg-emerald-500/10"
                }`}
              >
                {reminder.is_overdue ? "Scaduto" : isUrgent ? "Imminente" : "In Regola"}
              </Badge>

              <Button
                variant="ghost"
                size="sm"
                className="h-7 w-7 p-0 text-muted-foreground hover:text-foreground"
                onClick={() => onEdit(reminder)}
                title="Modifica"
              >
                <Edit3 className="h-3.5 w-3.5" />
              </Button>
              <Button
                variant="ghost"
                size="sm"
                className="h-7 w-7 p-0 text-muted-foreground hover:text-rose-400"
                onClick={() => setDeleteDialogOpen(true)}
                title="Elimina"
              >
                <Trash2 className="h-3.5 w-3.5" />
              </Button>
            </div>
          </div>

          {/* Progress Bar & Status Message */}
          <div className="space-y-1.5">
            <div className="flex items-center justify-between text-xs">
              <span
                className={`font-semibold ${
                  reminder.is_overdue
                    ? "text-rose-400"
                    : isUrgent
                      ? "text-amber-400"
                      : "text-foreground"
                }`}
              >
                {reminder.status_message}
              </span>
              <span className="font-mono text-xs text-muted-foreground">
                {pct}%
              </span>
            </div>

            {/* Visual Progress Bar Rail */}
            <div className="h-2.5 w-full rounded-full bg-muted/40 overflow-hidden relative">
              <div
                className={`h-full transition-all duration-500 rounded-full ${
                  reminder.is_overdue
                    ? "bg-rose-500 shadow-sm shadow-rose-500/40"
                    : isUrgent
                      ? "bg-amber-500 shadow-sm shadow-amber-500/40"
                      : "bg-emerald-500 shadow-sm shadow-emerald-500/40"
                }`}
                style={{ width: `${pct}%` }}
              />
            </div>
          </div>

          {/* Detailed Info Grid: Targets and Last checks */}
          <div className="grid grid-cols-2 gap-2 text-xs bg-muted/20 p-3 rounded-xl border border-border/40">
            <div>
              <span className="text-[10px] uppercase font-semibold text-muted-foreground block">
                Ultimo Controllo
              </span>
              <span className="font-mono text-foreground mt-0.5 block">
                {reminder.last_km_check !== null
                  ? `${reminder.last_km_check.toLocaleString("it-IT")} km`
                  : reminder.last_date_check || "—"}
              </span>
            </div>

            <div>
              <span className="text-[10px] uppercase font-semibold text-muted-foreground block">
                Obiettivo Ciclo
              </span>
              <span className="font-mono text-foreground mt-0.5 block">
                {reminder.target_km !== null
                  ? `${reminder.target_km.toLocaleString("it-IT")} km`
                  : reminder.target_date || "—"}
              </span>
            </div>
          </div>

          {reminder.notes && (
            <p className="text-xs text-muted-foreground italic truncate">
              {reminder.notes}
            </p>
          )}

          {/* Atomic CTA: Segna come Eseguito (Mark as Done) */}
          <Button
            variant={reminder.is_overdue ? "emerald" : "outline"}
            size="sm"
            className="w-full gap-2 font-semibold text-xs h-9 border-border/80 hover:border-emerald-500/50"
            onClick={handleMarkAsDone}
            disabled={completeMutation.isPending}
          >
            {completeMutation.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <CheckCircle2 className="h-4 w-4 text-emerald-400" />
            )}
            <span>Segna come Eseguito (Azzera Ciclo)</span>
          </Button>
        </CardContent>
      </Card>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-rose-400">
              <AlertCircle className="h-5 w-5" />
              Elimina Promemoria
            </DialogTitle>
            <DialogDescription>
              Sei sicuro di voler eliminare il promemoria <strong>&quot;{reminder.title}&quot;</strong>?
              Non riceverai più notifiche relative a questo controllo periodico.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="gap-2">
            <Button
              variant="outline"
              onClick={() => setDeleteDialogOpen(false)}
              disabled={deleteMutation.isPending}
            >
              Annulla
            </Button>
            <Button
              variant="destructive"
              onClick={handleDelete}
              disabled={deleteMutation.isPending}
              className="gap-2"
            >
              {deleteMutation.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
              Elimina Definitivamente
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}

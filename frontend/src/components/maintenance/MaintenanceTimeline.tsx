import { useState } from "react"
import {
  Wrench,
  Gauge,
  Clock,
  Edit3,
  Trash2,
  AlertTriangle,
  Loader2,
} from "lucide-react"
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
import { useDeleteMaintenance } from "@/hooks/useMaintenance"
import type { MaintenanceResponse } from "@/types"
import { toast } from "sonner"

interface MaintenanceTimelineProps {
  records: MaintenanceResponse[]
  onEdit: (record: MaintenanceResponse) => void
}

const CATEGORY_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  Tagliando: { bg: "bg-emerald-500/10", text: "text-emerald-400", border: "border-emerald-500/30" },
  Freni: { bg: "bg-rose-500/10", text: "text-rose-400", border: "border-rose-500/30" },
  Gomme: { bg: "bg-blue-500/10", text: "text-blue-400", border: "border-blue-500/30" },
  Revisione: { bg: "bg-purple-500/10", text: "text-purple-400", border: "border-purple-500/30" },
  Batteria: { bg: "bg-amber-500/10", text: "text-amber-400", border: "border-amber-500/30" },
  "Olio & Filtri": { bg: "bg-teal-500/10", text: "text-teal-400", border: "border-teal-500/30" },
  Distribuzione: { bg: "bg-orange-500/10", text: "text-orange-400", border: "border-orange-500/30" },
}

export function MaintenanceTimeline({ records, onEdit }: MaintenanceTimelineProps) {
  const [deleteTarget, setDeleteTarget] = useState<MaintenanceResponse | null>(null)
  const deleteMutation = useDeleteMaintenance()

  if (records.length === 0) {
    return (
      <div className="p-12 text-center text-muted-foreground space-y-3 rounded-2xl border border-dashed border-border/60">
        <div className="mx-auto w-12 h-12 rounded-full bg-muted/40 flex items-center justify-center text-muted-foreground">
          <Wrench className="h-6 w-6" />
        </div>
        <p className="text-sm font-medium">Nessun intervento registrato.</p>
        <p className="text-xs text-muted-foreground">
          Utilizza il pulsante in alto a destra per inserire la prima voce del libretto officina.
        </p>
      </div>
    )
  }

  const handleDelete = async () => {
    if (!deleteTarget) return
    try {
      await deleteMutation.mutateAsync(deleteTarget.id)
      toast.success("Intervento eliminato con successo")
      setDeleteTarget(null)
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Errore durante l'eliminazione"
      toast.error(msg)
    }
  }

  return (
    <>
      <div className="relative pl-6 sm:pl-8 space-y-6 before:absolute before:left-2.5 sm:before:left-3.5 before:top-3 before:bottom-3 before:w-0.5 before:bg-border/60">
        {records.map((r) => {
          const color = CATEGORY_COLORS[r.expense_type] || {
            bg: "bg-muted/40",
            text: "text-foreground",
            border: "border-border",
          }

          return (
            <div key={r.id} className="relative group">
              {/* Timeline Marker Dot */}
              <div
                className={`absolute -left-6 sm:-left-8 top-4 w-5 h-5 rounded-full border-2 border-background flex items-center justify-center shadow-sm ${color.bg} ${color.border}`}
              >
                <div className={`w-2 h-2 rounded-full ${color.text} bg-current`} />
              </div>

              {/* Timeline Card Content */}
              <div className="p-4 sm:p-5 rounded-2xl bg-card border border-border/60 hover:border-border transition-all shadow-sm space-y-3">
                {/* Header Row: Date, Category Pill, Cost */}
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-foreground">
                      {r.date}
                    </span>
                    <Badge
                      variant="outline"
                      className={`text-xs font-semibold py-0.5 px-2 ${color.bg} ${color.text} ${color.border}`}
                    >
                      {r.expense_type}
                    </Badge>
                  </div>

                  <div className="flex items-center gap-3">
                    <span className="font-mono text-lg font-extrabold text-foreground">
                      {r.cost.toFixed(2)} €
                    </span>
                    <div className="flex items-center gap-1 opacity-80 group-hover:opacity-100 transition-opacity">
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-8 w-8 p-0 text-muted-foreground hover:text-foreground"
                        onClick={() => onEdit(r)}
                        title="Modifica intervento"
                      >
                        <Edit3 className="h-3.5 w-3.5" />
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-8 w-8 p-0 text-muted-foreground hover:text-rose-400"
                        onClick={() => setDeleteTarget(r)}
                        title="Elimina intervento"
                      >
                        <Trash2 className="h-3.5 w-3.5" />
                      </Button>
                    </div>
                  </div>
                </div>

                {/* Second Row: Km, Description */}
                <div className="space-y-1.5">
                  <div className="flex items-center gap-1.5 text-xs text-muted-foreground font-mono">
                    <Gauge className="h-3.5 w-3.5" />
                    <span>Chilometraggio: {r.total_km.toLocaleString("it-IT")} km</span>
                  </div>

                  {r.description ? (
                    <p className="text-xs text-foreground/90 bg-muted/20 p-2.5 rounded-xl border border-border/40">
                      {r.description}
                    </p>
                  ) : (
                    <p className="text-xs italic text-muted-foreground">
                      Nessuna descrizione o ricambio specificato.
                    </p>
                  )}
                </div>

                {/* Expiry / Next Scheduled Target Footer */}
                {(r.expiry_km || r.expiry_date) && (
                  <div className="pt-2 border-t border-border/40 flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
                    <span className="flex items-center gap-1 text-[11px] font-semibold text-amber-400/90">
                      <Clock className="h-3 w-3" />
                      Prossimo intervento:
                    </span>
                    {r.expiry_km && (
                      <span className="font-mono text-[11px]">
                        Target {r.expiry_km.toLocaleString("it-IT")} km
                      </span>
                    )}
                    {r.expiry_date && (
                      <span className="font-mono text-[11px]">
                        Entro il {r.expiry_date}
                      </span>
                    )}
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>

      {/* Delete Confirmation Dialog */}
      <Dialog open={!!deleteTarget} onOpenChange={(val) => !val && setDeleteTarget(null)}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-rose-400">
              <AlertTriangle className="h-5 w-5" />
              Conferma Eliminazione
            </DialogTitle>
            <DialogDescription>
              Sei sicuro di voler eliminare l&apos;intervento di manutenzione del{" "}
              <strong>{deleteTarget?.date}</strong> ({deleteTarget?.expense_type} - €{" "}
              {deleteTarget?.cost.toFixed(2)})? L&apos;operazione è irreversibile.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="gap-2">
            <Button
              variant="outline"
              onClick={() => setDeleteTarget(null)}
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

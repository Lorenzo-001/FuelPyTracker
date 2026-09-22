import { useState } from "react"
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
  SheetFooter,
} from "@/components/ui/sheet"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  Fuel,
  Gauge,
  TrendingUp,
  Calendar,
  Wallet,
  Clock,
  Edit3,
  Trash2,
  AlertTriangle,
  FileText,
  Loader2,
} from "lucide-react"
import { format, parseISO } from "date-fns"
import { it } from "date-fns/locale"
import { useDeleteRefueling } from "@/hooks/useRefuelings"
import type { RefuelingResponse } from "@/types"
import { toast } from "sonner"

interface FuelInspectorSheetProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  refueling: RefuelingResponse | null
  onEdit: (refueling: RefuelingResponse) => void
}

export function FuelInspectorSheet({
  open,
  onOpenChange,
  refueling,
  onEdit,
}: FuelInspectorSheetProps) {
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false)
  const deleteMutation = useDeleteRefueling()

  if (!refueling) return null

  let formattedDate = refueling.date
  try {
    formattedDate = format(parseISO(refueling.date), "EEEE d MMMM yyyy", { locale: it })
  } catch {
    // Keep raw string on parsing failure
  }

  const costPerKm =
    refueling.delta_km && refueling.delta_km > 0
      ? (refueling.total_cost / refueling.delta_km).toFixed(3)
      : null

  const handleDelete = async () => {
    try {
      await deleteMutation.mutateAsync(refueling.id)
      toast.success("Rifornimento eliminato con successo")
      setDeleteConfirmOpen(false)
      onOpenChange(false)
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Errore durante l'eliminazione"
      toast.error(msg)
    }
  }

  return (
    <>
      <Sheet open={open} onOpenChange={onOpenChange}>
        <SheetContent side="right" className="sm:max-w-md w-full overflow-y-auto flex flex-col justify-between">
          <div>
            <SheetHeader className="pb-4 border-b border-border/60">
              <div className="flex items-center justify-between gap-2">
                <Badge
                  variant="outline"
                  className={
                    refueling.is_full_tank
                      ? "border-emerald-500/30 text-emerald-400 bg-emerald-500/10"
                      : "border-amber-500/30 text-amber-400 bg-amber-500/10"
                  }
                >
                  {refueling.is_full_tank ? "Pieno Completo" : "Rifornimento Parziale"}
                </Badge>
                <span className="text-xs text-muted-foreground font-mono">
                  ID #{refueling.id}
                </span>
              </div>
              <SheetTitle className="text-lg font-bold capitalize mt-2 flex items-center gap-2">
                <Calendar className="h-4 w-4 text-emerald-400 shrink-0" />
                {formattedDate}
              </SheetTitle>
              <SheetDescription className="text-xs">
                Dettaglio completo dei parametri chilometrici ed efficienza energetica.
              </SheetDescription>
            </SheetHeader>

            {/* KPI High-Density Grid */}
            <div className="py-5 space-y-4">
              {/* Card Efficienza */}
              <div className="p-4 rounded-xl bg-muted/30 border border-border/50 space-y-3">
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider block">
                  Metrica di Rendimento
                </span>
                <div className="flex items-baseline justify-between">
                  <div>
                    <span className="text-3xl font-extrabold font-mono text-emerald-400">
                      {refueling.km_per_liter !== null
                        ? refueling.km_per_liter.toFixed(2)
                        : "—"}
                    </span>
                    <span className="ml-1.5 text-sm font-medium text-muted-foreground">
                      km/L
                    </span>
                  </div>

                  {refueling.delta_km !== null && (
                    <div className="text-right">
                      <span className="text-xs text-muted-foreground block">Tratta percorsa</span>
                      <span className="text-sm font-bold font-mono text-foreground">
                        +{refueling.delta_km.toLocaleString("it-IT")} km
                      </span>
                    </div>
                  )}
                </div>

                {refueling.km_per_liter === null && (
                  <p className="text-[11px] text-amber-300/80 bg-amber-500/10 p-2 rounded-lg border border-amber-500/20">
                    Consumo non calcolabile per rifornimento parziale. Verrà integrato al prossimo pieno completo.
                  </p>
                )}
              </div>

              {/* Parametri Rifornimento */}
              <div className="grid grid-cols-2 gap-2.5 text-xs">
                <div className="p-3 rounded-xl bg-card border border-border/60">
                  <div className="flex items-center gap-1.5 text-muted-foreground mb-1">
                    <Wallet className="h-3.5 w-3.5" />
                    <span>Importo Speso</span>
                  </div>
                  <span className="text-base font-bold font-mono text-foreground">
                    {refueling.total_cost.toFixed(2)} €
                  </span>
                </div>

                <div className="p-3 rounded-xl bg-card border border-border/60">
                  <div className="flex items-center gap-1.5 text-muted-foreground mb-1">
                    <Fuel className="h-3.5 w-3.5" />
                    <span>Litri Erogati</span>
                  </div>
                  <span className="text-base font-bold font-mono text-foreground">
                    {refueling.liters.toFixed(2)} L
                  </span>
                </div>

                <div className="p-3 rounded-xl bg-card border border-border/60">
                  <div className="flex items-center gap-1.5 text-muted-foreground mb-1">
                    <TrendingUp className="h-3.5 w-3.5" />
                    <span>Prezzo al Litro</span>
                  </div>
                  <span className="text-base font-bold font-mono text-foreground">
                    {refueling.price_per_liter.toFixed(3)} €/L
                  </span>
                </div>

                <div className="p-3 rounded-xl bg-card border border-border/60">
                  <div className="flex items-center gap-1.5 text-muted-foreground mb-1">
                    <Gauge className="h-3.5 w-3.5" />
                    <span>Contachilometri</span>
                  </div>
                  <span className="text-base font-bold font-mono text-foreground">
                    {refueling.total_km.toLocaleString("it-IT")} km
                  </span>
                </div>
              </div>

              {/* Indicatori Secondari */}
              <div className="space-y-2 text-xs">
                {costPerKm && (
                  <div className="flex items-center justify-between p-2.5 rounded-lg bg-muted/20 border border-border/40">
                    <span className="text-muted-foreground">Costo per chilometro:</span>
                    <span className="font-mono font-semibold text-foreground">
                      {costPerKm} €/km
                    </span>
                  </div>
                )}

                {refueling.days_since_last !== null && (
                  <div className="flex items-center justify-between p-2.5 rounded-lg bg-muted/20 border border-border/40">
                    <span className="text-muted-foreground flex items-center gap-1.5">
                      <Clock className="h-3.5 w-3.5" />
                      Intervallo dal pieno precedente:
                    </span>
                    <span className="font-mono font-semibold text-foreground">
                      {refueling.days_since_last} giorni
                    </span>
                  </div>
                )}
              </div>

              {/* Note / Stazione */}
              <div className="p-3 rounded-xl bg-muted/20 border border-border/40 space-y-1.5">
                <div className="flex items-center gap-1.5 text-xs font-semibold text-muted-foreground">
                  <FileText className="h-3.5 w-3.5" />
                  <span>Stazione & Note</span>
                </div>
                <p className="text-xs text-foreground/90">
                  {refueling.notes || (
                    <span className="italic text-muted-foreground">Nessuna nota registrata.</span>
                  )}
                </p>
              </div>
            </div>
          </div>

          {/* Sheet Footer Actions */}
          <SheetFooter className="pt-4 border-t border-border/60 flex-col sm:flex-row gap-2">
            <Button
              variant="outline"
              className="gap-1.5 flex-1"
              onClick={() => {
                onOpenChange(false)
                onEdit(refueling)
              }}
            >
              <Edit3 className="h-4 w-4" />
              Modifica
            </Button>
            <Button
              variant="destructive"
              className="gap-1.5 flex-1"
              onClick={() => setDeleteConfirmOpen(true)}
            >
              <Trash2 className="h-4 w-4" />
              Elimina
            </Button>
          </SheetFooter>
        </SheetContent>
      </Sheet>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteConfirmOpen} onOpenChange={setDeleteConfirmOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2 text-rose-400">
              <AlertTriangle className="h-5 w-5" />
              Conferma Eliminazione
            </DialogTitle>
            <DialogDescription>
              Sei sicuro di voler eliminare il rifornimento del{" "}
              <strong>{refueling.date}</strong> ({refueling.total_km.toLocaleString("it-IT")} km)?
              Questa azione è irreversibile e ricalcolerà l&apos;efficienza chilometrica dei pieni successivi.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter className="gap-2">
            <Button
              variant="outline"
              onClick={() => setDeleteConfirmOpen(false)}
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

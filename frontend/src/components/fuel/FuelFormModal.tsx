import { useState, useEffect } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import {
  Fuel,
  CheckCircle2,
  AlertTriangle,
  Loader2,
  Calendar,
  Gauge,
  Sparkles,
} from "lucide-react"
import {
  useCreateRefueling,
  useUpdateRefueling,
  useValidateRefueling,
} from "@/hooks/useRefuelings"
import type { RefuelingResponse } from "@/types"
import { toast } from "sonner"

const refuelingSchema = z.object({
  date: z.string().min(1, "La data è obbligatoria"),
  total_km: z
    .number({ invalid_type_error: "Inserisci un numero valido" })
    .int("I chilometri devono essere un numero intero")
    .positive("I chilometri devono essere maggiori di 0"),
  price_per_liter: z
    .number({ invalid_type_error: "Inserisci un prezzo valido" })
    .positive("Il prezzo al litro deve essere maggiore di 0"),
  total_cost: z
    .number({ invalid_type_error: "Inserisci un totale valido" })
    .positive("Il costo totale deve essere maggiore di 0"),
  liters: z
    .number({ invalid_type_error: "Inserisci una quantità valida" })
    .positive("I litri devono essere maggiori di 0"),
  is_full_tank: z.boolean(),
  notes: z.string().optional(),
})

type RefuelingFormData = z.infer<typeof refuelingSchema>

interface FuelFormModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  initialData?: RefuelingResponse | null
  prefillData?: Partial<RefuelingFormData> | null
}

export function FuelFormModal({
  open,
  onOpenChange,
  initialData,
  prefillData,
}: FuelFormModalProps) {
  const isEditing = !!initialData
  const createMutation = useCreateRefueling()
  const updateMutation = useUpdateRefueling()
  const validateMutation = useValidateRefueling()

  const [validationState, setValidationState] = useState<{
    checked: boolean
    isValid: boolean
    message: string
    prevKm?: number | null
    nextKm?: number | null
  } | null>(null)

  const todayStr = new Date().toISOString().split("T")[0]

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<RefuelingFormData>({
    resolver: zodResolver(refuelingSchema),
    defaultValues: {
      date: todayStr,
      total_km: undefined,
      price_per_liter: undefined,
      total_cost: undefined,
      liters: undefined,
      is_full_tank: true,
      notes: "",
    },
  })

  const watchedTotalKm = watch("total_km")
  const watchedDate = watch("date")
  const watchedPrice = watch("price_per_liter")
  const watchedCost = watch("total_cost")
  const watchedIsFull = watch("is_full_tank")

  // Reset form when modal opens with initialData or prefillData
  useEffect(() => {
    if (open) {
      if (initialData) {
        reset({
          date: initialData.date,
          total_km: initialData.total_km,
          price_per_liter: initialData.price_per_liter,
          total_cost: initialData.total_cost,
          liters: initialData.liters,
          is_full_tank: initialData.is_full_tank,
          notes: initialData.notes || "",
        })
      } else if (prefillData) {
        reset({
          date: prefillData.date || todayStr,
          total_km: prefillData.total_km,
          price_per_liter: prefillData.price_per_liter,
          total_cost: prefillData.total_cost,
          liters: prefillData.liters,
          is_full_tank: prefillData.is_full_tank ?? true,
          notes: prefillData.notes || "",
        })
      } else {
        reset({
          date: todayStr,
          total_km: undefined,
          price_per_liter: undefined,
          total_cost: undefined,
          liters: undefined,
          is_full_tank: true,
          notes: "",
        })
      }
      setValidationState(null)
    }
  }, [open, initialData, prefillData, reset, todayStr])

  // Bidirectional calculation: Euro & Price -> Liters
  const handleCostChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = parseFloat(e.target.value)
    if (!isNaN(val) && watchedPrice && watchedPrice > 0) {
      const computedLiters = parseFloat((val / watchedPrice).toFixed(2))
      setValue("liters", computedLiters, { shouldValidate: true })
    }
  }

  // Bidirectional calculation: Liters & Price -> Euro
  const handleLitersChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = parseFloat(e.target.value)
    if (!isNaN(val) && watchedPrice && watchedPrice > 0) {
      const computedCost = parseFloat((val * watchedPrice).toFixed(2))
      setValue("total_cost", computedCost, { shouldValidate: true })
    }
  }

  // Bidirectional calculation: Price changed -> recompute liters if cost exists
  const handlePriceChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = parseFloat(e.target.value)
    if (!isNaN(val) && val > 0 && watchedCost && watchedCost > 0) {
      const computedLiters = parseFloat((watchedCost / val).toFixed(2))
      setValue("liters", computedLiters, { shouldValidate: true })
    }
  }

  // Live Pre-flight validation on blur of total_km
  const triggerKmValidation = async () => {
    if (!watchedTotalKm || watchedTotalKm <= 0 || !watchedDate) return
    try {
      const res = await validateMutation.mutateAsync({
        date: watchedDate,
        km: watchedTotalKm,
        price: watchedPrice || 1.8,
        cost: watchedCost || 50,
        is_full: watchedIsFull,
      })
      setValidationState({
        checked: true,
        isValid: res.is_valid,
        message: res.message,
        prevKm: res.prev_km,
        nextKm: res.next_km,
      })
    } catch {
      // Ignore network errors in validation preflight
    }
  }

  const onSubmit = async (data: RefuelingFormData) => {
    try {
      if (isEditing && initialData) {
        await updateMutation.mutateAsync({
          id: initialData.id,
          data: {
            date: data.date,
            total_km: data.total_km,
            price_per_liter: data.price_per_liter,
            total_cost: data.total_cost,
            liters: data.liters,
            is_full_tank: data.is_full_tank,
            notes: data.notes || null,
          },
        })
        toast.success("Rifornimento aggiornato con successo!")
      } else {
        await createMutation.mutateAsync({
          date: data.date,
          total_km: data.total_km,
          price_per_liter: data.price_per_liter,
          total_cost: data.total_cost,
          liters: data.liters,
          is_full_tank: data.is_full_tank,
          notes: data.notes || null,
        })
        toast.success("Nuovo pieno registrato nel registro!")
      }
      onOpenChange(false)
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Errore durante il salvataggio"
      toast.error(msg)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-lg max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-xl font-bold">
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
              <Fuel className="h-5 w-5" />
            </div>
            {isEditing ? "Modifica Rifornimento" : "Registra Nuovo Pieno"}
          </DialogTitle>
          <DialogDescription>
            {isEditing
              ? "Aggiorna i parametri del rifornimento selezionato. I calcoli di consumo verranno riallineati automaticamente."
              : "Inserisci i dati del rifornimento. La coerenza chilometrica e il consumo medio verranno calcolati in tempo reale."}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 py-2">
          {/* Row 1: Data e Chilometri */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <Label htmlFor="date" className="flex items-center gap-1.5 text-xs font-semibold">
                <Calendar className="h-3.5 w-3.5 text-muted-foreground" />
                Data Rifornimento
              </Label>
              <Input
                id="date"
                type="date"
                {...register("date")}
                className="bg-muted/40 font-mono text-sm"
              />
              {errors.date && (
                <p className="text-xs text-rose-400">{errors.date.message}</p>
              )}
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="total_km" className="flex items-center gap-1.5 text-xs font-semibold">
                <Gauge className="h-3.5 w-3.5 text-muted-foreground" />
                Chilometri Totali
              </Label>
              <div className="relative">
                <Input
                  id="total_km"
                  type="number"
                  placeholder="Es. 120650"
                  {...register("total_km", {
                    valueAsNumber: true,
                    onBlur: triggerKmValidation,
                  })}
                  className="pr-12 font-mono text-sm"
                />
                <span className="absolute right-3 top-2.5 text-xs font-semibold text-muted-foreground">
                  km
                </span>
              </div>
              {errors.total_km && (
                <p className="text-xs text-rose-400">{errors.total_km.message}</p>
              )}
            </div>
          </div>

          {/* Validation Feedback Banner */}
          {validateMutation.isPending && (
            <div className="flex items-center gap-2 p-2.5 rounded-lg bg-muted/40 text-xs text-muted-foreground animate-pulse">
              <Loader2 className="h-3.5 w-3.5 animate-spin text-emerald-400" />
              Verifica coerenza chilometrica in corso...
            </div>
          )}

          {validationState?.checked && (
            <div
              className={`p-3 rounded-lg text-xs flex items-start gap-2.5 border transition-all ${
                validationState.isValid
                  ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-300"
                  : "bg-amber-500/10 border-amber-500/20 text-amber-300"
              }`}
            >
              {validationState.isValid ? (
                <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-400 mt-0.5" />
              ) : (
                <AlertTriangle className="h-4 w-4 shrink-0 text-amber-400 mt-0.5" />
              )}
              <div>
                <p className="font-semibold">
                  {validationState.isValid
                    ? "Chilometraggio coerente"
                    : "Attenzione sulla sequenza chilometrica"}
                </p>
                <p className="text-muted-foreground mt-0.5 text-[11px]">
                  {validationState.message ||
                    (validationState.prevKm
                      ? `Rifornimento precedente registrato a ${validationState.prevKm.toLocaleString("it-IT")} km.`
                      : "Primo rifornimento registrato.")}
                </p>
              </div>
            </div>
          )}

          {/* Row 2: Prezzo/L, Totale Spesa, Litri */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="price_per_liter" className="text-xs font-semibold">
                Prezzo al Litro
              </Label>
              <div className="relative">
                <Input
                  id="price_per_liter"
                  type="number"
                  step="0.001"
                  placeholder="1.799"
                  {...register("price_per_liter", {
                    valueAsNumber: true,
                    onChange: handlePriceChange,
                  })}
                  className="pr-10 font-mono text-sm"
                />
                <span className="absolute right-3 top-2.5 text-xs text-muted-foreground">
                  €/L
                </span>
              </div>
              {errors.price_per_liter && (
                <p className="text-xs text-rose-400">{errors.price_per_liter.message}</p>
              )}
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="total_cost" className="text-xs font-semibold">
                Totale Spesa
              </Label>
              <div className="relative">
                <Input
                  id="total_cost"
                  type="number"
                  step="0.01"
                  placeholder="65.00"
                  {...register("total_cost", {
                    valueAsNumber: true,
                    onChange: handleCostChange,
                  })}
                  className="pr-7 font-mono text-sm font-medium"
                />
                <span className="absolute right-3 top-2.5 text-xs text-muted-foreground">
                  €
                </span>
              </div>
              {errors.total_cost && (
                <p className="text-xs text-rose-400">{errors.total_cost.message}</p>
              )}
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="liters" className="text-xs font-semibold">
                Litri Erogati
              </Label>
              <div className="relative">
                <Input
                  id="liters"
                  type="number"
                  step="0.01"
                  placeholder="36.13"
                  {...register("liters", {
                    valueAsNumber: true,
                    onChange: handleLitersChange,
                  })}
                  className="pr-7 font-mono text-sm"
                />
                <span className="absolute right-3 top-2.5 text-xs text-muted-foreground">
                  L
                </span>
              </div>
              {errors.liters && (
                <p className="text-xs text-rose-400">{errors.liters.message}</p>
              )}
            </div>
          </div>

          {/* Row 3: Toggle Pieno Completo */}
          <div className="p-3 rounded-xl bg-muted/30 border border-border/50 flex items-center justify-between gap-3">
            <div className="space-y-0.5">
              <div className="flex items-center gap-2">
                <span className="text-sm font-semibold">Serbatoio Pieno Completo</span>
                <Badge
                  variant="outline"
                  className={
                    watchedIsFull
                      ? "border-emerald-500/30 text-emerald-400 bg-emerald-500/10"
                      : "border-amber-500/30 text-amber-400 bg-amber-500/10"
                  }
                >
                  {watchedIsFull ? "Pieno Full-to-Full" : "Rifornimento Parziale"}
                </Badge>
              </div>
              <p className="text-xs text-muted-foreground">
                Disattiva se hai immesso solo una quantità parziale senza riempire fino allo scatto.
              </p>
            </div>

            <label className="relative inline-flex items-center cursor-pointer shrink-0">
              <input
                type="checkbox"
                {...register("is_full_tank")}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-muted peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-500"></div>
            </label>
          </div>

          {/* Row 4: Distributore e Note */}
          <div className="space-y-1.5">
            <Label htmlFor="notes" className="text-xs font-semibold">
              Distributore / Note
            </Label>
            <Input
              id="notes"
              placeholder="Es. Eni Station Milano Viale Certosa, autostrada A4..."
              {...register("notes")}
              className="text-sm"
            />
          </div>

          <DialogFooter className="pt-2 sm:space-x-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={isSubmitting}
            >
              Annulla
            </Button>
            <Button
              type="submit"
              variant="emerald"
              disabled={isSubmitting || createMutation.isPending || updateMutation.isPending}
              className="gap-2"
            >
              {(isSubmitting || createMutation.isPending || updateMutation.isPending) && (
                <Loader2 className="h-4 w-4 animate-spin" />
              )}
              {isEditing ? (
                "Salva Modifiche"
              ) : (
                <>
                  <Sparkles className="h-4 w-4" />
                  Registra Rifornimento
                </>
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

import { useEffect } from "react"
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
import { CalendarClock, Gauge, Clock, Loader2, Sparkles } from "lucide-react"
import { useCreateReminder, useUpdateReminder } from "@/hooks/useReminders"
import { useRefuelings } from "@/hooks/useRefuelings"
import { useSettings } from "@/hooks/useSettings"
import type { ReminderResponse } from "@/types"
import { toast } from "sonner"

const reminderSchema = z
  .object({
    title: z.string().min(2, "Il titolo deve contenere almeno 2 caratteri"),
    frequency_type: z.enum(["days", "km"]),
    frequency_days: z
      .number({ invalid_type_error: "Inserisci un numero valido" })
      .positive("I giorni devono essere maggiori di 0")
      .optional()
      .nullable(),
    frequency_km: z
      .number({ invalid_type_error: "Inserisci un numero valido" })
      .positive("L'intervallo km deve essere maggiore di 0")
      .optional()
      .nullable(),
    current_km: z
      .number({ invalid_type_error: "Inserisci i chilometri attuali" })
      .min(1, "I chilometri attuali devono essere maggiori di 0")
      .optional()
      .nullable(),
    notes: z.string().optional(),
  })
  .refine(
    (data) => {
      if (data.frequency_type === "km") {
        return typeof data.current_km === "number" && data.current_km > 0
      }
      return true
    },
    {
      message: "I chilometri attuali sono obbligatori per i controlli a base chilometrica",
      path: ["current_km"],
    }
  )
  .refine(
    (data) => {
      if (data.frequency_type === "km") {
        return typeof data.frequency_km === "number" && data.frequency_km > 0
      }
      return true
    },
    {
      message: "L'intervallo km è obbligatorio",
      path: ["frequency_km"],
    }
  )
  .refine(
    (data) => {
      if (data.frequency_type === "days") {
        return typeof data.frequency_days === "number" && data.frequency_days > 0
      }
      return true
    },
    {
      message: "L'intervallo giorni è obbligatorio",
      path: ["frequency_days"],
    }
  )

type ReminderFormData = z.infer<typeof reminderSchema>

const PRESETS = [
  { title: "Controllo Pressione Pneumatici", type: "days" as const, days: 30, km: null },
  { title: "Verifica Livello Olio Motore", type: "km" as const, days: null, km: 3000 },
  { title: "Rabbocco Liquido Tergicristalli", type: "days" as const, days: 60, km: null },
  { title: "Controllo Liquido Refrigerante", type: "km" as const, days: null, km: 10000 },
  { title: "Lavaggio & Cura Carrozzeria", type: "days" as const, days: 30, km: null },
]

interface ReminderFormModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  initialData?: ReminderResponse | null
}

export function ReminderFormModal({
  open,
  onOpenChange,
  initialData,
}: ReminderFormModalProps) {
  const isEditing = !!initialData
  const createMutation = useCreateReminder()
  const updateMutation = useUpdateReminder()
  const { data: settings } = useSettings()
  const { data: refuelings } = useRefuelings()

  const latestRefuelingKm = Math.max(
    ...(refuelings?.map((r) => r.total_km) || [0]),
    0
  )

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<ReminderFormData>({
    resolver: zodResolver(reminderSchema),
    defaultValues: {
      title: "",
      frequency_type: "days",
      frequency_days: 30,
      frequency_km: null,
      current_km: null,
      notes: "",
    },
  })

  const freqType = watch("frequency_type")

  useEffect(() => {
    if (open) {
      if (initialData) {
        reset({
          title: initialData.title,
          frequency_type: initialData.frequency_km ? "km" : "days",
          frequency_days: initialData.frequency_days || null,
          frequency_km: initialData.frequency_km || null,
          current_km: initialData.last_km_check ?? (latestRefuelingKm > 0 ? latestRefuelingKm : null),
          notes: initialData.notes || "",
        })
      } else {
        reset({
          title: "",
          frequency_type: "days",
          frequency_days: 30,
          frequency_km: null,
          current_km: latestRefuelingKm > 0 ? latestRefuelingKm : null,
          notes: "",
        })
      }
    }
  }, [open, initialData, latestRefuelingKm, reset])

  const applyPreset = (preset: typeof PRESETS[0]) => {
    setValue("title", preset.title, { shouldValidate: true })
    setValue("frequency_type", preset.type, { shouldValidate: true })
    if (preset.type === "days") {
      setValue("frequency_days", preset.days, { shouldValidate: true })
      setValue("frequency_km", null)
      setValue("current_km", null)
    } else {
      setValue("frequency_km", preset.km, { shouldValidate: true })
      setValue("frequency_days", null)
      if (!watch("current_km") && latestRefuelingKm > 0) {
        setValue("current_km", latestRefuelingKm, { shouldValidate: true })
      }
    }
  }

  const onSubmit = async (data: ReminderFormData) => {
    try {
      if (isEditing && initialData) {
        await updateMutation.mutateAsync({
          id: initialData.id,
          data: {
            title: data.title,
            frequency_days: data.frequency_type === "days" ? data.frequency_days : null,
            frequency_km: data.frequency_type === "km" ? data.frequency_km : null,
            current_km: data.frequency_type === "km" ? data.current_km : null,
            notes: data.notes || null,
          },
        })
        toast.success("Promemoria aggiornato con successo!")
      } else {
        await createMutation.mutateAsync({
          title: data.title,
          frequency_days: data.frequency_type === "days" ? data.frequency_days : null,
          frequency_km: data.frequency_type === "km" ? data.frequency_km : null,
          current_km: data.frequency_type === "km" ? data.current_km : null,
          notes: data.notes || null,
        })
        toast.success("Nuovo promemoria attivato!")
      }
      onOpenChange(false)
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Errore durante il salvataggio"
      toast.error(msg)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-xl font-bold">
            <div className="p-2 rounded-lg bg-rose-500/10 text-rose-400">
              <CalendarClock className="h-5 w-5" />
            </div>
            {isEditing ? "Modifica Promemoria" : "Nuovo Promemoria Routine"}
          </DialogTitle>
          <DialogDescription>
            Imposta controlli ricorrenti per tenere sempre sotto controllo i liquidi e lo stato del veicolo.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4 py-2">
          {/* Presets Quick Pills */}
          {!isEditing && (
            <div className="space-y-1.5">
              <Label className="text-xs font-semibold text-muted-foreground">
                Suggerimenti Rapidi & Categorie
              </Label>
              <div className="flex flex-wrap gap-1.5">
                {PRESETS.map((p) => (
                  <Badge
                    key={p.title}
                    variant="outline"
                    onClick={() => applyPreset(p)}
                    className="cursor-pointer hover:bg-muted/50 transition-all text-xs py-1"
                  >
                    {p.title}
                  </Badge>
                ))}
                {settings?.reminder_types
                  ?.filter((t) => !PRESETS.some((p) => p.title.toLowerCase() === t.toLowerCase()))
                  .map((customType) => (
                    <Badge
                      key={customType}
                      variant="outline"
                      onClick={() => setValue("title", customType, { shouldValidate: true })}
                      className="cursor-pointer hover:bg-cyan-500/20 text-cyan-300 border-cyan-500/30 transition-all text-xs py-1"
                    >
                      {customType}
                    </Badge>
                  ))}
              </div>
            </div>
          )}

          {/* Title */}
          <div className="space-y-1.5">
            <Label htmlFor="title" className="text-xs font-semibold">
              Titolo del Controllo
            </Label>
            <Input
              id="title"
              placeholder="Es. Pressione gomme, cambio filtro abitacolo..."
              {...register("title")}
              className="text-sm"
            />
            {errors.title && (
              <p className="text-xs text-rose-400">{errors.title.message}</p>
            )}
          </div>

          {/* Frequency Type Selector: Days vs Km */}
          <div className="space-y-1.5">
            <Label className="text-xs font-semibold text-muted-foreground">
              Tipologia Frequenza
            </Label>
            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={() => {
                  setValue("frequency_type", "days")
                  setValue("frequency_km", null)
                  if (!watch("frequency_days")) setValue("frequency_days", 30)
                }}
                className={`p-2.5 rounded-xl border text-xs font-semibold flex items-center justify-center gap-2 transition-all ${
                  freqType === "days"
                    ? "border-emerald-500/50 bg-emerald-500/10 text-emerald-400"
                    : "border-border/60 bg-muted/20 text-muted-foreground hover:text-foreground"
                }`}
              >
                <Clock className="h-4 w-4" />
                <span>Base Temporale (Giorni)</span>
              </button>

              <button
                type="button"
                onClick={() => {
                  setValue("frequency_type", "km")
                  setValue("frequency_days", null)
                  if (!watch("frequency_km")) setValue("frequency_km", 5000)
                  if (!watch("current_km") && latestRefuelingKm > 0) {
                    setValue("current_km", latestRefuelingKm, { shouldValidate: true })
                  }
                }}
                className={`p-2.5 rounded-xl border text-xs font-semibold flex items-center justify-center gap-2 transition-all ${
                  freqType === "km"
                    ? "border-emerald-500/50 bg-emerald-500/10 text-emerald-400"
                    : "border-border/60 bg-muted/20 text-muted-foreground hover:text-foreground"
                }`}
              >
                <Gauge className="h-4 w-4" />
                <span>Base Chilometrica (Km)</span>
              </button>
            </div>
          </div>

          {/* Value input for Days or Km */}
          {freqType === "days" ? (
            <div className="space-y-1.5">
              <Label htmlFor="frequency_days" className="text-xs font-semibold">
                Ogni quanti giorni ripetere? <span className="text-destructive font-bold">*</span>
              </Label>
              <div className="relative">
                <Input
                  id="frequency_days"
                  type="number"
                  placeholder="30"
                  {...register("frequency_days", { valueAsNumber: true })}
                  className="pr-16 font-mono text-sm"
                />
                <span className="absolute right-3 top-2.5 text-xs text-muted-foreground">
                  giorni
                </span>
              </div>
              {errors.frequency_days && (
                <p className="text-xs text-rose-400">{errors.frequency_days.message}</p>
              )}
            </div>
          ) : (
            <div className="space-y-3">
              {/* Current Km (Required) */}
              <div className="space-y-1.5">
                <div className="flex items-center justify-between">
                  <Label htmlFor="current_km" className="text-xs font-semibold">
                    Chilometri Attuali del Veicolo <span className="text-destructive font-bold">*</span>
                  </Label>
                  {latestRefuelingKm > 0 && (
                    <span className="text-[11px] text-muted-foreground">
                      Ultimo rifornimento: <strong className="font-mono text-foreground">{latestRefuelingKm.toLocaleString("it-IT")} km</strong>
                    </span>
                  )}
                </div>
                <div className="relative">
                  <Input
                    id="current_km"
                    type="number"
                    placeholder={latestRefuelingKm > 0 ? String(latestRefuelingKm) : "Es. 125000"}
                    {...register("current_km", { valueAsNumber: true })}
                    className="pr-12 font-mono text-sm"
                  />
                  <span className="absolute right-3 top-2.5 text-xs text-muted-foreground">
                    km
                  </span>
                </div>
                {errors.current_km && (
                  <p className="text-xs text-rose-400">{errors.current_km.message}</p>
                )}
                <p className="text-[11px] text-muted-foreground">
                  Punto di partenza per il ciclo. Precompilato in automatico con l'ultimo valore registrato.
                </p>
              </div>

              {/* Frequency Km */}
              <div className="space-y-1.5">
                <Label htmlFor="frequency_km" className="text-xs font-semibold">
                  Ogni quanti chilometri ripetere? <span className="text-destructive font-bold">*</span>
                </Label>
                <div className="relative">
                  <Input
                    id="frequency_km"
                    type="number"
                    placeholder="5000"
                    {...register("frequency_km", { valueAsNumber: true })}
                    className="pr-12 font-mono text-sm"
                  />
                  <span className="absolute right-3 top-2.5 text-xs text-muted-foreground">
                    km
                  </span>
                </div>
                {errors.frequency_km && (
                  <p className="text-xs text-rose-400">{errors.frequency_km.message}</p>
                )}
                {Boolean(watch("current_km") && watch("frequency_km")) && (
                  <p className="text-[11px] text-emerald-400 font-mono">
                    ✓ Prossima scadenza prevista a: {(
                      (Number(watch("current_km")) || 0) + (Number(watch("frequency_km")) || 0)
                    ).toLocaleString("it-IT")} km
                  </p>
                )}
              </div>
            </div>
          )}

          {/* Notes */}
          <div className="space-y-1.5">
            <Label htmlFor="notes" className="text-xs font-semibold">
              Note Operative / Specifiche
            </Label>
            <Input
              id="notes"
              placeholder="Es. Misurare a motore freddo, bar consigliati..."
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
                  Crea Promemoria
                </>
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

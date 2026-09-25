import { useEffect, useState, useMemo } from "react"
import { useForm, type FieldErrors } from "react-hook-form"
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
  Wrench,
  Calendar,
  Gauge,
  Wallet,
  Clock,
  Loader2,
  Sparkles,
  FileText,
  SlidersHorizontal,
  X,
} from "lucide-react"
import { useCreateMaintenance, useUpdateMaintenance } from "@/hooks/useMaintenance"
import { useSettings } from "@/hooks/useSettings"
import type { MaintenanceResponse } from "@/types"
import { toast } from "sonner"

const maintenanceSchema = z.object({
  date: z.string().min(1, "La data è obbligatoria"),
  total_km: z
    .number({ invalid_type_error: "Inserisci un numero valido" })
    .int("I chilometri devono essere un intero")
    .positive("I chilometri devono essere maggiori di 0"),
  expense_type: z
    .string()
    .min(1, "La tipologia di spesa è obbligatoria")
    .max(30, "Massimo 30 caratteri"),
  cost: z
    .number({ invalid_type_error: "Inserisci un costo valido" })
    .min(0, "L'importo non può essere negativo"),
  description: z.string().optional(),
  expiry_km: z
    .number({ invalid_type_error: "Inserisci un numero valido" })
    .int("I chilometri devono essere un intero")
    .positive("La scadenza chilometrica deve essere maggiore di 0")
    .nullable()
    .optional(),
  expiry_date: z.string().nullable().optional(),
})

type MaintenanceFormData = z.infer<typeof maintenanceSchema>

const CATEGORY_PRESETS = [
  "Tagliando",
  "Freni",
  "Gomme",
  "Revisione",
  "Batteria",
  "Olio & Filtri",
  "Distribuzione",
  "Altro",
]

interface MaintenanceFormModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  initialData?: MaintenanceResponse | null
}

export function MaintenanceFormModal({
  open,
  onOpenChange,
  initialData,
}: MaintenanceFormModalProps) {
  const isEditing = !!initialData
  const createMutation = useCreateMaintenance()
  const updateMutation = useUpdateMaintenance()
  const { data: settings } = useSettings()

  const availableCategories = useMemo(() => {
    const list =
      settings?.maintenance_types && settings.maintenance_types.length > 0
        ? [...settings.maintenance_types]
        : [...CATEGORY_PRESETS]
    if (!list.includes("Altro")) {
      list.push("Altro")
    }
    return list
  }, [settings])

  const [selectedPreset, setSelectedPreset] = useState<string>("Tagliando")
  const [customExpenseType, setCustomExpenseType] = useState<string>("")
  const [showDeadlines, setShowDeadlines] = useState(false)
  const todayStr = new Date().toISOString().split("T")[0]

  const {
    register,
    handleSubmit,
    setValue,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<MaintenanceFormData>({
    resolver: zodResolver(maintenanceSchema),
    defaultValues: {
      date: todayStr,
      total_km: undefined,
      expense_type: "Tagliando",
      cost: undefined,
      description: "",
      expiry_km: null,
      expiry_date: null,
    },
  })

  useEffect(() => {
    if (open) {
      if (initialData) {
        const isPreset = availableCategories
          .filter((c) => c !== "Altro")
          .includes(initialData.expense_type)
        if (isPreset) {
          setSelectedPreset(initialData.expense_type)
          setCustomExpenseType("")
        } else {
          setSelectedPreset("Altro")
          setCustomExpenseType(
            initialData.expense_type === "Altro" ? "" : initialData.expense_type
          )
        }
        reset({
          date: initialData.date,
          total_km: initialData.total_km,
          expense_type: initialData.expense_type,
          cost: initialData.cost,
          description: initialData.description || "",
          expiry_km: initialData.expiry_km || null,
          expiry_date: initialData.expiry_date || null,
        })
        setShowDeadlines(!!(initialData.expiry_km || initialData.expiry_date))
      } else {
        setSelectedPreset("Tagliando")
        setCustomExpenseType("")
        reset({
          date: todayStr,
          total_km: undefined,
          expense_type: "Tagliando",
          cost: undefined,
          description: "",
          expiry_km: null,
          expiry_date: null,
        })
        setShowDeadlines(false)
      }
    }
  }, [open, initialData, reset, todayStr, availableCategories])

  const handleSelectPreset = (cat: string) => {
    setSelectedPreset(cat)
    if (cat === "Altro") {
      const customVal = customExpenseType.trim() || "Altro"
      setValue("expense_type", customVal, { shouldValidate: true })
    } else {
      setValue("expense_type", cat, { shouldValidate: true })
    }
  }

  const handleCustomTypeChange = (val: string) => {
    const limited = val.slice(0, 20)
    setCustomExpenseType(limited)
    const effective = limited.trim() || "Altro"
    setValue("expense_type", effective, { shouldValidate: true })
  }

  const handleToggleDeadlines = () => {
    if (showDeadlines) {
      setValue("expiry_km", null, { shouldValidate: true })
      setValue("expiry_date", null, { shouldValidate: true })
      setShowDeadlines(false)
    } else {
      setShowDeadlines(true)
    }
  }

  const onInvalid = (fieldErrors: FieldErrors<MaintenanceFormData>) => {
    const firstKey = Object.keys(fieldErrors)[0]
    const firstErr = fieldErrors[firstKey as keyof MaintenanceFormData]
    if (firstErr && firstErr.message) {
      toast.error(String(firstErr.message))
    } else {
      toast.error("Controlla i campi inseriti nel form.")
    }
  }

  const onSubmit = async (data: MaintenanceFormData) => {
    try {
      const finalExpenseType =
        selectedPreset === "Altro"
          ? (customExpenseType.trim() || "Altro")
          : data.expense_type

      const payload = {
        date: data.date,
        total_km: data.total_km,
        expense_type: finalExpenseType,
        cost: data.cost,
        description: data.description || null,
        expiry_km: showDeadlines ? (data.expiry_km ?? null) : null,
        expiry_date: showDeadlines ? (data.expiry_date || null) : null,
      }

      if (isEditing && initialData) {
        await updateMutation.mutateAsync({
          id: initialData.id,
          data: payload,
        })
        toast.success("Intervento di manutenzione aggiornato!")
      } else {
        await createMutation.mutateAsync(payload)
        toast.success("Intervento registrato con successo!")
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
            <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400">
              <Wrench className="h-5 w-5" />
            </div>
            {isEditing ? "Modifica Intervento" : "Nuova Manutenzione"}
          </DialogTitle>
          <DialogDescription>
            {isEditing
              ? "Modifica i dettagli dell'intervento e i promemoria di scadenza."
              : "Registra tagliandi, riparazioni o ricambi effettuati in officina o in autonomia."}
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit, onInvalid)} className="space-y-4 py-2">
          {/* Preset Categories */}
          <div className="space-y-2">
            <Label className="text-xs font-semibold text-muted-foreground">
              Categoria Intervento
            </Label>
            <div className="flex flex-wrap gap-1.5">
              {availableCategories.map((cat) => (
                <Badge
                  key={cat}
                  variant="outline"
                  onClick={() => handleSelectPreset(cat)}
                  className={`cursor-pointer transition-all text-xs py-1 px-2.5 ${
                    selectedPreset === cat
                      ? "bg-amber-500/20 text-amber-300 border-amber-500/40 shadow-xs"
                      : "hover:bg-muted/40 text-muted-foreground"
                  }`}
                >
                  {cat}
                </Badge>
              ))}
            </div>

            {selectedPreset === "Altro" && (
              <div className="pt-1.5 space-y-1 animate-in fade-in-50 duration-200">
                <div className="flex items-center justify-between">
                  <Label
                    htmlFor="custom_expense_type"
                    className="text-[11px] font-semibold text-muted-foreground"
                  >
                    Specifica tipologia intervento
                  </Label>
                  <span className="text-[10px] text-muted-foreground font-mono">
                    {customExpenseType.length}/20 max
                  </span>
                </div>
                <Input
                  id="custom_expense_type"
                  value={customExpenseType}
                  maxLength={20}
                  placeholder="Es. Tergicristalli, Candelette..."
                  onChange={(e) => handleCustomTypeChange(e.target.value)}
                  className="h-8 text-xs bg-muted/30 focus-visible:ring-amber-500"
                />
              </div>
            )}

            {errors.expense_type && (
              <p className="text-xs text-rose-400">{errors.expense_type.message}</p>
            )}
          </div>

          {/* Row 1: Data e Chilometri */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="date" className="flex items-center gap-1.5 text-xs font-semibold h-5">
                <Calendar className="h-3.5 w-3.5 text-muted-foreground" />
                Data Esecuzione
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
              <Label htmlFor="total_km" className="flex items-center gap-1.5 text-xs font-semibold h-5">
                <Gauge className="h-3.5 w-3.5 text-muted-foreground" />
                Chilometri Attuali
              </Label>
              <div className="relative">
                <Input
                  id="total_km"
                  type="number"
                  placeholder="Es. 120200"
                  {...register("total_km", { valueAsNumber: true })}
                  className="pr-12 font-mono text-sm"
                />
                <span className="absolute right-3 top-2.5 text-xs text-muted-foreground">
                  km
                </span>
              </div>
              {errors.total_km && (
                <p className="text-xs text-rose-400">{errors.total_km.message}</p>
              )}
            </div>
          </div>

          {/* Row 2: Importo e Descrizione */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="space-y-1.5 sm:col-span-1">
              <Label htmlFor="cost" className="flex items-center gap-1.5 text-xs font-semibold h-5">
                <Wallet className="h-3.5 w-3.5 text-muted-foreground" />
                Importo Speso
              </Label>
              <div className="relative">
                <Input
                  id="cost"
                  type="number"
                  step="0.01"
                  placeholder="140.00"
                  {...register("cost", { valueAsNumber: true })}
                  className="pr-7 font-mono text-sm font-semibold"
                />
                <span className="absolute right-3 top-2.5 text-xs text-muted-foreground">
                  €
                </span>
              </div>
              {errors.cost && (
                <p className="text-xs text-rose-400">{errors.cost.message}</p>
              )}
            </div>

            <div className="space-y-1.5 sm:col-span-2">
              <Label htmlFor="description" className="flex items-center gap-1.5 text-xs font-semibold h-5">
                <FileText className="h-3.5 w-3.5 text-muted-foreground" />
                Dettaglio Lavorazioni & Ricambi
              </Label>
              <Input
                id="description"
                placeholder="Es. Sostituzione pastiglie anteriori Brembo, olio Motul..."
                {...register("description")}
                className="text-sm"
              />
            </div>
          </div>

          {/* Collapsible: Prossima Scadenza */}
          <div className="rounded-xl border border-border/60 bg-muted/20 p-3.5 space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4 text-amber-400" />
                <span className="text-xs font-semibold text-foreground">
                  Pianifica Prossima Scadenza (Predittiva)
                </span>
              </div>
              <Button
                type="button"
                variant="outline"
                size="sm"
                className={`h-7 px-2.5 text-xs font-semibold transition-all shadow-xs flex items-center gap-1.5 ${
                  showDeadlines
                    ? "border-rose-500/40 bg-rose-500/10 text-rose-300 hover:bg-rose-500/20 hover:border-rose-500/60"
                    : "border-amber-500/50 bg-amber-500/15 text-amber-300 hover:bg-amber-500/25 hover:border-amber-500/70"
                }`}
                onClick={handleToggleDeadlines}
              >
                {showDeadlines ? (
                  <>
                    <X className="h-3.5 w-3.5" />
                    <span>Disattiva</span>
                  </>
                ) : (
                  <>
                    <SlidersHorizontal className="h-3.5 w-3.5" />
                    <span>Configura</span>
                  </>
                )}
              </Button>
            </div>

            {showDeadlines && (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 border-t border-border/40 animate-in fade-in-50">
                <div className="space-y-1">
                  <Label htmlFor="expiry_km" className="text-[11px] font-semibold text-muted-foreground">
                    Scadenza a Chilometri Target
                  </Label>
                  <div className="relative">
                    <Input
                      id="expiry_km"
                      type="number"
                      placeholder="Es. 135000"
                      {...register("expiry_km", {
                        setValueAs: (v) => {
                          if (v === "" || v === null || v === undefined) return null
                          const parsed = parseInt(String(v), 10)
                          return Number.isNaN(parsed) ? null : parsed
                        },
                      })}
                      className="pr-12 text-xs font-mono"
                    />
                    <span className="absolute right-3 top-2 text-xs text-muted-foreground">
                      km
                    </span>
                  </div>
                  {errors.expiry_km && (
                    <p className="text-xs text-rose-400">{errors.expiry_km.message}</p>
                  )}
                </div>

                <div className="space-y-1">
                  <Label htmlFor="expiry_date" className="text-[11px] font-semibold text-muted-foreground">
                    Scadenza a Data Limite
                  </Label>
                  <Input
                    id="expiry_date"
                    type="date"
                    {...register("expiry_date", {
                      setValueAs: (v) => {
                        if (!v || typeof v !== "string" || v.trim() === "") return null
                        return v.trim()
                      },
                    })}
                    className="text-xs font-mono bg-muted/40"
                  />
                  {errors.expiry_date && (
                    <p className="text-xs text-rose-400">{errors.expiry_date.message}</p>
                  )}
                </div>
              </div>
            )}
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
                  Salva Intervento
                </>
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

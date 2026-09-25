import { useEffect, useRef } from "react"
import { useForm, Controller } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { Car, Save, Loader2, RotateCcw, ShieldCheck, Fuel, Hash } from "lucide-react"
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import type { AppSettingsResponse } from "@/types/settings"
import { useUpdateSettings } from "@/hooks/useSettings"
import { showDemoReadOnlyNotice } from "@/lib/demo"
import { POPULAR_FUEL_TYPES } from "@/data/vehicles"
import { VehicleSelector } from "./VehicleSelector"
import { toast } from "sonner"

const vehicleSchema = z.object({
  vehicle_name: z
    .string()
    .min(2, "Il nome o modello del veicolo deve avere almeno 2 caratteri")
    .max(100, "Massimo 100 caratteri"),
  vehicle_plate: z
    .string()
    .max(20, "Massimo 20 caratteri")
    .optional()
    .or(z.literal("")),
  vehicle_fuel_type: z
    .string()
    .min(2, "Specificare il carburante o alimentazione")
    .max(50, "Massimo 50 caratteri"),
})

type VehicleFormData = z.infer<typeof vehicleSchema>

interface VehicleSettingsCardProps {
  settings: AppSettingsResponse
}

export function VehicleSettingsCard({ settings }: VehicleSettingsCardProps) {
  const updateMutation = useUpdateSettings()
  const fuelInputRef = useRef<HTMLInputElement | null>(null)

  const {
    control,
    register,
    handleSubmit,
    reset,
    watch,
    setValue,
    formState: { errors, isDirty, isSubmitting },
  } = useForm<VehicleFormData>({
    resolver: zodResolver(vehicleSchema),
    defaultValues: {
      vehicle_name: settings.vehicle_name || "Il mio Veicolo",
      vehicle_plate: settings.vehicle_plate || "",
      vehicle_fuel_type: settings.vehicle_fuel_type || "Benzina",
    },
  })

  const currentFuelType = watch("vehicle_fuel_type")
  const isCustomFuel = !POPULAR_FUEL_TYPES.slice(0, -1).some(
    (f) => f.toLowerCase() === currentFuelType?.trim().toLowerCase()
  )
  const { ref: fuelRegisterRef, ...fuelRegisterRest } = register("vehicle_fuel_type")

  useEffect(() => {
    reset({
      vehicle_name: settings.vehicle_name || "Il mio Veicolo",
      vehicle_plate: settings.vehicle_plate || "",
      vehicle_fuel_type: settings.vehicle_fuel_type || "Benzina",
    })
  }, [settings, reset])

  const onSubmit = async (data: VehicleFormData) => {
    if (showDemoReadOnlyNotice("L'aggiornamento dei dati del veicolo")) return

    try {
      const updated = await updateMutation.mutateAsync({
        vehicle_name: data.vehicle_name.trim(),
        vehicle_plate: (data.vehicle_plate || "").trim().toUpperCase(),
        vehicle_fuel_type: data.vehicle_fuel_type.trim(),
      })
      reset({
        vehicle_name: updated.vehicle_name || data.vehicle_name.trim(),
        vehicle_plate: updated.vehicle_plate || (data.vehicle_plate || "").trim().toUpperCase(),
        vehicle_fuel_type: updated.vehicle_fuel_type || data.vehicle_fuel_type.trim(),
      })
      toast.success("Dati del veicolo salvati con successo!")
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Errore durante il salvataggio"
      toast.error(msg)
    }
  }

  return (
    <Card className="border-border/60 bg-card/60 backdrop-blur-sm shadow-md">
      <CardHeader>
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
            <Car className="h-5 w-5" />
          </div>
          <div>
            <CardTitle className="text-base font-bold">
              Anagrafica del Veicolo
            </CardTitle>
            <CardDescription className="text-xs text-muted-foreground mt-0.5">
              Personalizza il modello, la targa e l&apos;alimentazione del veicolo monitorato in FuelPyTracker.
            </CardDescription>
          </div>
        </div>
      </CardHeader>

      <form onSubmit={handleSubmit(onSubmit)}>
        <CardContent className="space-y-4">
          {/* Selettore Intelligente Modello (Smart Combobox Ibrido) */}
          <Controller
            name="vehicle_name"
            control={control}
            render={({ field }) => (
              <VehicleSelector
                value={field.value}
                onChange={field.onChange}
                error={errors.vehicle_name?.message}
              />
            )}
          />

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-1">
            {/* Targa */}
            <div className="space-y-1.5">
              <Label htmlFor="vehicle_plate" className="text-xs font-semibold flex items-center gap-1.5">
                <Hash className="h-3.5 w-3.5 text-emerald-400" />
                <span>Targa Veicolo (Opzionale)</span>
              </Label>
              <Input
                id="vehicle_plate"
                placeholder="Es. AB 123 CD"
                {...register("vehicle_plate")}
                className="text-xs uppercase font-mono tracking-wider"
              />
              {errors.vehicle_plate && (
                <p className="text-[11px] text-destructive">{errors.vehicle_plate.message}</p>
              )}
            </div>

            {/* Alimentazione */}
            <div className="space-y-1.5">
              <Label htmlFor="vehicle_fuel_type" className="text-xs font-semibold flex items-center gap-1.5">
                <Fuel className="h-3.5 w-3.5 text-emerald-400" />
                <span>Carburante / Alimentazione</span>
                <span className="text-destructive">*</span>
              </Label>

              {/* Quick Fuel Selection Chips */}
              <div className="flex flex-wrap gap-1 pb-1">
                {POPULAR_FUEL_TYPES.map((fuel) => {
                  const isSelected =
                    fuel === "Altro"
                      ? isCustomFuel
                      : currentFuelType?.toLowerCase() === fuel.toLowerCase()
                  return (
                    <button
                      key={fuel}
                      type="button"
                      onClick={() => {
                        if (fuel === "Altro") {
                          const isStandard = POPULAR_FUEL_TYPES.slice(0, -1).some(
                            (f) => f.toLowerCase() === currentFuelType?.trim().toLowerCase()
                          )
                          if (isStandard) {
                            setValue("vehicle_fuel_type", "", {
                              shouldDirty: true,
                              shouldValidate: false,
                            })
                          }
                          setTimeout(() => fuelInputRef.current?.focus(), 50)
                        } else {
                          setValue("vehicle_fuel_type", fuel, {
                            shouldDirty: true,
                            shouldValidate: true,
                          })
                        }
                      }}
                      className={`text-[10px] px-2 py-0.5 rounded-md border transition-all ${
                        isSelected
                          ? "bg-emerald-500/20 text-emerald-300 border-emerald-500/40 font-semibold"
                          : "bg-muted/30 text-muted-foreground border-border/40 hover:bg-muted hover:text-foreground"
                      }`}
                    >
                      {fuel}
                    </button>
                  )
                })}
              </div>

              <Input
                id="vehicle_fuel_type"
                placeholder={
                  isCustomFuel
                    ? "Digita l'alimentazione (es. Idrogeno, Miscela 2T)..."
                    : "Es. Diesel, Benzina, Ibrida, GPL, Elettrica..."
                }
                {...fuelRegisterRest}
                ref={(e) => {
                  fuelRegisterRef(e)
                  fuelInputRef.current = e
                }}
                className="text-xs"
              />
              {isCustomFuel && (
                <p className="text-[10px] text-muted-foreground">
                  Hai selezionato &quot;Altro&quot;: specifica l&apos;alimentazione nel campo di testo.
                </p>
              )}
              {errors.vehicle_fuel_type && (
                <p className="text-[11px] text-destructive">{errors.vehicle_fuel_type.message}</p>
              )}
            </div>
          </div>

          <div className="p-3 rounded-xl bg-muted/20 border border-border/40 text-xs text-muted-foreground flex items-center gap-2.5">
            <ShieldCheck className="h-4 w-4 text-emerald-400 shrink-0" />
            <span>
              I dati inseriti compariranno istantaneamente nella barra laterale, nei libretti PDF generati e nell&apos;intestazione di tutte le schermate.
            </span>
          </div>
        </CardContent>

        <CardFooter className="border-t border-border/60 pt-4 flex items-center justify-between">
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={() => reset()}
            disabled={!isDirty || isSubmitting || updateMutation.isPending}
            className="gap-1.5 text-xs text-muted-foreground"
          >
            <RotateCcw className="h-3.5 w-3.5" />
            <span>Ripristina</span>
          </Button>

          <Button
            type="submit"
            variant="emerald"
            size="sm"
            disabled={!isDirty || isSubmitting || updateMutation.isPending}
            className="gap-1.5 text-xs font-semibold shadow-sm shadow-emerald-500/20"
          >
            {isSubmitting || updateMutation.isPending ? (
              <>
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
                <span>Salvataggio...</span>
              </>
            ) : (
              <>
                <Save className="h-3.5 w-3.5" />
                <span>Salva Dati Veicolo</span>
              </>
            )}
          </Button>
        </CardFooter>
      </form>
    </Card>
  )
}

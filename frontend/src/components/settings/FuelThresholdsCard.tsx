import { useEffect } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { Shield, Save, AlertTriangle, Gauge, Fuel, Loader2, RotateCcw } from "lucide-react"
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import type { AppSettingsResponse } from "@/types/settings"
import { useUpdateSettings } from "@/hooks/useSettings"

const thresholdsSchema = z.object({
  price_fluctuation_cents: z
    .number({ invalid_type_error: "Inserisci un numero valido" })
    .positive("La tolleranza deve essere maggiore di zero")
    .max(1.0, "La tolleranza massima è 1.00 €/L"),
  max_total_cost: z
    .number({ invalid_type_error: "Inserisci un numero valido" })
    .positive("Il tetto deve essere positivo")
    .max(1000, "Valore massimo consentito 1000 €"),
  max_accumulated_partial_cost: z
    .number({ invalid_type_error: "Inserisci un numero valido" })
    .positive("La soglia deve essere positiva")
    .max(1000, "Valore massimo consentito 1000 €"),
  import_kml_min: z
    .number({ invalid_type_error: "Inserisci un numero valido" })
    .positive("Il consumo minimo deve essere positivo"),
  import_kml_max: z
    .number({ invalid_type_error: "Inserisci un numero valido" })
    .positive("Il consumo massimo deve essere positivo"),
  import_kml_error: z
    .number({ invalid_type_error: "Inserisci un numero valido" })
    .positive("La soglia d'errore deve essere positiva"),
  import_kmd_max: z
    .number({ invalid_type_error: "Inserisci un numero valido" })
    .positive("La percorrenza deve essere positiva"),
})

type ThresholdsFormData = z.infer<typeof thresholdsSchema>

interface FuelThresholdsCardProps {
  settings: AppSettingsResponse
}

export function FuelThresholdsCard({ settings }: FuelThresholdsCardProps) {
  const updateMutation = useUpdateSettings()

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isDirty },
  } = useForm<ThresholdsFormData>({
    resolver: zodResolver(thresholdsSchema),
    defaultValues: {
      price_fluctuation_cents: settings.price_fluctuation_cents,
      max_total_cost: settings.max_total_cost,
      max_accumulated_partial_cost: settings.max_accumulated_partial_cost,
      import_kml_min: settings.import_kml_min,
      import_kml_max: settings.import_kml_max,
      import_kml_error: settings.import_kml_error,
      import_kmd_max: settings.import_kmd_max,
    },
  })

  // Sincronizza i valori se settings cambia dal backend
  useEffect(() => {
    reset({
      price_fluctuation_cents: settings.price_fluctuation_cents,
      max_total_cost: settings.max_total_cost,
      max_accumulated_partial_cost: settings.max_accumulated_partial_cost,
      import_kml_min: settings.import_kml_min,
      import_kml_max: settings.import_kml_max,
      import_kml_error: settings.import_kml_error,
      import_kmd_max: settings.import_kmd_max,
    })
  }, [settings, reset])

  const onSubmit = (data: ThresholdsFormData) => {
    updateMutation.mutate(data)
  }

  const handleReset = () => {
    reset({
      price_fluctuation_cents: settings.price_fluctuation_cents,
      max_total_cost: settings.max_total_cost,
      max_accumulated_partial_cost: settings.max_accumulated_partial_cost,
      import_kml_min: settings.import_kml_min,
      import_kml_max: settings.import_kml_max,
      import_kml_error: settings.import_kml_error,
      import_kmd_max: settings.import_kmd_max,
    })
  }

  return (
    <Card className="border-border/60 bg-card/60 backdrop-blur-sm shadow-md">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
              <Shield className="h-5 w-5" />
            </div>
            <div>
              <CardTitle className="text-base font-bold">
                Soglie di Sicurezza & Limiti Operativi
              </CardTitle>
              <CardDescription className="text-xs text-muted-foreground mt-0.5">
                Regola i parametri di allerta per i rifornimenti e i sanity check del motore di importazione.
              </CardDescription>
            </div>
          </div>
        </div>
      </CardHeader>

      <form onSubmit={handleSubmit(onSubmit)}>
        <CardContent className="space-y-6">
          {/* Sezione 1: Spesa Carburante & Tolleranze */}
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground border-b border-border/40 pb-2">
              <Fuel className="h-4 w-4 text-emerald-400" />
              <span>Parametri Rifornimenti & Prezzi</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Tetto Massimo Pieno */}
              <div className="space-y-1.5">
                <Label htmlFor="max_total_cost" className="text-xs font-medium">
                  Tetto Max Singolo Pieno (€)
                </Label>
                <div className="relative">
                  <Input
                    id="max_total_cost"
                    type="number"
                    step="1"
                    {...register("max_total_cost", { valueAsNumber: true })}
                    className="pr-8"
                  />
                  <span className="absolute right-2.5 top-1/2 -translate-y-1/2 text-xs text-muted-foreground">
                    €
                  </span>
                </div>
                <p className="text-[11px] text-muted-foreground">
                  Spese superiori sollevano un warning.
                </p>
                {errors.max_total_cost && (
                  <p className="text-[11px] text-rose-400">{errors.max_total_cost.message}</p>
                )}
              </div>

              {/* Allarme Rifornimenti Parziali */}
              <div className="space-y-1.5">
                <Label htmlFor="max_accumulated_partial_cost" className="text-xs font-medium">
                  Allarme Parziali Accumulati (€)
                </Label>
                <div className="relative">
                  <Input
                    id="max_accumulated_partial_cost"
                    type="number"
                    step="1"
                    {...register("max_accumulated_partial_cost", { valueAsNumber: true })}
                    className="pr-8"
                  />
                  <span className="absolute right-2.5 top-1/2 -translate-y-1/2 text-xs text-muted-foreground">
                    €
                  </span>
                </div>
                <p className="text-[11px] text-muted-foreground">
                  Avviso quando la somma dei parziali supera questa soglia.
                </p>
                {errors.max_accumulated_partial_cost && (
                  <p className="text-[11px] text-rose-400">
                    {errors.max_accumulated_partial_cost.message}
                  </p>
                )}
              </div>

              {/* Tolleranza Oscillazione Prezzo */}
              <div className="space-y-1.5">
                <Label htmlFor="price_fluctuation_cents" className="text-xs font-medium">
                  Tolleranza Prezzo Carburante (€/L)
                </Label>
                <div className="relative">
                  <Input
                    id="price_fluctuation_cents"
                    type="number"
                    step="0.01"
                    {...register("price_fluctuation_cents", { valueAsNumber: true })}
                    className="pr-10"
                  />
                  <span className="absolute right-2.5 top-1/2 -translate-y-1/2 text-xs text-muted-foreground">
                    €/L
                  </span>
                </div>
                <p className="text-[11px] text-muted-foreground">
                  Scostamento anomalo rispetto alla media recente.
                </p>
                {errors.price_fluctuation_cents && (
                  <p className="text-[11px] text-rose-400">
                    {errors.price_fluctuation_cents.message}
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Sezione 2: Sanity Check Importazione */}
          <div className="space-y-4 pt-2">
            <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground border-b border-border/40 pb-2">
              <Gauge className="h-4 w-4 text-emerald-400" />
              <span>Soglie Motore Importazione Dati (Sanity Checks)</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Consumo Minimo */}
              <div className="space-y-1.5">
                <Label htmlFor="import_kml_min" className="text-xs font-medium">
                  Consumo Minimo Plausibile
                </Label>
                <div className="relative">
                  <Input
                    id="import_kml_min"
                    type="number"
                    step="0.5"
                    {...register("import_kml_min", { valueAsNumber: true })}
                    className="pr-12"
                  />
                  <span className="absolute right-2.5 top-1/2 -translate-y-1/2 text-[11px] text-muted-foreground">
                    km/L
                  </span>
                </div>
                <p className="text-[11px] text-muted-foreground">Warning sotto questo valore.</p>
                {errors.import_kml_min && (
                  <p className="text-[11px] text-rose-400">{errors.import_kml_min.message}</p>
                )}
              </div>

              {/* Consumo Massimo */}
              <div className="space-y-1.5">
                <Label htmlFor="import_kml_max" className="text-xs font-medium">
                  Consumo Massimo Plausibile
                </Label>
                <div className="relative">
                  <Input
                    id="import_kml_max"
                    type="number"
                    step="0.5"
                    {...register("import_kml_max", { valueAsNumber: true })}
                    className="pr-12"
                  />
                  <span className="absolute right-2.5 top-1/2 -translate-y-1/2 text-[11px] text-muted-foreground">
                    km/L
                  </span>
                </div>
                <p className="text-[11px] text-muted-foreground">Warning sopra questo valore.</p>
                {errors.import_kml_max && (
                  <p className="text-[11px] text-rose-400">{errors.import_kml_max.message}</p>
                )}
              </div>

              {/* Consumo Errore Bloccante */}
              <div className="space-y-1.5">
                <Label htmlFor="import_kml_error" className="text-xs font-medium text-rose-300">
                  Consumo Errore Bloccante
                </Label>
                <div className="relative">
                  <Input
                    id="import_kml_error"
                    type="number"
                    step="1"
                    {...register("import_kml_error", { valueAsNumber: true })}
                    className="pr-12 border-rose-500/30 focus:border-rose-500"
                  />
                  <span className="absolute right-2.5 top-1/2 -translate-y-1/2 text-[11px] text-muted-foreground">
                    km/L
                  </span>
                </div>
                <p className="text-[11px] text-muted-foreground">
                  Valore impossibile (blocca import).
                </p>
                {errors.import_kml_error && (
                  <p className="text-[11px] text-rose-400">{errors.import_kml_error.message}</p>
                )}
              </div>

              {/* Distanza Massima Giorno */}
              <div className="space-y-1.5">
                <Label htmlFor="import_kmd_max" className="text-xs font-medium text-amber-300">
                  Distanza Max Giornaliera
                </Label>
                <div className="relative">
                  <Input
                    id="import_kmd_max"
                    type="number"
                    step="50"
                    {...register("import_kmd_max", { valueAsNumber: true })}
                    className="pr-14 border-amber-500/30"
                  />
                  <span className="absolute right-2.5 top-1/2 -translate-y-1/2 text-[11px] text-muted-foreground">
                    km/gg
                  </span>
                </div>
                <p className="text-[11px] text-muted-foreground">
                  Limite massimo plausibile in un giorno.
                </p>
                {errors.import_kmd_max && (
                  <p className="text-[11px] text-rose-400">{errors.import_kmd_max.message}</p>
                )}
              </div>
            </div>
          </div>

          <div className="p-3 rounded-lg bg-muted/20 border border-border/50 flex items-start gap-2.5 text-xs text-muted-foreground">
            <AlertTriangle className="h-4 w-4 text-amber-400 shrink-0 mt-0.5" />
            <span>
              Questi parametri vengono applicati in tempo reale sia nella modale di validazione preventiva dei rifornimenti, sia nello staging pre-commit durante l&apos;importazione dei file Excel/CSV.
            </span>
          </div>
        </CardContent>

        <CardFooter className="border-t border-border/60 pt-4 flex items-center justify-between">
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={handleReset}
            disabled={!isDirty || updateMutation.isPending}
            className="gap-1.5 text-xs text-muted-foreground hover:text-foreground"
          >
            <RotateCcw className="h-3.5 w-3.5" />
            Ripristina
          </Button>

          <Button
            type="submit"
            variant="emerald"
            size="sm"
            disabled={!isDirty || updateMutation.isPending}
            className="gap-2 font-semibold shadow-sm"
          >
            {updateMutation.isPending ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>Salvataggio...</span>
              </>
            ) : (
              <>
                <Save className="h-4 w-4" />
                <span>Salva Soglie Operative</span>
              </>
            )}
          </Button>
        </CardFooter>
      </form>
    </Card>
  )
}

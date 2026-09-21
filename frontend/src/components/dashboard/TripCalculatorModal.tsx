import React, { useState } from "react"
import { Calculator, Navigation, Sparkles, Fuel, Euro } from "lucide-react"
import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { dashboardApi } from "@/services/api/dashboardApi"
import type { TripCalculationResponse } from "@/types"

interface TripCalculatorModalProps {
  defaultAvgKml?: number
}

export function TripCalculatorModal({ defaultAvgKml = 18.45 }: TripCalculatorModalProps) {
  const [open, setOpen] = useState(false)
  const [distanceKm, setDistanceKm] = useState<number>(350)
  const [fuelPrice, setFuelPrice] = useState<number>(1.82)
  const [result, setResult] = useState<TripCalculationResponse | null>(null)
  const [loading, setLoading] = useState(false)

  const handleCalculate = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const res = await dashboardApi.calculateTrip({
        distance_km: distanceKm,
        expected_fuel_price: fuelPrice,
      })
      setResult(res)
    } catch {
      // Fallback calculation using local stats if offline or unauthenticated
      const kml = defaultAvgKml > 0 ? defaultAvgKml : 18.45
      const liters = distanceKm / kml
      const cost = liters * fuelPrice
      setResult({
        distance_km: distanceKm,
        estimated_liters: Number(liters.toFixed(2)),
        estimated_cost: Number(cost.toFixed(2)),
        avg_km_per_liter_used: Number(kml.toFixed(2)),
        fuel_price_used: fuelPrice,
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button variant="emerald" size="sm" className="gap-1.5 shadow-sm shadow-emerald-500/20">
          <Calculator className="h-4 w-4" />
          <span>Calcola Viaggio</span>
        </Button>
      </DialogTrigger>

      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <div className="flex items-center gap-2 text-emerald-400">
            <Navigation className="h-5 w-5" />
            <DialogTitle>Simulatore Costi Viaggio</DialogTitle>
          </div>
          <DialogDescription>
            Stima il fabbisogno di carburante e la spesa complessiva basandoti sul consumo reale del veicolo.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleCalculate} className="space-y-4 py-2">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-muted-foreground flex items-center gap-1.5">
                <Navigation className="h-3.5 w-3.5 text-emerald-400" />
                Distanza (km)
              </label>
              <Input
                type="number"
                min={1}
                step={1}
                value={distanceKm}
                onChange={(e) => setDistanceKm(Number(e.target.value))}
                required
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-muted-foreground flex items-center gap-1.5">
                <Euro className="h-3.5 w-3.5 text-emerald-400" />
                Prezzo Stimato (€/L)
              </label>
              <Input
                type="number"
                min={0.5}
                step={0.01}
                value={fuelPrice}
                onChange={(e) => setFuelPrice(Number(e.target.value))}
                required
              />
            </div>
          </div>

          <Button type="submit" variant="emerald" className="w-full gap-2" disabled={loading}>
            <Sparkles className="h-4 w-4" />
            <span>{loading ? "Calcolo in corso..." : "Calcola Preventivo Spesa"}</span>
          </Button>

          {/* Results Box */}
          {result && (
            <div className="rounded-xl border border-emerald-500/40 bg-emerald-950/20 p-4 space-y-3 animate-in fade-in-50 duration-200">
              <div className="text-xs font-semibold text-emerald-300 uppercase tracking-wider">
                Risultato Stima Viaggio
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="p-2.5 rounded-lg bg-card/80 border border-border/60">
                  <div className="text-[11px] text-muted-foreground flex items-center gap-1">
                    <Fuel className="h-3 w-3 text-emerald-400" />
                    Litri Necessari
                  </div>
                  <div className="text-xl font-bold text-foreground mt-0.5">
                    {result.estimated_liters} L
                  </div>
                </div>

                <div className="p-2.5 rounded-lg bg-card/80 border border-border/60">
                  <div className="text-[11px] text-muted-foreground flex items-center gap-1">
                    <Euro className="h-3 w-3 text-emerald-400" />
                    Spesa Prevista
                  </div>
                  <div className="text-xl font-bold text-emerald-400 mt-0.5">
                    € {result.estimated_cost.toFixed(2).replace(".", ",")}
                  </div>
                </div>
              </div>

              <p className="text-[11px] text-muted-foreground">
                Calcolato con efficienza media di <strong>{result.avg_km_per_liter_used} km/L</strong> e prezzo carburante di <strong>€{result.fuel_price_used.toFixed(2)}/L</strong>.
              </p>
            </div>
          )}
        </form>

        <DialogFooter className="sm:justify-end pt-2">
          <Button variant="outline" size="sm" onClick={() => setOpen(false)}>
            Chiudi
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

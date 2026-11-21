import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"
import { Fuel, ChevronRight, MapPin, Gauge } from "lucide-react"
import type { RefuelingResponse } from "@/types"

interface FuelCardListProps {
  refuelings: RefuelingResponse[]
  onSelect: (refueling: RefuelingResponse) => void
}

export function FuelCardList({ refuelings, onSelect }: FuelCardListProps) {
  if (refuelings.length === 0) {
    return (
      <div className="p-12 text-center text-muted-foreground space-y-3">
        <div className="mx-auto w-12 h-12 rounded-full bg-muted/40 flex items-center justify-center text-muted-foreground">
          <Fuel className="h-6 w-6" />
        </div>
        <p className="text-sm font-medium">Nessun rifornimento trovato per i filtri selezionati.</p>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
      {refuelings.map((r) => (
        <Card
          key={r.id}
          onClick={() => onSelect(r)}
          className="cursor-pointer hover:border-emerald-500/50 hover:bg-muted/10 transition-all active:scale-[0.99] group border-border/60"
        >
          <CardContent className="p-4 space-y-3">
            {/* Top row: Data, Badge Pieno/Parziale */}
            <div className="flex items-center justify-between">
              <span className="font-mono text-xs font-semibold text-foreground">
                {r.date}
              </span>
              <Badge
                variant="outline"
                className={`text-[10px] ${
                  r.is_full_tank
                    ? "border-emerald-500/30 text-emerald-400 bg-emerald-500/10"
                    : "border-amber-500/30 text-amber-400 bg-amber-500/10"
                }`}
              >
                {r.is_full_tank ? "Pieno Completo" : "Parziale"}
              </Badge>
            </div>

            {/* Middle row: Spesa e Rendimento */}
            <div className="flex items-baseline justify-between pt-1">
              <div>
                <span className="text-2xl font-extrabold font-mono text-foreground">
                  {r.total_cost.toFixed(2)} €
                </span>
                <span className="text-xs text-muted-foreground ml-1.5 font-mono">
                  ({r.liters.toFixed(1)} L)
                </span>
              </div>

              {r.km_per_liter !== null ? (
                <div className="text-right">
                  <span className="font-mono text-sm font-bold text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-lg border border-emerald-500/20">
                    {r.km_per_liter.toFixed(2)} km/L
                  </span>
                </div>
              ) : (
                <span className="text-xs text-muted-foreground italic">
                  Parziale
                </span>
              )}
            </div>

            {/* Bottom info: Chilometri, Prezzo/L, Distributore */}
            <div className="pt-2 border-t border-border/40 text-xs text-muted-foreground flex items-center justify-between">
              <div className="flex items-center gap-1 font-mono">
                <Gauge className="h-3 w-3" />
                <span>{r.total_km.toLocaleString("it-IT")} km</span>
                {r.delta_km !== null && (
                  <span className="text-emerald-400 font-medium">
                    (+{r.delta_km} km)
                  </span>
                )}
              </div>

              <div className="flex items-center gap-1 font-mono">
                <span>{r.price_per_liter.toFixed(3)} €/L</span>
                <ChevronRight className="h-3.5 w-3.5 text-muted-foreground group-hover:text-emerald-400 transition-colors" />
              </div>
            </div>

            {r.notes && (
              <div className="flex items-center gap-1.5 text-[11px] text-muted-foreground truncate pt-0.5">
                <MapPin className="h-3 w-3 shrink-0 text-emerald-400/70" />
                <span className="truncate">{r.notes}</span>
              </div>
            )}
          </CardContent>
        </Card>
      ))}
    </div>
  )
}

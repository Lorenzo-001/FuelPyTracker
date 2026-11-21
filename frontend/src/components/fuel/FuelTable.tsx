import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
} from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { ChevronRight, Fuel } from "lucide-react"
import type { RefuelingResponse } from "@/types"

interface FuelTableProps {
  refuelings: RefuelingResponse[]
  onSelect: (refueling: RefuelingResponse) => void
}

export function FuelTable({ refuelings, onSelect }: FuelTableProps) {
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
    <div className="overflow-x-auto">
      <Table>
        <TableHeader className="bg-muted/20">
          <TableRow>
            <TableHead className="w-[120px]">Data</TableHead>
            <TableHead>Contachilometri</TableHead>
            <TableHead>Tratta (Delta)</TableHead>
            <TableHead>Prezzo / L</TableHead>
            <TableHead>Litri</TableHead>
            <TableHead>Totale Spesa</TableHead>
            <TableHead>Efficienza</TableHead>
            <TableHead>Stato</TableHead>
            <TableHead className="w-[50px]"></TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {refuelings.map((r) => (
            <TableRow
              key={r.id}
              onClick={() => onSelect(r)}
              className="cursor-pointer hover:bg-muted/30 transition-colors group"
            >
              <TableCell className="font-mono text-xs font-semibold text-foreground">
                {r.date}
              </TableCell>
              <TableCell className="font-mono text-xs text-muted-foreground">
                {r.total_km.toLocaleString("it-IT")} km
              </TableCell>
              <TableCell className="font-mono text-xs font-medium">
                {r.delta_km !== null ? (
                  <span className="text-emerald-400">+{r.delta_km.toLocaleString("it-IT")} km</span>
                ) : (
                  <span className="text-muted-foreground">—</span>
                )}
              </TableCell>
              <TableCell className="font-mono text-xs">
                {r.price_per_liter.toFixed(3)} €/L
              </TableCell>
              <TableCell className="font-mono text-xs">
                {r.liters.toFixed(2)} L
              </TableCell>
              <TableCell className="font-mono text-xs font-bold text-foreground">
                {r.total_cost.toFixed(2)} €
              </TableCell>
              <TableCell>
                {r.km_per_liter !== null ? (
                  <span className="font-mono text-xs font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
                    {r.km_per_liter.toFixed(2)} km/L
                  </span>
                ) : (
                  <span className="text-xs text-muted-foreground italic">Parziale</span>
                )}
              </TableCell>
              <TableCell>
                <Badge
                  variant="outline"
                  className={`text-[10px] ${
                    r.is_full_tank
                      ? "border-emerald-500/30 text-emerald-400 bg-emerald-500/10"
                      : "border-amber-500/30 text-amber-400 bg-amber-500/10"
                  }`}
                >
                  {r.is_full_tank ? "Pieno" : "Parziale"}
                </Badge>
              </TableCell>
              <TableCell className="text-right">
                <ChevronRight className="h-4 w-4 text-muted-foreground group-hover:text-emerald-400 transition-colors inline-block" />
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}

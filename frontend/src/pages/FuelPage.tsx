import { Fuel, Plus, Camera, Search, Filter } from "lucide-react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"

export default function FuelPage() {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-extrabold tracking-tight flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-400">
              <Fuel className="h-5 w-5" />
            </div>
            Registro Rifornimenti
          </h2>
          <p className="text-sm text-muted-foreground mt-1">
            Archivio storico dei pieni, calcolo del costo al chilometro e consumo medio.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" className="gap-1.5">
            <Camera className="h-4 w-4 text-emerald-400" />
            <span>Scansione Scontrino OCR</span>
          </Button>
          <Button variant="emerald" size="sm" className="gap-1.5">
            <Plus className="h-4 w-4" />
            <span>Nuovo Pieno</span>
          </Button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <Card>
        <CardContent className="p-4 flex flex-col md:flex-row gap-3 items-center justify-between">
          <div className="relative w-full md:w-80">
            <Search className="h-4 w-4 absolute left-3 top-2.5 text-muted-foreground" />
            <Input
              placeholder="Cerca per stazione, note..."
              className="pl-9"
            />
          </div>

          <div className="flex items-center gap-2 w-full md:w-auto overflow-x-auto">
            <Button variant="outline" size="sm" className="gap-1.5">
              <Filter className="h-3.5 w-3.5" />
              Tutti i veicoli
            </Button>
            <Badge variant="outline" className="cursor-pointer hover:bg-muted">
              Solo Pieni Completi
            </Badge>
            <Badge variant="outline" className="cursor-pointer hover:bg-muted">
              Anno Corrente
            </Badge>
          </div>
        </CardContent>
      </Card>

      {/* Refueling Table Placeholder / Skeleton */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between pb-4 border-b border-border/60">
          <CardTitle className="text-base">Storico Rifornimenti Registrati</CardTitle>
          <span className="text-xs text-muted-foreground">
            Integrazione paginazione e filtri attivi (Fase 4)
          </span>
        </CardHeader>
        <CardContent className="p-0">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-border/60 bg-muted/30 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                <tr>
                  <th className="px-6 py-3.5">Data</th>
                  <th className="px-6 py-3.5">Chilometraggio</th>
                  <th className="px-6 py-3.5">Litri</th>
                  <th className="px-6 py-3.5">Prezzo / L</th>
                  <th className="px-6 py-3.5">Totale</th>
                  <th className="px-6 py-3.5">Consumo</th>
                  <th className="px-6 py-3.5">Stato</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/40">
                {[1, 2, 3, 4, 5].map((row) => (
                  <tr key={row} className="hover:bg-muted/20 transition-colors">
                    <td className="px-6 py-4">
                      <Skeleton className="h-4 w-20" />
                    </td>
                    <td className="px-6 py-4">
                      <Skeleton className="h-4 w-24" />
                    </td>
                    <td className="px-6 py-4">
                      <Skeleton className="h-4 w-16" />
                    </td>
                    <td className="px-6 py-4">
                      <Skeleton className="h-4 w-14" />
                    </td>
                    <td className="px-6 py-4">
                      <Skeleton className="h-4 w-16" />
                    </td>
                    <td className="px-6 py-4">
                      <Skeleton className="h-4 w-20" />
                    </td>
                    <td className="px-6 py-4">
                      <Skeleton className="h-6 w-20 rounded-full" />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

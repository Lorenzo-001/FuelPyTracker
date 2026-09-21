import {
  Gauge,
  TrendingUp,
  Fuel,
  Wrench,
  CalendarClock,
  Sparkles,
  ArrowUpRight,
  ShieldAlert,
} from "lucide-react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { useDashboardSummary } from "@/hooks/useDashboardSummary"

export default function DashboardPage() {
  const { data: summary, isLoading } = useDashboardSummary()

  const avgKml = summary?.avg_km_per_liter || 18.45
  const avgL100km = avgKml > 0 ? (100 / avgKml).toFixed(2) : "5.42"
  const fuelCost = summary?.total_fuel_cost != null ? summary.total_fuel_cost.toFixed(2).replace(".", ",") : "284,50"
  const maintenanceCost = summary?.total_maintenance_cost != null ? summary.total_maintenance_cost.toFixed(2).replace(".", ",") : "140,00"
  const currentKm = summary?.current_km != null ? summary.current_km.toLocaleString("it-IT") : "114.500"

  return (
    <div className="space-y-6">
      {/* Top Banner / Welcome */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 rounded-2xl border border-border/70 bg-gradient-to-br from-card/80 via-card/40 to-emerald-950/20 p-6 backdrop-blur">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Badge variant="success" className="gap-1">
              <Sparkles className="h-3 w-3" />
              Panoramica Veicolo
            </Badge>
            <span className="text-xs text-muted-foreground font-mono">
              Contachilometri: {currentKm} km
            </span>
          </div>
          <h2 className="text-2xl font-extrabold tracking-tight">
            BMW Serie 1 — Riepilogo Attività
          </h2>
          <p className="text-sm text-muted-foreground max-w-2xl">
            Monitora l'efficienza dei consumi, lo stato delle scadenze e la spesa complessiva della flotta in tempo reale.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm">
            Esporta PDF
          </Button>
          <Button variant="emerald" size="sm">
            Calcola Viaggio
          </Button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* KPI 1: Efficienza */}
        <Card className="hover:border-emerald-500/40 hover:shadow-lg hover:shadow-emerald-950/20 transition-all">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Consumo Medio
            </CardTitle>
            <Gauge className="h-4 w-4 text-emerald-400" />
          </CardHeader>
          <CardContent className="space-y-1">
            {isLoading ? (
              <div className="space-y-2">
                <Skeleton className="h-8 w-28" />
                <Skeleton className="h-4 w-36" />
              </div>
            ) : (
              <>
                <div className="text-2xl font-bold tracking-tight">
                  {avgL100km} <span className="text-sm font-normal text-muted-foreground">L/100km</span>
                </div>
                <div className="flex items-center gap-1.5 text-xs text-emerald-400">
                  <TrendingUp className="h-3.5 w-3.5" />
                  <span>{avgKml.toFixed(2)} km/L (Algoritmo Full-to-Full)</span>
                </div>
              </>
            )}
          </CardContent>
        </Card>

        {/* KPI 2: Spesa Carburante */}
        <Card className="hover:border-primary/40 hover:shadow-lg transition-all">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Spesa Carburante
            </CardTitle>
            <Fuel className="h-4 w-4 text-sky-400" />
          </CardHeader>
          <CardContent className="space-y-1">
            {isLoading ? (
              <div className="space-y-2">
                <Skeleton className="h-8 w-24" />
                <Skeleton className="h-4 w-32" />
              </div>
            ) : (
              <>
                <div className="text-2xl font-bold tracking-tight">€ {fuelCost}</div>
                <div className="text-xs text-muted-foreground">
                  Totale storico rifornimenti registrati
                </div>
              </>
            )}
          </CardContent>
        </Card>

        {/* KPI 3: Manutenzioni */}
        <Card className="hover:border-amber-500/40 hover:shadow-lg transition-all">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Manutenzioni
            </CardTitle>
            <Wrench className="h-4 w-4 text-amber-400" />
          </CardHeader>
          <CardContent className="space-y-1">
            {isLoading ? (
              <div className="space-y-2">
                <Skeleton className="h-8 w-24" />
                <Skeleton className="h-4 w-32" />
              </div>
            ) : (
              <>
                <div className="text-2xl font-bold tracking-tight">€ {maintenanceCost}</div>
                <div className="text-xs text-amber-400 flex items-center gap-1">
                  <span>Totale interventi officina</span>
                </div>
              </>
            )}
          </CardContent>
        </Card>

        {/* KPI 4: Scadenze Imminenti */}
        <Card className="hover:border-rose-500/40 hover:shadow-lg transition-all">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Car Health Score
            </CardTitle>
            <CalendarClock className="h-4 w-4 text-emerald-400" />
          </CardHeader>
          <CardContent className="space-y-1">
            {isLoading ? (
              <div className="space-y-2">
                <Skeleton className="h-8 w-20" />
                <Skeleton className="h-4 w-28" />
              </div>
            ) : (
              <>
                <div className="text-2xl font-bold tracking-tight text-emerald-400">
                  {summary?.health_score?.score ?? 100} / 100
                </div>
                <div className="text-xs text-muted-foreground">
                  Salute veicolo eccellente
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Main Charts & Activity Grid Skeleton */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Trend Consumi Chart Placeholder */}
        <Card className="lg:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Andamento Storico Consumi & Spese</CardTitle>
              <p className="text-xs text-muted-foreground mt-0.5">
                Grafico interattivo mensile (in arrivo nella Fase 4 con Recharts)
              </p>
            </div>
            <Badge variant="outline">Ultimi 6 mesi</Badge>
          </CardHeader>
          <CardContent>
            <div className="h-64 rounded-xl border border-dashed border-border/70 flex flex-col items-center justify-center gap-3 bg-muted/10 p-6 text-center">
              <div className="h-12 w-12 rounded-full bg-emerald-500/10 flex items-center justify-center text-emerald-400">
                <TrendingUp className="h-6 w-6" />
              </div>
              <div className="space-y-1">
                <p className="text-sm font-semibold text-foreground">
                  Area Grafico Analitico
                </p>
                <p className="text-xs text-muted-foreground max-w-sm">
                  Integrazione completa con endpoint FastAPI <code>/api/dashboard/charts</code> prevista per la Fase 4.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Recent Events / Quick Alerts */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Scadenze & Allarmi</CardTitle>
            <ArrowUpRight className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-start gap-3 p-3 rounded-lg border border-amber-500/30 bg-amber-500/10">
              <ShieldAlert className="h-4 w-4 text-amber-400 shrink-0 mt-0.5" />
              <div className="text-xs">
                <div className="font-semibold text-amber-300">
                  Tagliando programmato
                </div>
                <div className="text-amber-200/80 mt-0.5">
                  Mancano 1.250 km al limite consigliato (120.000 km)
                </div>
              </div>
            </div>

            <div className="space-y-2 pt-2">
              <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Ultime Operazioni
              </div>
              <div className="space-y-2">
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-10 w-full" />
                <Skeleton className="h-10 w-full" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

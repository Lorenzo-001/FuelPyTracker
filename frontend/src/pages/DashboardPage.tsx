import { useNavigate } from "react-router-dom"
import {
  Gauge,
  TrendingUp,
  Fuel,
  Wrench,
  Sparkles,
  Wallet,
  AlertTriangle,
  FileText,
} from "lucide-react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { useDashboardSummary } from "@/hooks/useDashboardSummary"
import { DashboardCharts } from "@/components/dashboard/DashboardCharts"
import { CarHealthWidget } from "@/components/dashboard/CarHealthWidget"
import { TripCalculatorModal } from "@/components/dashboard/TripCalculatorModal"

export default function DashboardPage() {
  const navigate = useNavigate()
  const { data: summary, isLoading } = useDashboardSummary()

  const avgKml = summary?.avg_km_per_liter ?? 0
  const avgL100km = avgKml > 0 ? (100 / avgKml).toFixed(2) : "—"
  const fuelCost =
    summary?.total_fuel_cost != null
      ? summary.total_fuel_cost.toFixed(2).replace(".", ",")
      : "0,00"
  const maintenanceCost =
    summary?.total_maintenance_cost != null
      ? summary.total_maintenance_cost.toFixed(2).replace(".", ",")
      : "0,00"
  const totalSpent =
    summary?.total_spent != null
      ? summary.total_spent.toFixed(2).replace(".", ",")
      : "0,00"
  const currentKm =
    summary?.current_km != null
      ? summary.current_km.toLocaleString("it-IT")
      : "0"

  const hasPartialAlert = summary?.partial_alert?.is_warning

  return (
    <div className="space-y-6">
      {/* Top Banner / Welcome */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 rounded-2xl border border-border/70 bg-gradient-to-br from-card/90 via-card/50 to-emerald-950/20 p-5 md:p-6 backdrop-blur shadow-sm">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Badge variant="success" className="gap-1 text-xs">
              <Sparkles className="h-3 w-3" />
              Panoramica Flotta Attiva
            </Badge>
            <span className="text-xs text-muted-foreground font-mono">
              Contachilometri: <strong>{currentKm} km</strong>
            </span>
          </div>
          <h2 className="text-2xl md:text-3xl font-black tracking-tight">
            BMW Serie 1 — Riepilogo Operativo
          </h2>
          <p className="text-xs md:text-sm text-muted-foreground max-w-2xl">
            Monitora l'efficienza energetica, l'andamento dei prezzi carburante e la salute meccanica in tempo reale.
          </p>
        </div>

        <div className="flex items-center gap-2.5 w-full sm:w-auto">
          <Button
            variant="outline"
            size="sm"
            className="gap-1.5 flex-1 sm:flex-initial"
            onClick={() => navigate("/reports")}
          >
            <FileText className="h-4 w-4 text-muted-foreground" />
            <span>Report PDF</span>
          </Button>
          <div className="flex-1 sm:flex-initial">
            <TripCalculatorModal defaultAvgKml={avgKml} />
          </div>
        </div>
      </div>

      {/* Partial Refuelings Warning Banner (Appears only if partial accumulation is active) */}
      {hasPartialAlert && (
        <div className="rounded-xl border border-amber-500/40 bg-amber-500/10 p-4 flex items-center justify-between gap-3 animate-in fade-in duration-300">
          <div className="flex items-center gap-3">
            <AlertTriangle className="h-5 w-5 text-amber-400 shrink-0" />
            <div className="text-xs md:text-sm">
              <span className="font-bold text-amber-300">
                Allarme Rifornimenti Parziali Non Consolidati:{" "}
              </span>
              <span className="text-amber-200/90">
                Hai accumulato € {summary?.partial_alert.accumulated_cost.toFixed(2)} in{" "}
                {summary?.partial_alert.partials_count} rifornimenti parziali. Fai un pieno per consolidare l'esattezza dei consumi.
              </span>
            </div>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => navigate("/fuel")}
            className="shrink-0 border-amber-500/30 text-amber-300 hover:bg-amber-500/20 text-xs h-8"
          >
            Fai il Pieno
          </Button>
        </div>
      )}

      {/* 4 Smart KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* KPI 1: Efficienza / Consumo */}
        <Card className="hover:border-emerald-500/40 hover:shadow-lg hover:shadow-emerald-950/20 transition-all">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Consumo Medio Storico
            </CardTitle>
            <Gauge className="h-4 w-4 text-emerald-400" />
          </CardHeader>
          <CardContent className="space-y-1">
            {isLoading ? (
              <div className="space-y-2">
                <Skeleton className="h-8 w-28" />
                <Skeleton className="h-4 w-36" />
              </div>
            ) : avgKml > 0 ? (
              <>
                <div className="text-2xl font-bold tracking-tight">
                  {avgL100km} <span className="text-sm font-normal text-muted-foreground">L/100km</span>
                </div>
                <div className="flex items-center gap-1.5 text-xs text-emerald-400 font-medium">
                  <TrendingUp className="h-3.5 w-3.5" />
                  <span>{avgKml.toFixed(2)} km/L (Full-to-Full)</span>
                </div>
              </>
            ) : (
              <>
                <div className="text-2xl font-bold tracking-tight text-muted-foreground">
                  — <span className="text-sm font-normal text-muted-foreground/60">L/100km</span>
                </div>
                <div className="text-xs text-muted-foreground">
                  In attesa di rifornimenti pieni
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
                  {summary?.last_refueling?.date
                    ? `Ultimo pieno: ${summary.last_refueling.date}`
                    : "Nessun rifornimento registrato"}
                </div>
              </>
            )}
          </CardContent>
        </Card>

        {/* KPI 3: Manutenzioni */}
        <Card className="hover:border-amber-500/40 hover:shadow-lg transition-all">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Spesa Manutenzioni
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
                <div className="text-xs text-amber-400 flex items-center gap-1 font-medium">
                  <span>Totale interventi officina</span>
                </div>
              </>
            )}
          </CardContent>
        </Card>

        {/* KPI 4: Spesa Complessiva Totale */}
        <Card className="hover:border-indigo-500/40 hover:shadow-lg transition-all">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Spesa Complessiva Auto
            </CardTitle>
            <Wallet className="h-4 w-4 text-indigo-400" />
          </CardHeader>
          <CardContent className="space-y-1">
            {isLoading ? (
              <div className="space-y-2">
                <Skeleton className="h-8 w-24" />
                <Skeleton className="h-4 w-32" />
              </div>
            ) : (
              <>
                <div className="text-2xl font-bold tracking-tight text-indigo-300">€ {totalSpent}</div>
                <div className="text-xs text-muted-foreground">
                  Carburante + Tagliandi + Ricambi
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Main Analytics Grid: Recharts Time-Series Charts (Left) & Car Health Widget (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Interactive Charts with Time-Range Filters and Metric Tabs */}
        <DashboardCharts />

        {/* Car Health Score & Active Issues Diagnostic */}
        <CarHealthWidget
          healthScore={summary?.health_score}
          currentKm={summary?.current_km}
        />
      </div>
    </div>
  )
}

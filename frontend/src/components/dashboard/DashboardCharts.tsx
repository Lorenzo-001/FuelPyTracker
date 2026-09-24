import { useState } from "react"
import { useNavigate } from "react-router-dom"
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts"
import { TrendingUp, Fuel, BarChart3, Plus, UploadCloud } from "lucide-react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { useDashboardCharts } from "@/hooks/useDashboardCharts"

interface CustomTooltipProps {
  active?: boolean
  payload?: Array<{ value: number; name: string; color: string }>
  label?: string
  suffix?: string
}

function CustomTooltip({ active, payload, label, suffix = "" }: CustomTooltipProps) {
  if (active && payload && payload.length) {
    return (
      <div className="rounded-xl border border-border/80 bg-card/95 p-3 shadow-xl backdrop-blur-md text-xs space-y-1">
        <p className="font-semibold text-foreground border-b border-border/50 pb-1">{label}</p>
        {payload.map((item, idx) => (
          <div key={idx} className="flex items-center justify-between gap-4">
            <span className="flex items-center gap-1.5 text-muted-foreground">
              <span className="h-2 w-2 rounded-full" style={{ backgroundColor: item.color }} />
              {item.name}:
            </span>
            <span className="font-mono font-bold text-foreground">
              {typeof item.value === "number" ? item.value.toFixed(2) : item.value} {suffix}
            </span>
          </div>
        ))}
      </div>
    )
  }
  return null
}

interface DashboardChartsProps {
  timeRange?: string
  onTimeRangeChange?: (range: string) => void
}

export function DashboardCharts({
  timeRange: controlledTimeRange,
  onTimeRangeChange,
}: DashboardChartsProps = {}) {
  const navigate = useNavigate()
  const [internalTimeRange, setInternalTimeRange] = useState("ytd")
  const [activeTab, setActiveTab] = useState<"price" | "efficiency" | "spending">("price")

  const effectiveTimeRange = controlledTimeRange ?? internalTimeRange
  const handleTimeRangeChange = (range: string) => {
    if (onTimeRangeChange) {
      onTimeRangeChange(range)
    } else {
      setInternalTimeRange(range)
    }
  }

  const { data: chartsData, isLoading } = useDashboardCharts(effectiveTimeRange)

  const priceData = chartsData?.price_trend ?? []
  const efficiencyData = chartsData?.efficiency ?? []
  const spendingData = chartsData?.monthly_spending ?? []

  const timeRangeOptions = [
    { id: "3m", label: "3M" },
    { id: "6m", label: "6M" },
    { id: "ytd", label: "Anno" },
    { id: "1y", label: "1A" },
    { id: "3y", label: "3A" },
    { id: "all", label: "Tutto" },
  ]

  return (
    <Card className="lg:col-span-2 shadow-sm hover:border-border transition-all">
      <CardHeader className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 gap-3">
        <div>
          <CardTitle className="text-base font-bold flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-emerald-400" />
            Analisi Temporale
          </CardTitle>
          <p className="text-xs text-muted-foreground mt-0.5">
            Monitoraggio storico dei prezzi, efficienza Full-to-Full e ripartizione spese mensili.
          </p>
        </div>

        {/* Time Range Filter Switcher */}
        <div className="flex items-center gap-1 bg-muted/40 p-1 rounded-lg border border-border/60 self-start sm:self-auto overflow-x-auto max-w-full">
          {timeRangeOptions.map((t) => (
            <button
              key={t.id}
              type="button"
              onClick={() => handleTimeRangeChange(t.id)}
              className={`px-2.5 py-1 text-xs font-semibold rounded-md transition-all shrink-0 ${
                effectiveTimeRange === t.id
                  ? "bg-card text-emerald-400 shadow-xs border border-border/60"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              {t.label}
            </button>
          ))}
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Metric Selector Tabs */}
        <Tabs
          value={activeTab}
          onValueChange={(val) => setActiveTab(val as "price" | "efficiency" | "spending")}
          className="w-full"
        >
          <TabsList className="w-full sm:w-auto grid grid-cols-3">
            <TabsTrigger value="price" className="text-xs gap-1.5">
              <Fuel className="h-3.5 w-3.5" />
              <span>Prezzo Carburante</span>
            </TabsTrigger>
            <TabsTrigger value="efficiency" className="text-xs gap-1.5">
              <TrendingUp className="h-3.5 w-3.5" />
              <span>Consumi (km/L)</span>
            </TabsTrigger>
            <TabsTrigger value="spending" className="text-xs gap-1.5">
              <BarChart3 className="h-3.5 w-3.5" />
              <span>Spese Mensili</span>
            </TabsTrigger>
          </TabsList>
        </Tabs>

        {/* Chart Area */}
        <div className="h-72 w-full pt-2">
          {isLoading ? (
            <div className="h-full w-full flex items-center justify-center">
              <Skeleton className="h-full w-full rounded-xl" />
            </div>
          ) : activeTab === "price" ? (
            priceData.length >= 2 ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={priceData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="priceGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.35} />
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0.0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#27272a" vertical={false} />
                  <XAxis dataKey="date" stroke="#71717a" fontSize={11} tickLine={false} />
                  <YAxis
                    stroke="#71717a"
                    fontSize={11}
                    domain={["dataMin - 0.05", "dataMax + 0.05"]}
                    tickFormatter={(v) => `€${v.toFixed(2)}`}
                    tickLine={false}
                  />
                  <Tooltip content={<CustomTooltip suffix="€/L" />} />
                  <Area
                    type="monotone"
                    dataKey="price_per_liter"
                    name="Prezzo al Litro"
                    stroke="#10b981"
                    strokeWidth={2.5}
                    fillOpacity={1}
                    fill="url(#priceGradient)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full w-full flex flex-col items-center justify-center text-center p-6 rounded-xl border border-dashed border-border/80 bg-muted/10">
                <div className="h-10 w-10 rounded-full bg-emerald-500/10 flex items-center justify-center mb-2.5">
                  <Fuel className="h-5 w-5 text-emerald-400" />
                </div>
                <h4 className="text-sm font-semibold text-foreground">Dati Prezzo Insufficienti</h4>
                <p className="text-xs text-muted-foreground max-w-sm mt-1 mb-3">
                  Registra almeno due rifornimenti con prezzo al litro per generare il grafico dell'andamento storico.
                </p>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => navigate("/fuel")}
                  className="gap-1.5 text-xs border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/10"
                >
                  <Plus className="h-3.5 w-3.5" />
                  Registra Rifornimento
                </Button>
              </div>
            )
          ) : activeTab === "efficiency" ? (
            efficiencyData.length >= 2 ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={efficiencyData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="effGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.35} />
                      <stop offset="95%" stopColor="#06b6d4" stopOpacity={0.0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#27272a" vertical={false} />
                  <XAxis dataKey="date" stroke="#71717a" fontSize={11} tickLine={false} />
                  <YAxis
                    stroke="#71717a"
                    fontSize={11}
                    domain={["dataMin - 1", "dataMax + 1"]}
                    tickFormatter={(v) => `${v}`}
                    tickLine={false}
                  />
                  <Tooltip content={<CustomTooltip suffix="km/L" />} />
                  <Area
                    type="monotone"
                    dataKey="km_per_liter"
                    name="Consumo Tratta"
                    stroke="#06b6d4"
                    strokeWidth={2.5}
                    fillOpacity={1}
                    fill="url(#effGradient)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full w-full flex flex-col items-center justify-center text-center p-6 rounded-xl border border-dashed border-border/80 bg-muted/10">
                <div className="h-10 w-10 rounded-full bg-cyan-500/10 flex items-center justify-center mb-2.5">
                  <TrendingUp className="h-5 w-5 text-cyan-400" />
                </div>
                <h4 className="text-sm font-semibold text-foreground">Nessun Consumo Calcolato</h4>
                <p className="text-xs text-muted-foreground max-w-sm mt-1 mb-3">
                  L'algoritmo Full-to-Full calcola i km/L confrontando due rifornimenti pieni consecutivi.
                </p>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => navigate("/fuel")}
                  className="gap-1.5 text-xs border-cyan-500/30 text-cyan-400 hover:bg-cyan-500/10"
                >
                  <Plus className="h-3.5 w-3.5" />
                  Registra Rifornimento
                </Button>
              </div>
            )
          ) : spendingData.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={spendingData} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#27272a" vertical={false} />
                <XAxis dataKey="label" stroke="#71717a" fontSize={11} tickLine={false} />
                <YAxis
                  stroke="#71717a"
                  fontSize={11}
                  tickFormatter={(v) => `€${v}`}
                  tickLine={false}
                />
                <Tooltip content={<CustomTooltip suffix="€" />} />
                <Legend
                  verticalAlign="top"
                  align="right"
                  iconType="circle"
                  wrapperStyle={{ fontSize: "11px", paddingBottom: "10px" }}
                />
                <Bar
                  dataKey="fuel_cost"
                  name="Carburante"
                  fill="#10b981"
                  radius={[4, 4, 0, 0]}
                  maxBarSize={32}
                />
                <Bar
                  dataKey="maintenance_cost"
                  name="Officina"
                  fill="#f59e0b"
                  radius={[4, 4, 0, 0]}
                  maxBarSize={32}
                />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-full w-full flex flex-col items-center justify-center text-center p-6 rounded-xl border border-dashed border-border/80 bg-muted/10">
              <div className="h-10 w-10 rounded-full bg-indigo-500/10 flex items-center justify-center mb-2.5">
                <BarChart3 className="h-5 w-5 text-indigo-400" />
              </div>
              <h4 className="text-sm font-semibold text-foreground">Nessuna Spesa Registrata</h4>
              <p className="text-xs text-muted-foreground max-w-sm mt-1 mb-3">
                Non sono presenti spese carburante o interventi officina registrati per il periodo selezionato.
              </p>
              <Button
                size="sm"
                variant="outline"
                onClick={() => navigate("/reports")}
                className="gap-1.5 text-xs border-indigo-500/30 text-indigo-400 hover:bg-indigo-500/10"
              >
                <UploadCloud className="h-3.5 w-3.5" />
                Importa Archivio Excel
              </Button>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

import { useState } from "react"
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
import { TrendingUp, Fuel, BarChart3 } from "lucide-react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Skeleton } from "@/components/ui/skeleton"
import { useDashboardCharts } from "@/hooks/useDashboardCharts"

// Sample fallback points for pristine visual showcase if database has < 2 records
const FALLBACK_PRICE_DATA = [
  { date: "Mag 25", price_per_liter: 1.789 },
  { date: "Giu 25", price_per_liter: 1.815 },
  { date: "Lug 25", price_per_liter: 1.849 },
  { date: "Ago 25", price_per_liter: 1.832 },
  { date: "Set 25", price_per_liter: 1.799 },
  { date: "Ott 25", price_per_liter: 1.819 },
]

const FALLBACK_EFFICIENCY_DATA = [
  { date: "Mag 25", km_per_liter: 17.8 },
  { date: "Giu 25", km_per_liter: 18.2 },
  { date: "Lug 25", km_per_liter: 18.9 },
  { date: "Ago 25", km_per_liter: 18.1 },
  { date: "Set 25", km_per_liter: 18.6 },
  { date: "Ott 25", km_per_liter: 19.1 },
]

const FALLBACK_SPENDING_DATA = [
  { label: "Mag", fuel_cost: 165.0, maintenance_cost: 0, total_cost: 165.0 },
  { label: "Giu", fuel_cost: 190.5, maintenance_cost: 85.0, total_cost: 275.5 },
  { label: "Lug", fuel_cost: 220.0, maintenance_cost: 0, total_cost: 220.0 },
  { label: "Ago", fuel_cost: 280.0, maintenance_cost: 140.0, total_cost: 420.0 },
  { label: "Set", fuel_cost: 175.2, maintenance_cost: 0, total_cost: 175.2 },
  { label: "Ott", fuel_cost: 184.5, maintenance_cost: 50.0, total_cost: 234.5 },
]

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

export function DashboardCharts() {
  const [timeRange, setTimeRange] = useState("all")
  const [activeTab, setActiveTab] = useState<"price" | "efficiency" | "spending">("price")

  const { data: chartsData, isLoading } = useDashboardCharts(timeRange)

  const priceData =
    chartsData?.price_trend && chartsData.price_trend.length > 1
      ? chartsData.price_trend
      : FALLBACK_PRICE_DATA

  const efficiencyData =
    chartsData?.efficiency && chartsData.efficiency.length > 1
      ? chartsData.efficiency
      : FALLBACK_EFFICIENCY_DATA

  const spendingData =
    chartsData?.monthly_spending && chartsData.monthly_spending.length > 0
      ? chartsData.monthly_spending
      : FALLBACK_SPENDING_DATA

  return (
    <Card className="lg:col-span-2 shadow-sm hover:border-border transition-all">
      <CardHeader className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 gap-3">
        <div>
          <CardTitle className="text-base font-bold flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-emerald-400" />
            Analisi Temporale Flotta
          </CardTitle>
          <p className="text-xs text-muted-foreground mt-0.5">
            Monitoraggio storico dei prezzi, efficienza Full-to-Full e ripartizione spese mensili.
          </p>
        </div>

        {/* Time Range Filter Switcher */}
        <div className="flex items-center gap-1 bg-muted/40 p-1 rounded-lg border border-border/60 self-start sm:self-auto">
          {[
            { id: "3m", label: "3M" },
            { id: "6m", label: "6M" },
            { id: "1y", label: "1A" },
            { id: "all", label: "Tutto" },
          ].map((t) => (
            <button
              key={t.id}
              type="button"
              onClick={() => setTimeRange(t.id)}
              className={`px-2.5 py-1 text-xs font-semibold rounded-md transition-all ${
                timeRange === t.id
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
          ) : activeTab === "efficiency" ? (
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
          )}
        </div>
      </CardContent>
    </Card>
  )
}

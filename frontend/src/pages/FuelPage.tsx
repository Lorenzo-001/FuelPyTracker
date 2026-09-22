import { useState, useMemo, useEffect } from "react"
import { useSearchParams } from "react-router-dom"
import {
  Fuel,
  Plus,
  Camera,
  Search,
  Table2,
  LayoutGrid,
  RefreshCw,
} from "lucide-react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Skeleton } from "@/components/ui/skeleton"
import { useRefuelings } from "@/hooks/useRefuelings"
import { FuelTable } from "@/components/fuel/FuelTable"
import { FuelCardList } from "@/components/fuel/FuelCardList"
import { FuelFormModal } from "@/components/fuel/FuelFormModal"
import { ReceiptOcrModal } from "@/components/fuel/ReceiptOcrModal"
import { FuelInspectorSheet } from "@/components/fuel/FuelInspectorSheet"
import type { RefuelingResponse } from "@/types"

export default function FuelPage() {
  const [searchParams, setSearchParams] = useSearchParams()

  // State: Modals and Sheets
  const [isFormOpen, setIsFormOpen] = useState(false)
  const [isOcrOpen, setIsOcrOpen] = useState(false)
  const [editingRefueling, setEditingRefueling] = useState<RefuelingResponse | null>(null)
  const [selectedRefueling, setSelectedRefueling] = useState<RefuelingResponse | null>(null)
  const [ocrPrefillData, setOcrPrefillData] = useState<{
    date?: string
    price_per_liter?: number
    total_cost?: number
    liters?: number
    notes?: string
  } | null>(null)

  // State: View and Filters
  const [viewMode, setViewMode] = useState<"table" | "cards">("table")
  const [searchQuery, setSearchQuery] = useState("")
  const [typeFilter, setTypeFilter] = useState<"all" | "full" | "partial">("all")
  const [selectedYear, setSelectedYear] = useState<number | undefined>(undefined)

  // Data fetching via React Query
  const { data: refuelings, isLoading, isError, refetch } = useRefuelings(selectedYear)

  // Handle ?action=new query param (e.g. from FAB or Header)
  useEffect(() => {
    if (searchParams.get("action") === "new") {
      const timer = setTimeout(() => {
        setEditingRefueling(null)
        setOcrPrefillData(null)
        setIsFormOpen(true)
        setSearchParams(
          (prev) => {
            const next = new URLSearchParams(prev)
            next.delete("action")
            return next
          },
          { replace: true }
        )
      }, 0)
      return () => clearTimeout(timer)
    }
  }, [searchParams, setSearchParams])

  // Listen for global custom event 'open-new-refueling'
  useEffect(() => {
    const handleGlobalNew = () => {
      setEditingRefueling(null)
      setOcrPrefillData(null)
      setIsFormOpen(true)
    }
    window.addEventListener("open-new-refueling", handleGlobalNew)
    return () => window.removeEventListener("open-new-refueling", handleGlobalNew)
  }, [])

  // Calculate available years for dropdown
  const availableYears = useMemo(() => {
    if (!refuelings) return []
    const years = new Set<number>()
    refuelings.forEach((r) => {
      const y = parseInt(r.date.split("-")[0], 10)
      if (!isNaN(y)) years.add(y)
    })
    return Array.from(years).sort((a, b) => b - a)
  }, [refuelings])

  // Filtered dataset
  const filteredRefuelings = useMemo(() => {
    if (!refuelings) return []
    return refuelings.filter((r) => {
      // Type filter
      if (typeFilter === "full" && !r.is_full_tank) return false
      if (typeFilter === "partial" && r.is_full_tank) return false

      // Search query (notes, station, date, km)
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase()
        const matchNotes = r.notes?.toLowerCase().includes(q) || false
        const matchDate = r.date.includes(q)
        const matchKm = r.total_km.toString().includes(q)
        if (!matchNotes && !matchDate && !matchKm) return false
      }

      return true
    })
  }, [refuelings, typeFilter, searchQuery])

  // Quick statistics on filtered set
  const stats = useMemo(() => {
    if (!filteredRefuelings.length) {
      return { count: 0, totalCost: 0, totalLiters: 0, avgKmL: 0 }
    }
    const count = filteredRefuelings.length
    const totalCost = filteredRefuelings.reduce((sum, r) => sum + r.total_cost, 0)
    const totalLiters = filteredRefuelings.reduce((sum, r) => sum + r.liters, 0)
    const withKmL = filteredRefuelings.filter((r) => r.km_per_liter !== null && r.km_per_liter > 0)
    const avgKmL =
      withKmL.length > 0
        ? withKmL.reduce((sum, r) => sum + (r.km_per_liter || 0), 0) / withKmL.length
        : 0

    return { count, totalCost, totalLiters, avgKmL }
  }, [filteredRefuelings])

  const handleStartCreate = () => {
    setEditingRefueling(null)
    setOcrPrefillData(null)
    setIsFormOpen(true)
  }

  const handleStartEdit = (refueling: RefuelingResponse) => {
    setEditingRefueling(refueling)
    setOcrPrefillData(null)
    setIsFormOpen(true)
  }

  const handleApplyOcrData = (data: {
    date?: string
    price_per_liter?: number
    total_cost?: number
    liters?: number
    notes?: string
  }) => {
    setEditingRefueling(null)
    setOcrPrefillData(data)
    setIsFormOpen(true)
  }

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
            Archivio cronologico dei pieni, calcolo automatico del consumo medio ed efficienza Full-to-Full.
          </p>
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <Button
            variant="outline"
            size="sm"
            className="gap-1.5 flex-1 sm:flex-none border-border/80 hover:border-emerald-500/50"
            onClick={() => setIsOcrOpen(true)}
          >
            <Camera className="h-4 w-4 text-emerald-400" />
            <span>Scansione OCR</span>
          </Button>

          <Button
            variant="emerald"
            size="sm"
            className="gap-1.5 flex-1 sm:flex-none"
            onClick={handleStartCreate}
          >
            <Plus className="h-4 w-4" />
            <span>Nuovo Pieno</span>
          </Button>
        </div>
      </div>

      {/* Quick Aggregate Stats Ribbon */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="p-3.5 rounded-xl bg-card border border-border/60 flex flex-col justify-between">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
            Pieni Registrati
          </span>
          <div className="mt-1 flex items-baseline gap-1.5">
            <span className="text-xl font-bold font-mono text-foreground">{stats.count}</span>
            <span className="text-xs text-muted-foreground">record</span>
          </div>
        </div>

        <div className="p-3.5 rounded-xl bg-card border border-border/60 flex flex-col justify-between">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
            Spesa Totale
          </span>
          <div className="mt-1 flex items-baseline gap-1.5">
            <span className="text-xl font-bold font-mono text-emerald-400">
              {stats.totalCost.toLocaleString("it-IT", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </span>
            <span className="text-xs text-muted-foreground">€</span>
          </div>
        </div>

        <div className="p-3.5 rounded-xl bg-card border border-border/60 flex flex-col justify-between">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
            Carburante Immesso
          </span>
          <div className="mt-1 flex items-baseline gap-1.5">
            <span className="text-xl font-bold font-mono text-foreground">
              {stats.totalLiters.toFixed(1)}
            </span>
            <span className="text-xs text-muted-foreground">L</span>
          </div>
        </div>

        <div className="p-3.5 rounded-xl bg-card border border-border/60 flex flex-col justify-between">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
            Consumo Medio Reale
          </span>
          <div className="mt-1 flex items-baseline gap-1.5">
            <span className="text-xl font-bold font-mono text-emerald-400">
              {stats.avgKmL > 0 ? stats.avgKmL.toFixed(2) : "—"}
            </span>
            <span className="text-xs text-muted-foreground">km/L</span>
          </div>
        </div>
      </div>

      {/* Filter and Search Bar with View Switcher */}
      <Card className="border-border/60">
        <CardContent className="p-3.5 flex flex-col md:flex-row gap-3 items-center justify-between">
          {/* Search Input */}
          <div className="relative w-full md:w-80">
            <Search className="h-4 w-4 absolute left-3 top-2.5 text-muted-foreground" />
            <Input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Cerca stazione, data, km..."
              className="pl-9 h-9 text-xs"
            />
          </div>

          {/* Filters & View Switcher */}
          <div className="flex flex-wrap items-center gap-2 w-full md:w-auto justify-between md:justify-end">
            {/* Type Filter Buttons */}
            <div className="flex items-center rounded-lg bg-muted/40 p-1 border border-border/40 text-xs">
              <button
                type="button"
                onClick={() => setTypeFilter("all")}
                className={`px-2.5 py-1 rounded-md transition-all font-medium ${
                  typeFilter === "all"
                    ? "bg-background text-foreground shadow-sm"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                Tutti
              </button>
              <button
                type="button"
                onClick={() => setTypeFilter("full")}
                className={`px-2.5 py-1 rounded-md transition-all font-medium ${
                  typeFilter === "full"
                    ? "bg-background text-emerald-400 shadow-sm"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                Solo Pieni
              </button>
              <button
                type="button"
                onClick={() => setTypeFilter("partial")}
                className={`px-2.5 py-1 rounded-md transition-all font-medium ${
                  typeFilter === "partial"
                    ? "bg-background text-amber-400 shadow-sm"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                Parziali
              </button>
            </div>

            {/* Year Selector */}
            {availableYears.length > 0 && (
              <select
                value={selectedYear || ""}
                onChange={(e) => setSelectedYear(e.target.value ? parseInt(e.target.value, 10) : undefined)}
                className="h-9 px-2.5 rounded-lg bg-muted/40 border border-border/40 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-emerald-500"
              >
                <option value="">Tutti gli anni</option>
                {availableYears.map((yr) => (
                  <option key={yr} value={yr}>
                    Anno {yr}
                  </option>
                ))}
              </select>
            )}

            {/* View Switcher: Table vs Cards */}
            <div className="flex items-center rounded-lg bg-muted/40 p-1 border border-border/40">
              <button
                type="button"
                onClick={() => setViewMode("table")}
                className={`p-1.5 rounded-md transition-all ${
                  viewMode === "table"
                    ? "bg-background text-emerald-400 shadow-sm"
                    : "text-muted-foreground hover:text-foreground"
                }`}
                title="Vista Tabella"
              >
                <Table2 className="h-4 w-4" />
              </button>
              <button
                type="button"
                onClick={() => setViewMode("cards")}
                className={`p-1.5 rounded-md transition-all ${
                  viewMode === "cards"
                    ? "bg-background text-emerald-400 shadow-sm"
                    : "text-muted-foreground hover:text-foreground"
                }`}
                title="Vista Schede"
              >
                <LayoutGrid className="h-4 w-4" />
              </button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Main Content Area */}
      <Card className="border-border/60 overflow-hidden">
        <CardHeader className="flex flex-row items-center justify-between pb-3 border-b border-border/50">
          <div>
            <CardTitle className="text-base font-bold">
              Cronologia Rifornimenti
            </CardTitle>
            <p className="text-xs text-muted-foreground mt-0.5">
              Clicca su una riga per aprire il pannello di dettaglio, apportare modifiche o eliminare.
            </p>
          </div>

          <Button
            variant="ghost"
            size="sm"
            onClick={() => refetch()}
            className="h-8 w-8 p-0 text-muted-foreground hover:text-foreground"
            title="Ricarica elenco"
          >
            <RefreshCw className="h-4 w-4" />
          </Button>
        </CardHeader>

        <CardContent className="p-0">
          {isLoading ? (
            <div className="p-6 space-y-3">
              {[1, 2, 3, 4, 5].map((i) => (
                <Skeleton key={i} className="h-10 w-full" />
              ))}
            </div>
          ) : isError ? (
            <div className="p-12 text-center text-muted-foreground space-y-3">
              <p className="text-rose-400 text-sm">
                Si è verificato un errore durante il recupero dei rifornimenti.
              </p>
              <Button variant="outline" size="sm" onClick={() => refetch()}>
                Riprova
              </Button>
            </div>
          ) : viewMode === "table" ? (
            <FuelTable
              refuelings={filteredRefuelings}
              onSelect={(r) => setSelectedRefueling(r)}
            />
          ) : (
            <div className="p-4">
              <FuelCardList
                refuelings={filteredRefuelings}
                onSelect={(r) => setSelectedRefueling(r)}
              />
            </div>
          )}
        </CardContent>
      </Card>

      {/* Modale Nuovo / Modifica Rifornimento */}
      <FuelFormModal
        open={isFormOpen}
        onOpenChange={setIsFormOpen}
        initialData={editingRefueling}
        prefillData={ocrPrefillData}
      />

      {/* Modale Scansione OCR Scontrino */}
      <ReceiptOcrModal
        open={isOcrOpen}
        onOpenChange={setIsOcrOpen}
        onApplyData={handleApplyOcrData}
      />

      {/* Side Inspector Dettaglio Rifornimento */}
      <FuelInspectorSheet
        open={!!selectedRefueling}
        onOpenChange={(open) => !open && setSelectedRefueling(null)}
        refueling={selectedRefueling}
        onEdit={handleStartEdit}
      />
    </div>
  )
}

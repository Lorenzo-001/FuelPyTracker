import { useState, useMemo } from "react"
import {
  Wrench,
  Plus,
  Search,
  RefreshCw,
} from "lucide-react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Skeleton } from "@/components/ui/skeleton"
import { useMaintenances, useMaintenanceCategories } from "@/hooks/useMaintenance"
import { DeadlineBanner } from "@/components/maintenance/DeadlineBanner"
import { MaintenanceTimeline } from "@/components/maintenance/MaintenanceTimeline"
import { MaintenanceFormModal } from "@/components/maintenance/MaintenanceFormModal"
import type { MaintenanceResponse } from "@/types"

export default function MaintenancePage() {
  const [isFormOpen, setIsFormOpen] = useState(false)
  const [editingRecord, setEditingRecord] = useState<MaintenanceResponse | null>(null)

  const [searchQuery, setSearchQuery] = useState("")
  const [selectedCategory, setSelectedCategory] = useState<string>("")
  const [selectedYear, setSelectedYear] = useState<number | undefined>(undefined)

  const { data: maintenances, isLoading, isError, refetch } = useMaintenances(
    selectedYear,
    selectedCategory || undefined
  )
  const { data: categories } = useMaintenanceCategories()

  // Available years
  const availableYears = useMemo(() => {
    if (!maintenances) return []
    const years = new Set<number>()
    maintenances.forEach((m) => {
      const y = parseInt(m.date.split("-")[0], 10)
      if (!isNaN(y)) years.add(y)
    })
    return Array.from(years).sort((a, b) => b - a)
  }, [maintenances])

  // Filtered dataset
  const filteredRecords = useMemo(() => {
    if (!maintenances) return []
    return maintenances.filter((m) => {
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase()
        const matchDesc = m.description?.toLowerCase().includes(q) || false
        const matchType = m.expense_type.toLowerCase().includes(q)
        const matchDate = m.date.includes(q)
        const matchKm = m.total_km.toString().includes(q)
        if (!matchDesc && !matchType && !matchDate && !matchKm) return false
      }
      return true
    })
  }, [maintenances, searchQuery])

  // Quick stats
  const stats = useMemo(() => {
    if (!maintenances || !maintenances.length) {
      return { totalCost: 0, count: 0, lastDate: "—", lastKm: "—" }
    }
    const totalCost = maintenances.reduce((sum, m) => sum + m.cost, 0)
    const count = maintenances.length
    const sorted = [...maintenances].sort((a, b) => b.date.localeCompare(a.date))
    const last = sorted[0]
    return {
      totalCost,
      count,
      lastDate: last.date,
      lastKm: last.total_km.toLocaleString("it-IT"),
    }
  }, [maintenances])

  const handleStartCreate = () => {
    setEditingRecord(null)
    setIsFormOpen(true)
  }

  const handleStartEdit = (record: MaintenanceResponse) => {
    setEditingRecord(record)
    setIsFormOpen(true)
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-extrabold tracking-tight flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-amber-500/10 text-amber-400">
              <Wrench className="h-5 w-5" />
            </div>
            Registro Manutenzioni & Officina
          </h2>
          <p className="text-sm text-muted-foreground mt-1">
            Archivio tagliandi, ricambi e monitoraggio predittivo delle scadenze dei componenti.
          </p>
        </div>

        <Button
          variant="emerald"
          size="sm"
          className="gap-1.5 w-full sm:w-auto"
          onClick={handleStartCreate}
        >
          <Plus className="h-4 w-4" />
          <span>Nuova Manutenzione</span>
        </Button>
      </div>

      {/* Quick Aggregate Stats Ribbon */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="p-3.5 rounded-xl bg-card border border-border/60 flex flex-col justify-between">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
            Spesa Complessiva
          </span>
          <div className="mt-1 flex items-baseline gap-1.5">
            <span className="text-xl font-bold font-mono text-foreground">
              {stats.totalCost.toLocaleString("it-IT", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            </span>
            <span className="text-xs text-muted-foreground">€</span>
          </div>
        </div>

        <div className="p-3.5 rounded-xl bg-card border border-border/60 flex flex-col justify-between">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
            Interventi Svolti
          </span>
          <div className="mt-1 flex items-baseline gap-1.5">
            <span className="text-xl font-bold font-mono text-foreground">{stats.count}</span>
            <span className="text-xs text-muted-foreground">voci</span>
          </div>
        </div>

        <div className="p-3.5 rounded-xl bg-card border border-border/60 flex flex-col justify-between">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
            Ultimo Intervento
          </span>
          <div className="mt-1 flex items-baseline gap-1.5">
            <span className="text-sm font-bold font-mono text-emerald-400">
              {stats.lastDate}
            </span>
          </div>
        </div>

        <div className="p-3.5 rounded-xl bg-card border border-border/60 flex flex-col justify-between">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
            Km Ultimo Check
          </span>
          <div className="mt-1 flex items-baseline gap-1.5">
            <span className="text-base font-bold font-mono text-foreground">
              {stats.lastKm}
            </span>
            <span className="text-xs text-muted-foreground">km</span>
          </div>
        </div>
      </div>

      {/* Predictive Deadlines Banner */}
      <DeadlineBanner />

      {/* Filter and Search Bar */}
      <Card className="border-border/60">
        <CardContent className="p-3.5 flex flex-col md:flex-row gap-3 items-center justify-between">
          {/* Search Input */}
          <div className="relative w-full md:w-80">
            <Search className="h-4 w-4 absolute left-3 top-2.5 text-muted-foreground" />
            <Input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Cerca per lavorazione, ricambio..."
              className="pl-9 h-9 text-xs"
            />
          </div>

          {/* Filters: Category and Year */}
          <div className="flex flex-wrap items-center gap-2 w-full md:w-auto justify-between md:justify-end">
            {categories && categories.length > 0 && (
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="h-9 px-2.5 rounded-lg bg-muted/40 border border-border/40 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-emerald-500"
              >
                <option value="">Tutte le categorie</option>
                {categories.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat}
                  </option>
                ))}
              </select>
            )}

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

            <Button
              variant="ghost"
              size="sm"
              onClick={() => refetch()}
              className="h-9 w-9 p-0 text-muted-foreground hover:text-foreground"
              title="Ricarica elenco"
            >
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Main Content Area: Timeline */}
      <Card className="border-border/60 overflow-hidden">
        <CardHeader className="flex flex-row items-center justify-between pb-3 border-b border-border/50">
          <div>
            <CardTitle className="text-base font-bold">
              Timeline Cronologica Officina
            </CardTitle>
            <p className="text-xs text-muted-foreground mt-0.5">
              Storico sequenziale degli interventi con indicazione chilometrica e promemoria successivi.
            </p>
          </div>
        </CardHeader>

        <CardContent className="p-4 sm:p-6">
          {isLoading ? (
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-24 w-full rounded-xl" />
              ))}
            </div>
          ) : isError ? (
            <div className="p-8 text-center text-muted-foreground space-y-3">
              <p className="text-rose-400 text-sm">
                Si è verificato un errore durante il recupero degli interventi.
              </p>
              <Button variant="outline" size="sm" onClick={() => refetch()}>
                Riprova
              </Button>
            </div>
          ) : (
            <MaintenanceTimeline
              records={filteredRecords}
              onEdit={handleStartEdit}
            />
          )}
        </CardContent>
      </Card>

      {/* Modal Inserimento / Modifica Manutenzione */}
      <MaintenanceFormModal
        open={isFormOpen}
        onOpenChange={setIsFormOpen}
        initialData={editingRecord}
      />
    </div>
  )
}

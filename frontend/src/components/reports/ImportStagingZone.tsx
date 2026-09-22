import { useState, useRef } from "react"
import {
  Upload,
  FileSpreadsheet,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Loader2,
  RefreshCw,
  Database,
  Info,
  Check,
  Fuel,
  Wrench,
  Edit3,
} from "lucide-react"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"
import {
  Table,
  TableHeader,
  TableRow,
  TableHead,
  TableBody,
  TableCell,
} from "@/components/ui/table"
import { usePreviewImport, useCommitImport, useRevalidateImport } from "@/hooks/useReports"
import { ImportRowEditModal } from "./ImportRowEditModal"
import type {
  ImportPreviewResponse,
  ImportCommitRowFuel,
  ImportCommitRowMaintenance,
} from "@/types"
import { toast } from "sonner"

export function ImportStagingZone() {
  const [dragActive, setDragActive] = useState(false)
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [previewData, setPreviewData] = useState<ImportPreviewResponse | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const previewMutation = usePreviewImport()
  const commitMutation = useCommitImport()
  const revalidateMutation = useRevalidateImport()

  const [editModalOpen, setEditModalOpen] = useState(false)
  const [editRowIndex, setEditRowIndex] = useState<number | null>(null)
  const [editRowType, setEditRowType] = useState<"fuel" | "maintenance">("fuel")
  const [editRowData, setEditRowData] = useState<Record<string, unknown> | null>(null)

  const handleOpenEdit = (
    row: Record<string, unknown>,
    index: number,
    type: "fuel" | "maintenance"
  ) => {
    setEditRowData(row)
    setEditRowIndex(index)
    setEditRowType(type)
    setEditModalOpen(true)
  }

  const handleRowEditSave = async (
    updatedRow: Record<string, unknown>,
    index: number,
    type: "fuel" | "maintenance"
  ) => {
    if (!previewData) return

    const newFuelRows = [...(previewData.fuel_rows || [])]
    const newMaintRows = [...(previewData.maintenance_rows || [])]

    if (type === "fuel") {
      newFuelRows[index] = updatedRow
    } else {
      newMaintRows[index] = updatedRow
    }

    try {
      toast.loading("Rivalidazione delle regole in corso...", { id: "revalidate-toast" })
      const freshPreview = await revalidateMutation.mutateAsync({
        fuel_rows: newFuelRows,
        maintenance_rows: newMaintRows,
      })
      setPreviewData(freshPreview)
      toast.success("Riga rettificata e ricalcolata con successo!", { id: "revalidate-toast" })
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Errore durante la rivalutazione dei record"
      toast.error(msg, { id: "revalidate-toast" })
    }
  }

  const handleFile = async (file: File) => {
    if (!file.name.endsWith(".xlsx") && !file.name.endsWith(".csv")) {
      toast.error("Formato non supportato. Carica un file .xlsx o .csv")
      return
    }

    setSelectedFile(file)
    try {
      const res = await previewMutation.mutateAsync(file)
      setPreviewData(res)
      if (res.global_error) {
        toast.error(`Errore analisi file: ${res.global_error}`)
      } else {
        const totalRows = (res.fuel_rows?.length || 0) + (res.maintenance_rows?.length || 0)
        toast.success(`Analisi completata: trovate ${totalRows} righe da elaborare`)
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Errore durante l'analisi del file"
      toast.error(msg)
    }
  }

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0])
    }
  }

  const resetStaging = () => {
    setSelectedFile(null)
    setPreviewData(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
  }

  const handleCommit = async () => {
    if (!previewData) return

    const fuelRows: ImportCommitRowFuel[] = (previewData.fuel_rows || [])
      .filter((r) => r.Stato !== "Errore")
      .map((r) => ({
        date: String(r.Data || "").split("T")[0],
        total_km: Number(r.Km || 0),
        price_per_liter: Number(r.Prezzo || 0),
        total_cost: Number(r.Costo || 0),
        liters: Number(r.Litri || 0),
        is_full_tank: Boolean(r.Pieno ?? true),
        notes: r.Note ? String(r.Note) : null,
        db_id: r.db_id ? Number(r.db_id) : null,
        status: String(r.Stato || "Nuovo"),
      }))

    const maintRows: ImportCommitRowMaintenance[] = (previewData.maintenance_rows || [])
      .filter((r) => r.Stato !== "Errore")
      .map((r) => ({
        date: String(r.Data || "").split("T")[0],
        total_km: Number(r.Km || 0),
        expense_type: String(r.Tipo || "Altro"),
        cost: Number(r.Costo || 0),
        description: r.Descrizione ? String(r.Descrizione) : null,
        expiry_km: r["Scadenza Km"] ? Number(r["Scadenza Km"]) : null,
        expiry_date: r["Scadenza Data"] ? String(r["Scadenza Data"]).split("T")[0] : null,
        db_id: r.db_id ? Number(r.db_id) : null,
        status: String(r.Stato || "Nuovo"),
      }))

    if (fuelRows.length === 0 && maintRows.length === 0) {
      toast.warning("Nessuna riga valida da importare nel database.")
      return
    }

    try {
      const res = await commitMutation.mutateAsync({
        fuel_rows: fuelRows,
        maintenance_rows: maintRows,
      })

      toast.success(
        res.message || `Importati ${res.fuel_inserted + res.maintenance_inserted} record!`
      )
      resetStaging()
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Errore durante il salvataggio a database"
      toast.error(msg)
    }
  }

  const renderStatusBadge = (statusStr: string) => {
    const s = (statusStr || "Nuovo").toLowerCase()
    if (s === "nuovo" || s === "ok") {
      return (
        <Badge variant="outline" className="border-emerald-500/40 text-emerald-400 bg-emerald-500/10 text-[10px]">
          Nuovo
        </Badge>
      )
    }
    if (s === "modifica") {
      return (
        <Badge variant="outline" className="border-sky-500/40 text-sky-400 bg-sky-500/10 text-[10px]">
          Modifica
        </Badge>
      )
    }
    if (s === "warning") {
      return (
        <Badge variant="outline" className="border-amber-500/40 text-amber-400 bg-amber-500/10 text-[10px]">
          Warning
        </Badge>
      )
    }
    if (s === "invariato") {
      return (
        <Badge variant="outline" className="border-slate-500/40 text-slate-400 bg-slate-500/10 text-[10px]">
          Invariato
        </Badge>
      )
    }
    return (
      <Badge variant="outline" className="border-rose-500/40 text-rose-400 bg-rose-500/10 text-[10px]">
        Errore
      </Badge>
    )
  }

  // Conteggio aggregato per il banner di sintesi
  const totalNew =
    (previewData?.fuel_summary?.Nuovo || 0) +
    (previewData?.fuel_summary?.OK || 0) +
    (previewData?.maintenance_summary?.Nuovo || 0) +
    (previewData?.maintenance_summary?.OK || 0)
  const totalMod =
    (previewData?.fuel_summary?.Modifica || 0) +
    (previewData?.maintenance_summary?.Modifica || 0)
  const totalInv =
    (previewData?.fuel_summary?.Invariato || 0) +
    (previewData?.maintenance_summary?.Invariato || 0)
  const totalWarn =
    (previewData?.fuel_summary?.Warning || 0) +
    (previewData?.maintenance_summary?.Warning || 0)
  const totalErr =
    (previewData?.fuel_summary?.Errore || 0) +
    (previewData?.maintenance_summary?.Errore || 0)

  return (
    <Card className="border-border/60 shadow-sm overflow-hidden">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-sky-500/10 text-sky-400">
              <Upload className="h-5 w-5" />
            </div>
            <div>
              <CardTitle className="text-base font-bold">
                Staging Importazione Massiva Dati
              </CardTitle>
              <CardDescription className="text-xs">
                Carica file Excel (.xlsx multi-foglio) o CSV per visualizzare l&apos;anteprima
                e convalidare le righe prima dell&apos;inserimento a database.
              </CardDescription>
            </div>
          </div>

          {previewData && (
            <Button
              variant="outline"
              size="sm"
              onClick={resetStaging}
              className="gap-1.5 text-xs text-muted-foreground hover:text-foreground"
            >
              <RefreshCw className="h-3.5 w-3.5" />
              <span>Nuovo Caricamento</span>
            </Button>
          )}
        </div>
      </CardHeader>

      <CardContent className="space-y-6 pt-0">
        {/* Upload Zone when no preview loaded */}
        {!previewData && (
          <div
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-2xl p-8 text-center transition-all cursor-pointer flex flex-col items-center justify-center gap-3 ${
              dragActive
                ? "border-sky-500 bg-sky-500/10 scale-[0.99]"
                : "border-border/60 hover:border-sky-500/50 hover:bg-muted/10 bg-muted/5"
            }`}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".xlsx,.csv"
              className="hidden"
              onChange={(e) => {
                if (e.target.files?.[0]) handleFile(e.target.files[0])
              }}
            />

            <div className="p-4 rounded-2xl bg-sky-500/10 text-sky-400">
              {previewMutation.isPending ? (
                <Loader2 className="h-8 w-8 animate-spin" />
              ) : (
                <FileSpreadsheet className="h-8 w-8" />
              )}
            </div>

            <div className="space-y-1 text-center">
              <p className="text-sm font-semibold text-foreground">
                {previewMutation.isPending
                  ? "Analisi file in corso..."
                  : "Trascina qui il file Excel o CSV, oppure clicca per sfogliare"}
              </p>
              <p className="text-xs text-muted-foreground">
                Supporta il formato ufficiale di esportazione FuelPyTracker e fogli personalizzati con colonne standard.
              </p>
            </div>

            <div className="flex flex-wrap items-center justify-center gap-2 pt-1">
              <Badge variant="outline" className="text-[10px] border-border/80">
                .XLSX Multi-Foglio (Consigliato)
              </Badge>
              <Badge variant="outline" className="text-[10px] border-border/80">
                .CSV Singolo
              </Badge>
              <Badge variant="outline" className="text-[10px] border-border/80 text-sky-400">
                Sniffing Automatico Fogli
              </Badge>
            </div>
          </div>
        )}

        {/* Global Error Banner */}
        {previewData?.global_error && (
          <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-start gap-3">
            <XCircle className="h-5 w-5 shrink-0 text-rose-400 mt-0.5" />
            <div className="space-y-1">
              <span className="font-bold block">Errore nel file caricato</span>
              <p className="leading-relaxed">{previewData.global_error}</p>
            </div>
          </div>
        )}

        {/* Staging Preview Section */}
        {previewData && !previewData.global_error && (
          <div className="space-y-4">
            {/* KPI Summary Strip */}
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
              <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-between">
                <div>
                  <span className="text-[10px] uppercase font-bold text-emerald-400 block">
                    Nuovi Record
                  </span>
                  <span className="text-lg font-mono font-bold text-emerald-300">{totalNew}</span>
                </div>
                <CheckCircle2 className="h-4 w-4 text-emerald-400/80" />
              </div>

              <div className="p-3 rounded-xl bg-sky-500/10 border border-sky-500/20 flex items-center justify-between">
                <div>
                  <span className="text-[10px] uppercase font-bold text-sky-400 block">
                    Modifiche
                  </span>
                  <span className="text-lg font-mono font-bold text-sky-300">{totalMod}</span>
                </div>
                <Database className="h-4 w-4 text-sky-400/80" />
              </div>

              <div className="p-3 rounded-xl bg-slate-500/10 border border-slate-500/20 flex items-center justify-between">
                <div>
                  <span className="text-[10px] uppercase font-bold text-slate-400 block">
                    Invariati
                  </span>
                  <span className="text-lg font-mono font-bold text-slate-300">{totalInv}</span>
                </div>
                <RefreshCw className="h-4 w-4 text-slate-400/80" />
              </div>

              <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-between">
                <div>
                  <span className="text-[10px] uppercase font-bold text-amber-400 block">
                    Avvisi
                  </span>
                  <span className="text-lg font-mono font-bold text-amber-300">{totalWarn}</span>
                </div>
                <AlertTriangle className="h-4 w-4 text-amber-400/80" />
              </div>

              <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-between">
                <div>
                  <span className="text-[10px] uppercase font-bold text-rose-400 block">
                    Errori (Bloccanti)
                  </span>
                  <span className="text-lg font-mono font-bold text-rose-300">{totalErr}</span>
                </div>
                <XCircle className="h-4 w-4 text-rose-400/80" />
              </div>
            </div>

            {/* Note bar */}
            <div className="p-3 rounded-xl bg-muted/30 border border-border/50 flex items-center gap-2.5 text-xs text-muted-foreground">
              <Info className="h-4 w-4 shrink-0 text-sky-400" />
              <span>
                File analizzato: <strong className="text-foreground">{selectedFile?.name}</strong>.
                Controlla l&apos;anteprima delle righe prima di confermare il salvataggio nel database.
              </span>
            </div>

            {/* Tabs for Fuel and Maintenance */}
            <Tabs defaultValue="fuel" className="w-full">
              <TabsList className="grid grid-cols-2 w-full max-w-sm mb-3">
                <TabsTrigger value="fuel" className="gap-2 text-xs">
                  <Fuel className="h-3.5 w-3.5 text-emerald-400" />
                  <span>Rifornimenti ({previewData.fuel_rows?.length || 0})</span>
                </TabsTrigger>
                <TabsTrigger value="maintenance" className="gap-2 text-xs">
                  <Wrench className="h-3.5 w-3.5 text-amber-400" />
                  <span>Manutenzioni ({previewData.maintenance_rows?.length || 0})</span>
                </TabsTrigger>
              </TabsList>

              {/* Fuel Table */}
              <TabsContent value="fuel" className="border rounded-xl overflow-hidden bg-card/40">
                {previewData.fuel_rows?.length > 0 ? (
                  <div className="max-h-[360px] overflow-y-auto">
                    <Table>
                      <TableHeader className="sticky top-0 bg-card z-10">
                        <TableRow>
                          <TableHead className="w-24 text-xs">Stato</TableHead>
                          <TableHead className="text-xs">Data</TableHead>
                          <TableHead className="text-xs text-right">KM</TableHead>
                          <TableHead className="text-xs text-right">Litri</TableHead>
                          <TableHead className="text-xs text-right">Prezzo/L</TableHead>
                          <TableHead className="text-xs text-right">Spesa</TableHead>
                          <TableHead className="text-xs text-center">Pieno</TableHead>
                          <TableHead className="text-xs min-w-[220px]">Esito Validazione & Motivo</TableHead>
                          <TableHead className="w-16 text-center text-xs">Azioni</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {previewData.fuel_rows.map((row, idx) => {
                          const isErr = String(row.Stato || "").toLowerCase() === "errore"
                          const isWarn = String(row.Stato || "").toLowerCase() === "warning"
                          const isMod = String(row.Stato || "").toLowerCase() === "modifica"
                          const isInv = String(row.Stato || "").toLowerCase() === "invariato"
                          return (
                            <TableRow
                              key={idx}
                              className={`text-xs transition-colors ${
                                isErr ? "bg-rose-500/5 hover:bg-rose-500/10" : ""
                              }`}
                            >
                              <TableCell>{renderStatusBadge(String(row.Stato || ""))}</TableCell>
                              <TableCell className="font-mono text-muted-foreground">
                                {String(row.Data || "").split("T")[0]}
                              </TableCell>
                              <TableCell className="text-right font-mono font-medium">
                                {Number(row.Km || 0).toLocaleString("it-IT")}
                              </TableCell>
                              <TableCell className="text-right font-mono">
                                {Number(row.Litri || 0).toFixed(2)} L
                              </TableCell>
                              <TableCell className="text-right font-mono">
                                {Number(row.Prezzo || 0).toFixed(3)} €
                              </TableCell>
                              <TableCell className="text-right font-mono font-bold text-emerald-400">
                                {Number(row.Costo || 0).toFixed(2)} €
                              </TableCell>
                              <TableCell className="text-center">
                                {row.Pieno ? (
                                  <span className="text-[10px] text-emerald-400 font-semibold">Sì</span>
                                ) : (
                                  <span className="text-[10px] text-amber-400 font-semibold">Parziale</span>
                                )}
                              </TableCell>
                              <TableCell className="text-xs min-w-[220px]">
                                {isErr ? (
                                  <div
                                    className="flex items-center gap-1.5 text-rose-400 font-semibold"
                                    title={String(row.Note || "")}
                                  >
                                    <AlertTriangle className="h-3.5 w-3.5 shrink-0 text-rose-400" />
                                    <span className="break-words line-clamp-2">
                                      {String(row.Note || "Errore di validazione")}
                                    </span>
                                  </div>
                                ) : isWarn ? (
                                  <div
                                    className="flex items-center gap-1.5 text-amber-400 font-medium"
                                    title={String(row.Note || "")}
                                  >
                                    <AlertTriangle className="h-3.5 w-3.5 shrink-0 text-amber-400" />
                                    <span className="break-words line-clamp-2">
                                      {String(row.Note || "Avviso di congruenza")}
                                    </span>
                                  </div>
                                ) : isMod ? (
                                  <div
                                    className="flex items-center gap-1.5 text-sky-400 font-medium"
                                    title={String(row.Note || "")}
                                  >
                                    <Database className="h-3.5 w-3.5 shrink-0 text-sky-400" />
                                    <span className="break-words line-clamp-2">
                                      {String(row.Note).replace(/^(Cambia|Aggiornamenti):\s*/i, "Variazione: ")}
                                    </span>
                                  </div>
                                ) : isInv ? (
                                  <div
                                    className="flex items-center gap-1.5 text-slate-400 text-[11px]"
                                    title="Record identico già presente nel database (verrà ignorato)"
                                  >
                                    <Check className="h-3.5 w-3.5 shrink-0 text-slate-400" />
                                    <span>Identico allo storico DB</span>
                                  </div>
                                ) : row.Note ? (
                                  <span
                                    className="text-muted-foreground break-words line-clamp-2"
                                    title={String(row.Note)}
                                  >
                                    {String(row.Note)}
                                  </span>
                                ) : (
                                  <span className="text-muted-foreground/50">—</span>
                                )}
                              </TableCell>
                              <TableCell className="text-center">
                                <Button
                                  type="button"
                                  variant="ghost"
                                  size="icon"
                                  className="h-7 w-7 text-muted-foreground hover:text-sky-400 hover:bg-sky-500/10"
                                  title="Rettifica riga"
                                  onClick={() =>
                                    handleOpenEdit(
                                      row as unknown as Record<string, unknown>,
                                      idx,
                                      "fuel"
                                    )
                                  }
                                >
                                  <Edit3 className="h-3.5 w-3.5" />
                                </Button>
                              </TableCell>
                            </TableRow>
                          )
                        })}
                      </TableBody>
                    </Table>
                  </div>
                ) : (
                  <div className="p-8 text-center text-xs text-muted-foreground">
                    Nessun dato di rifornimento rilevato nel file caricato.
                  </div>
                )}
              </TabsContent>

              {/* Maintenance Table */}
              <TabsContent value="maintenance" className="border rounded-xl overflow-hidden bg-card/40">
                {previewData.maintenance_rows?.length > 0 ? (
                  <div className="max-h-[360px] overflow-y-auto">
                    <Table>
                      <TableHeader className="sticky top-0 bg-card z-10">
                        <TableRow>
                          <TableHead className="w-24 text-xs">Stato</TableHead>
                          <TableHead className="text-xs">Data</TableHead>
                          <TableHead className="text-xs text-right">KM</TableHead>
                          <TableHead className="text-xs">Tipologia</TableHead>
                          <TableHead className="text-xs text-right">Spesa</TableHead>
                          <TableHead className="text-xs">Descrizione</TableHead>
                          <TableHead className="text-xs min-w-[220px]">Esito Validazione & Motivo</TableHead>
                          <TableHead className="text-xs">Scadenza Impostata</TableHead>
                          <TableHead className="w-16 text-center text-xs">Azioni</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {previewData.maintenance_rows.map((row, idx) => {
                          const isErr = String(row.Stato || "").toLowerCase() === "errore"
                          const isWarn = String(row.Stato || "").toLowerCase() === "warning"
                          const isMod = String(row.Stato || "").toLowerCase() === "modifica"
                          const isInv = String(row.Stato || "").toLowerCase() === "invariato"
                          return (
                            <TableRow
                              key={idx}
                              className={`text-xs transition-colors ${
                                isErr ? "bg-rose-500/5 hover:bg-rose-500/10" : ""
                              }`}
                            >
                              <TableCell>{renderStatusBadge(String(row.Stato || ""))}</TableCell>
                              <TableCell className="font-mono text-muted-foreground">
                                {String(row.Data || "").split("T")[0]}
                              </TableCell>
                              <TableCell className="text-right font-mono font-medium">
                                {Number(row.Km || 0).toLocaleString("it-IT")}
                              </TableCell>
                              <TableCell>
                                <Badge variant="outline" className="text-[10px]">
                                  {String(row.Tipo || "Altro")}
                                </Badge>
                              </TableCell>
                              <TableCell className="text-right font-mono font-bold text-amber-400">
                                {Number(row.Costo || 0).toFixed(2)} €
                              </TableCell>
                              <TableCell
                                className={`truncate max-w-[200px] ${
                                  isErr ? "text-rose-400 font-medium" : "text-muted-foreground"
                                }`}
                              >
                                {String(row.Descrizione || "—")}
                              </TableCell>
                              <TableCell className="text-xs min-w-[220px]">
                                {isErr ? (
                                  <div
                                    className="flex items-center gap-1.5 text-rose-400 font-semibold"
                                    title={String(row.Note || "")}
                                  >
                                    <AlertTriangle className="h-3.5 w-3.5 shrink-0 text-rose-400" />
                                    <span className="break-words line-clamp-2">
                                      {String(row.Note || "Errore di validazione")}
                                    </span>
                                  </div>
                                ) : isWarn ? (
                                  <div
                                    className="flex items-center gap-1.5 text-amber-400 font-medium"
                                    title={String(row.Note || "")}
                                  >
                                    <AlertTriangle className="h-3.5 w-3.5 shrink-0 text-amber-400" />
                                    <span className="break-words line-clamp-2">
                                      {String(row.Note || "Avviso di congruenza")}
                                    </span>
                                  </div>
                                ) : isMod ? (
                                  <div
                                    className="flex items-center gap-1.5 text-sky-400 font-medium"
                                    title={String(row.Note || "")}
                                  >
                                    <Database className="h-3.5 w-3.5 shrink-0 text-sky-400" />
                                    <span className="break-words line-clamp-2">
                                      {String(row.Note).replace(/^(Cambia|Aggiornamenti):\s*/i, "Variazione: ")}
                                    </span>
                                  </div>
                                ) : isInv ? (
                                  <div
                                    className="flex items-center gap-1.5 text-slate-400 text-[11px]"
                                    title="Record identico già presente nel database (verrà ignorato)"
                                  >
                                    <Check className="h-3.5 w-3.5 shrink-0 text-slate-400" />
                                    <span>Identico allo storico DB</span>
                                  </div>
                                ) : row.Note ? (
                                  <span
                                    className="text-muted-foreground break-words line-clamp-2"
                                    title={String(row.Note)}
                                  >
                                    {String(row.Note)}
                                  </span>
                                ) : (
                                  <span className="text-muted-foreground/50">—</span>
                                )}
                              </TableCell>
                              <TableCell className="text-muted-foreground font-mono text-[11px]">
                                {row["Scadenza Km"]
                                  ? `${Number(row["Scadenza Km"]).toLocaleString("it-IT")} km`
                                  : row["Scadenza Data"]
                                    ? String(row["Scadenza Data"]).split("T")[0]
                                    : "—"}
                              </TableCell>
                              <TableCell className="text-center">
                                <Button
                                  type="button"
                                  variant="ghost"
                                  size="icon"
                                  className="h-7 w-7 text-muted-foreground hover:text-amber-400 hover:bg-amber-500/10"
                                  title="Rettifica riga"
                                  onClick={() =>
                                    handleOpenEdit(
                                      row as unknown as Record<string, unknown>,
                                      idx,
                                      "maintenance"
                                    )
                                  }
                                >
                                  <Edit3 className="h-3.5 w-3.5" />
                                </Button>
                              </TableCell>
                            </TableRow>
                          )
                        })}
                      </TableBody>
                    </Table>
                  </div>
                ) : (
                  <div className="p-8 text-center text-xs text-muted-foreground">
                    Nessun intervento di manutenzione rilevato nel file caricato.
                  </div>
                )}
              </TabsContent>
            </Tabs>

            {/* Strict Safety Gatekeeper Alert if any errors exist */}
            {totalErr > 0 && (
              <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs space-y-2.5">
                <div className="flex items-center gap-2.5 font-bold">
                  <AlertTriangle className="h-4 w-4 text-rose-400 shrink-0" />
                  <span>
                    Blocco di Sicurezza Attivo ({totalErr} {totalErr === 1 ? "anomalia critica" : "anomalie critiche"} da correggere):
                  </span>
                </div>
                <p className="pl-6 text-rose-300/90 leading-relaxed text-[11px]">
                  Il database richiede dati coerenti prima del salvataggio. Di seguito il dettaglio delle anomalie rilevate dal motore di validazione:
                </p>
                <ul className="pl-6 space-y-1 list-disc list-inside font-mono text-[11px] text-rose-200">
                  {previewData.fuel_rows
                    ?.filter((r) => String(r.Stato || "").toLowerCase() === "errore")
                    .map((r, i) => (
                      <li key={`err-f-${i}`}>
                        <strong>Rifornimento ({String(r.Data || "").split("T")[0]}, {Number(r.Km || 0).toLocaleString("it-IT")} km):</strong>{" "}
                        {String(r.Note || "Valori incongruenti o fuori scala")}
                      </li>
                    ))}
                  {previewData.maintenance_rows
                    ?.filter((r) => String(r.Stato || "").toLowerCase() === "errore")
                    .map((r, i) => (
                      <li key={`err-m-${i}`}>
                        <strong>Manutenzione ({String(r.Data || "").split("T")[0]}, {String(r.Tipo || "Altro")}):</strong>{" "}
                        {String(r.Note || "Valori incongruenti o fuori scala")}
                      </li>
                    ))}
                </ul>
                <p className="pl-6 text-[11px] text-rose-300/80 pt-0.5">
                  Clicca sull&apos;icona <Edit3 className="inline h-3.5 w-3.5 mx-0.5 text-sky-400" /> a destra della riga per rettificare i dati errati.
                </p>
              </div>
            )}

            {/* Bottom Actions Confirmation Strip */}
            <div className="p-4 rounded-xl bg-card border border-border/70 flex flex-col sm:flex-row items-center justify-between gap-3 shadow-sm">
              <div className="text-xs text-muted-foreground">
                <span>
                  Righe pronte per l&apos;importazione:{" "}
                  <strong className="text-foreground">{totalNew + totalMod + totalWarn}</strong>
                  {totalErr > 0 ? (
                    <span className="text-rose-400 ml-1 font-semibold">
                      ({totalErr} righe con errori: correggile prima di poter salvare)
                    </span>
                  ) : (
                    <span className="text-emerald-400 ml-1 font-medium">
                      (Tutti i record sono validi e conformi)
                    </span>
                  )}
                </span>
              </div>

              <div className="flex items-center gap-2 w-full sm:w-auto">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={resetStaging}
                  disabled={commitMutation.isPending || revalidateMutation.isPending}
                  className="w-full sm:w-auto"
                >
                  Annulla
                </Button>

                <Button
                  type="button"
                  variant="emerald"
                  size="sm"
                  onClick={handleCommit}
                  disabled={
                    commitMutation.isPending ||
                    revalidateMutation.isPending ||
                    totalErr > 0 ||
                    totalNew + totalMod + totalWarn === 0
                  }
                  className="w-full sm:w-auto gap-2"
                >
                  {commitMutation.isPending ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Salvataggio in corso...
                    </>
                  ) : (
                    <>
                      <Check className="h-4 w-4" />
                      Conferma ed Importa nel Database
                    </>
                  )}
                </Button>
              </div>
            </div>
          </div>
        )}
      </CardContent>

      <ImportRowEditModal
        open={editModalOpen}
        onOpenChange={setEditModalOpen}
        rowIndex={editRowIndex}
        type={editRowType}
        rowData={editRowData}
        onSave={handleRowEditSave}
      />
    </Card>
  )
}

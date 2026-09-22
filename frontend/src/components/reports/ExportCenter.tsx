import { useState } from "react"
import {
  FileSpreadsheet,
  FileText,
  Download,
  Loader2,
  Calendar,
  Fuel,
  Wrench,
  Sparkles,
  FileCheck,
} from "lucide-react"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { PdfBookletModal } from "./PdfBookletModal"
import { useExportStats, useDownloadExcel, useDownloadTemplate } from "@/hooks/useReports"
import { toast } from "sonner"

export function ExportCenter() {
  const { data: stats, isLoading } = useExportStats()
  const downloadExcelMutation = useDownloadExcel()
  const downloadTemplateMutation = useDownloadTemplate()
  const [pdfModalOpen, setPdfModalOpen] = useState(false)

  const handleDownloadExcel = async () => {
    try {
      await downloadExcelMutation.mutateAsync()
      toast.success("Archivio Excel scaricato con successo!")
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Errore durante il download del file Excel"
      toast.error(msg)
    }
  }

  const handleDownloadTemplate = async () => {
    try {
      await downloadTemplateMutation.mutateAsync()
      toast.success("Modello Excel scaricato con successo!")
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Errore durante il download del modello"
      toast.error(msg)
    }
  }

  return (
    <div className="space-y-6">
      {/* Overview Stats Header Strip */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card className="border-border/60 bg-card/60 backdrop-blur-sm shadow-sm">
          <CardContent className="p-4 flex items-center justify-between">
            <div className="space-y-0.5">
              <span className="text-xs text-muted-foreground font-medium">Rifornimenti Archiviati</span>
              {isLoading ? (
                <Skeleton className="h-6 w-16" />
              ) : (
                <div className="text-xl font-extrabold font-mono text-emerald-400">
                  {stats?.refuelings_count || 0}
                  <span className="text-xs font-normal text-muted-foreground ml-1">record</span>
                </div>
              )}
            </div>
            <div className="p-2.5 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <Fuel className="h-5 w-5" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-border/60 bg-card/60 backdrop-blur-sm shadow-sm">
          <CardContent className="p-4 flex items-center justify-between">
            <div className="space-y-0.5">
              <span className="text-xs text-muted-foreground font-medium">Interventi Officina</span>
              {isLoading ? (
                <Skeleton className="h-6 w-16" />
              ) : (
                <div className="text-xl font-extrabold font-mono text-amber-400">
                  {stats?.maintenances_count || 0}
                  <span className="text-xs font-normal text-muted-foreground ml-1">tagliandi</span>
                </div>
              )}
            </div>
            <div className="p-2.5 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/20">
              <Wrench className="h-5 w-5" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-border/60 bg-card/60 backdrop-blur-sm shadow-sm">
          <CardContent className="p-4 flex items-center justify-between">
            <div className="space-y-0.5">
              <span className="text-xs text-muted-foreground font-medium">Copertura Storica</span>
              {isLoading ? (
                <Skeleton className="h-6 w-20" />
              ) : (
                <div className="text-xl font-extrabold font-mono text-sky-400">
                  {stats?.years_available?.length || 0}
                  <span className="text-xs font-normal text-muted-foreground ml-1">
                    {stats?.years_available?.length === 1 ? "anno" : "anni"}
                  </span>
                </div>
              )}
            </div>
            <div className="p-2.5 rounded-xl bg-sky-500/10 text-sky-400 border border-sky-500/20">
              <Calendar className="h-5 w-5" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Export Documents Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Card 1: Full Excel Backup */}
        <Card className="border-border/60 hover:border-emerald-500/40 transition-all shadow-sm flex flex-col justify-between">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
                <FileSpreadsheet className="h-5 w-5" />
              </div>
              <Badge variant="outline" className="border-emerald-500/30 text-emerald-400 text-[10px]">
                Multi-Sheet .xlsx
              </Badge>
            </div>
            <CardTitle className="text-base font-bold pt-2">Backup Completo Excel</CardTitle>
            <CardDescription className="text-xs">
              Esporta il database completo con fogli separati per Rifornimenti e Manutenzioni,
              completo di formule e stili formattati.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 pt-0">
            <div className="p-3 rounded-lg bg-muted/20 border border-border/40 text-xs text-muted-foreground space-y-1">
              <div className="flex justify-between">
                <span>Foglio 1:</span>
                <span className="font-semibold text-foreground">Rifornimenti Full-to-Full</span>
              </div>
              <div className="flex justify-between">
                <span>Foglio 2:</span>
                <span className="font-semibold text-foreground">Manutenzioni & Scadenze</span>
              </div>
            </div>
            <Button
              variant="emerald"
              className="w-full gap-2 text-xs"
              onClick={handleDownloadExcel}
              disabled={downloadExcelMutation.isPending || (!stats?.refuelings_count && !stats?.maintenances_count)}
            >
              {downloadExcelMutation.isPending ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Generazione archivio...
                </>
              ) : (
                <>
                  <Download className="h-4 w-4" />
                  Scarica Archivio Excel
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Card 2: Digital PDF Service Booklet */}
        <Card className="border-border/60 hover:border-rose-500/40 transition-all shadow-sm flex flex-col justify-between">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="p-2 rounded-lg bg-rose-500/10 text-rose-400">
                <FileText className="h-5 w-5" />
              </div>
              <Badge variant="outline" className="border-rose-500/30 text-rose-400 text-[10px]">
                Certificato PDF
              </Badge>
            </div>
            <CardTitle className="text-base font-bold pt-2">Libretto Manutenzione Digitale</CardTitle>
            <CardDescription className="text-xs">
              Genera il documento stampabile con scheda tecnica, storico tagliandi, costi complessivi
              e timbro digitale anti-manomissione.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 pt-0">
            <div className="p-3 rounded-lg bg-muted/20 border border-border/40 text-xs text-muted-foreground space-y-1">
              <div className="flex justify-between">
                <span>Layout:</span>
                <span className="font-semibold text-foreground">A4 Formale con Logo</span>
              </div>
              <div className="flex justify-between">
                <span>Ideale per:</span>
                <span className="font-semibold text-foreground">Rivendita / Assicurazione</span>
              </div>
            </div>
            <Button
              variant="outline"
              className="w-full gap-2 border-rose-500/30 text-rose-400 hover:bg-rose-500/10 hover:text-rose-300 text-xs"
              onClick={() => setPdfModalOpen(true)}
            >
              <Sparkles className="h-4 w-4" />
              Compila & Scarica Libretto
            </Button>
          </CardContent>
        </Card>

        {/* Card 3: Blank Excel Template */}
        <Card className="border-border/60 hover:border-sky-500/40 transition-all shadow-sm flex flex-col justify-between">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="p-2 rounded-lg bg-sky-500/10 text-sky-400">
                <FileCheck className="h-5 w-5" />
              </div>
              <Badge variant="outline" className="border-sky-500/30 text-sky-400 text-[10px]">
                Modello Pre-Compilato
              </Badge>
            </div>
            <CardTitle className="text-base font-bold pt-2">Modello Excel Vuoto</CardTitle>
            <CardDescription className="text-xs">
              Scarica il template con le intestazioni standard ufficiali per compilare offline i dati
              e importarli successivamente in FuelPyTracker.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 pt-0">
            <div className="p-3 rounded-lg bg-muted/20 border border-border/40 text-xs text-muted-foreground space-y-1">
              <div className="flex justify-between">
                <span>Formato:</span>
                <span className="font-semibold text-foreground">.xlsx Ufficiale V2</span>
              </div>
              <div className="flex justify-between">
                <span>Compatibilità:</span>
                <span className="font-semibold text-foreground">Excel, LibreOffice, Sheets</span>
              </div>
            </div>
            <Button
              variant="outline"
              className="w-full gap-2 border-sky-500/30 text-sky-400 hover:bg-sky-500/10 hover:text-sky-300 text-xs"
              onClick={handleDownloadTemplate}
              disabled={downloadTemplateMutation.isPending}
            >
              {downloadTemplateMutation.isPending ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Download in corso...
                </>
              ) : (
                <>
                  <Download className="h-4 w-4" />
                  Scarica Modello Vuoto
                </>
              )}
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Modal Libretto PDF */}
      <PdfBookletModal
        open={pdfModalOpen}
        onOpenChange={setPdfModalOpen}
        yearsAvailable={stats?.years_available || []}
      />
    </div>
  )
}

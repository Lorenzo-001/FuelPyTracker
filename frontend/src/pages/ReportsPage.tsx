import { BarChart3, Download, Upload, FileSpreadsheet, FileJson } from "lucide-react"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"

export default function ReportsPage() {
  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-extrabold tracking-tight flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-sky-500/10 text-sky-400">
              <BarChart3 className="h-5 w-5" />
            </div>
            Report & Esportazioni
          </h2>
          <p className="text-sm text-muted-foreground mt-1">
            Genera resoconti analitici completi ed esporta i dati nei formati standard.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" className="gap-1.5">
            <FileSpreadsheet className="h-4 w-4 text-emerald-400" />
            <span>Esporta CSV</span>
          </Button>
          <Button variant="outline" size="sm" className="gap-1.5">
            <FileJson className="h-4 w-4 text-sky-400" />
            <span>Esporta JSON</span>
          </Button>
        </div>
      </div>

      {/* Export / Import Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Esportazione Dati Flotta</CardTitle>
              <Download className="h-4 w-4 text-muted-foreground" />
            </div>
            <CardDescription>
              Scarica il database completo o filtra per veicolo e intervallo date.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="p-4 rounded-lg bg-muted/20 border border-border/60 space-y-2">
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>Rifornimenti totali da esportare</span>
                <span className="font-semibold text-foreground">42 record</span>
              </div>
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>Interventi di manutenzione</span>
                <span className="font-semibold text-foreground">8 record</span>
              </div>
            </div>
            <Button variant="emerald" className="w-full">
              Scarica Pacchetto Completo (ZIP/CSV)
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Importazione Dati Esterni</CardTitle>
              <Upload className="h-4 w-4 text-muted-foreground" />
            </div>
            <CardDescription>
              Importa dati da file CSV precedenti o da altre applicazioni di tracking.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="border border-dashed border-border/80 rounded-xl p-6 text-center space-y-2">
              <Upload className="h-8 w-8 mx-auto text-muted-foreground" />
              <p className="text-xs text-muted-foreground">
                Trascina qui il file CSV o clicca per sfogliare
              </p>
              <Badge variant="outline" className="text-[10px]">
                Supporta CSV FuelPyTracker v1.0
              </Badge>
            </div>
            <Button variant="outline" className="w-full" disabled>
              Verifica File & Anteprima
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Reports Analysis Skeleton */}
      <Card>
        <CardHeader>
          <CardTitle>Ripartizione Costi Annuale per Categoria</CardTitle>
          <CardDescription>
            Grafici aggregati con Recharts (Fase 4).
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          <Skeleton className="h-48 w-full rounded-xl" />
        </CardContent>
      </Card>
    </div>
  )
}

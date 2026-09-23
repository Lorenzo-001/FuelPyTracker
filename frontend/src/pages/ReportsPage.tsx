import { useState } from "react"
import { BarChart3, Download, Upload } from "lucide-react"
import { ExportCenter } from "@/components/reports/ExportCenter"
import { ImportStagingZone } from "@/components/reports/ImportStagingZone"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"

export default function ReportsPage() {
  const [activeTab, setActiveTab] = useState<string>("export")

  return (
    <div className="space-y-6 pb-12">
      {/* Page Title & Context Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-extrabold tracking-tight flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-sky-500/10 text-sky-400 border border-sky-500/20">
              <BarChart3 className="h-5 w-5" />
            </div>
            Report, Esportazioni & Importazione
          </h2>
          <p className="text-sm text-muted-foreground mt-1">
            Scarica l&apos;archivio dati, compila il libretto PDF ufficiale o carica massivamente record tramite file Excel e CSV.
          </p>
        </div>
      </div>

      {/* Main Mode Tabs: Esportazioni vs Importazione Staging */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full space-y-6">
        <TabsList className="grid grid-cols-2 w-full max-w-md h-10 p-1 bg-muted/40 border border-border/50">
          <TabsTrigger value="export" className="gap-2 text-xs font-semibold">
            <Download className="h-4 w-4 text-emerald-400" />
            <span>Download & Documenti</span>
          </TabsTrigger>
          <TabsTrigger value="import" className="gap-2 text-xs font-semibold">
            <Upload className="h-4 w-4 text-sky-400" />
            <span>Importazione & Verifica</span>
          </TabsTrigger>
        </TabsList>

        {/* Tab 1: Export Center */}
        <TabsContent value="export" className="space-y-6 mt-0">
          <ExportCenter />
        </TabsContent>

        {/* Tab 2: Staging Import */}
        <TabsContent value="import" className="space-y-6 mt-0">
          <ImportStagingZone />
        </TabsContent>
      </Tabs>
    </div>
  )
}

import { Settings, Shield, Tag, User, AlertCircle, RefreshCw } from "lucide-react"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { useSettings } from "@/hooks/useSettings"
import { FuelThresholdsCard } from "@/components/settings/FuelThresholdsCard"
import { CategoryManagerCard } from "@/components/settings/CategoryManagerCard"
import { OcrPreferencesCard } from "@/components/settings/OcrPreferencesCard"
import { UserProfileCard } from "@/components/settings/UserProfileCard"
import { ApiDiagnosticsCard } from "@/components/settings/ApiDiagnosticsCard"

export default function SettingsPage() {
  const { data: settings, isLoading, isError, error, refetch } = useSettings()

  return (
    <div className="space-y-6 max-w-5xl mx-auto pb-10">
      {/* Header Pagina */}
      <div>
        <h2 className="text-2xl font-extrabold tracking-tight flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-emerald-500/10 text-emerald-400">
            <Settings className="h-5 w-5" />
          </div>
          Impostazioni & Preferenze Sistema
        </h2>
        <p className="text-sm text-muted-foreground mt-1">
          Configura i parametri di sicurezza per il carburante, personalizza le categorie di officina e promemoria, e gestisci la tua sessione.
        </p>
      </div>

      {/* Stato Caricamento */}
      {isLoading ? (
        <div className="space-y-4">
          <Skeleton className="h-10 w-72 rounded-lg" />
          <Skeleton className="h-[380px] w-full rounded-2xl" />
        </div>
      ) : isError || !settings ? (
        <div className="p-6 rounded-2xl bg-destructive/10 border border-destructive/30 text-destructive space-y-3">
          <div className="flex items-center gap-2 font-bold text-base">
            <AlertCircle className="h-5 w-5" />
            <span>Impossibile caricare le impostazioni utente</span>
          </div>
          <p className="text-xs text-muted-foreground">
            {error instanceof Error ? error.message : "Errore sconosciuto di comunicazione con il server."}
          </p>
          <Button
            variant="outline"
            size="sm"
            onClick={() => refetch()}
            className="gap-2 text-xs"
          >
            <RefreshCw className="h-3.5 w-3.5" />
            <span>Riprova</span>
          </Button>
        </div>
      ) : (
        /* Tabs di Navigazione */
        <Tabs defaultValue="thresholds" className="space-y-6">
          <TabsList className="bg-muted/40 p-1 border border-border/60 rounded-xl">
            <TabsTrigger value="thresholds" className="gap-2 text-xs font-semibold px-4 py-2">
              <Shield className="h-3.5 w-3.5 text-emerald-400" />
              <span>Soglie & Carburante</span>
            </TabsTrigger>
            <TabsTrigger value="categories" className="gap-2 text-xs font-semibold px-4 py-2">
              <Tag className="h-3.5 w-3.5 text-emerald-400" />
              <span>Categorie & Tag</span>
            </TabsTrigger>
            <TabsTrigger value="system" className="gap-2 text-xs font-semibold px-4 py-2">
              <User className="h-3.5 w-3.5 text-emerald-400" />
              <span>Profilo & Diagnostica</span>
            </TabsTrigger>
          </TabsList>

          {/* Tab 1: Soglie Carburante & OCR */}
          <TabsContent value="thresholds" className="space-y-6 outline-none">
            <FuelThresholdsCard settings={settings} />
            <OcrPreferencesCard settings={settings} />
          </TabsContent>

          {/* Tab 2: Gestione Categorie */}
          <TabsContent value="categories" className="space-y-6 outline-none">
            <CategoryManagerCard settings={settings} />
          </TabsContent>

          {/* Tab 3: Profilo & Diagnostica API */}
          <TabsContent value="system" className="grid grid-cols-1 md:grid-cols-2 gap-6 outline-none">
            <UserProfileCard />
            <ApiDiagnosticsCard />
          </TabsContent>
        </Tabs>
      )}
    </div>
  )
}

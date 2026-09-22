import { FileText, Sparkles, Check, Loader2 } from "lucide-react"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import type { AppSettingsResponse } from "@/types/settings"
import { useUpdateSettings } from "@/hooks/useSettings"

interface OcrPreferencesCardProps {
  settings: AppSettingsResponse
}

export function OcrPreferencesCard({ settings }: OcrPreferencesCardProps) {
  const updateMutation = useUpdateSettings()

  const handleToggleStation = () => {
    updateMutation.mutate({
      ocr_add_station_to_notes: !settings.ocr_add_station_to_notes,
    })
  }

  const handleToggleLiters = () => {
    updateMutation.mutate({
      ocr_add_liters_to_notes: !settings.ocr_add_liters_to_notes,
    })
  }

  return (
    <Card className="border-border/60 bg-card/60 backdrop-blur-sm shadow-md">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
              <FileText className="h-5 w-5" />
            </div>
            <div>
              <CardTitle className="text-base font-bold">
                Preferenze OCR & Acquisizione Scontrini
              </CardTitle>
              <CardDescription className="text-xs text-muted-foreground mt-0.5">
                Controlla la composizione automatica delle note generate dall&apos;analisi ottica dello scontrino.
              </CardDescription>
            </div>
          </div>
          <Badge variant="outline" className="text-xs gap-1 border-border/80">
            <Sparkles className="h-3 w-3 text-emerald-400" />
            Vision AI
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Toggle 1: Distributore nelle note */}
        <div className="flex items-center justify-between p-3.5 rounded-xl bg-muted/20 border border-border/50 hover:bg-muted/30 transition-colors">
          <div className="space-y-0.5 pr-4">
            <div className="text-xs font-semibold text-foreground">
              Inserisci stazione / distributore nelle note
            </div>
            <p className="text-[11px] text-muted-foreground">
              Aggiunge automaticamente il brand o l&apos;indirizzo rilevato dallo scontrino (es. <em>&quot;Distributore: Eni Station Roma&quot;</em>).
            </p>
          </div>

          <button
            type="button"
            role="switch"
            aria-checked={settings.ocr_add_station_to_notes}
            onClick={handleToggleStation}
            disabled={updateMutation.isPending}
            className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500 disabled:opacity-50 ${
              settings.ocr_add_station_to_notes ? "bg-emerald-500" : "bg-muted"
            }`}
          >
            <span
              className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow-lg ring-0 transition duration-200 ease-in-out flex items-center justify-center text-[10px] text-emerald-800 font-bold ${
                settings.ocr_add_station_to_notes ? "translate-x-5" : "translate-x-0"
              }`}
            >
              {updateMutation.isPending ? (
                <Loader2 className="h-3 w-3 animate-spin text-slate-700" />
              ) : settings.ocr_add_station_to_notes ? (
                <Check className="h-3 w-3 text-emerald-600" />
              ) : null}
            </span>
          </button>
        </div>

        {/* Toggle 2: Litri nelle note */}
        <div className="flex items-center justify-between p-3.5 rounded-xl bg-muted/20 border border-border/50 hover:bg-muted/30 transition-colors">
          <div className="space-y-0.5 pr-4">
            <div className="text-xs font-semibold text-foreground">
              Inserisci riepilogo litri erogati nelle note
            </div>
            <p className="text-[11px] text-muted-foreground">
              Salva nei dettagli del record il quantitativo estratto dal display (es. <em>&quot;Litri scontrino: 42.15 L&quot;</em>).
            </p>
          </div>

          <button
            type="button"
            role="switch"
            aria-checked={settings.ocr_add_liters_to_notes}
            onClick={handleToggleLiters}
            disabled={updateMutation.isPending}
            className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500 disabled:opacity-50 ${
              settings.ocr_add_liters_to_notes ? "bg-emerald-500" : "bg-muted"
            }`}
          >
            <span
              className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow-lg ring-0 transition duration-200 ease-in-out flex items-center justify-center text-[10px] text-emerald-800 font-bold ${
                settings.ocr_add_liters_to_notes ? "translate-x-5" : "translate-x-0"
              }`}
            >
              {updateMutation.isPending ? (
                <Loader2 className="h-3 w-3 animate-spin text-slate-700" />
              ) : settings.ocr_add_liters_to_notes ? (
                <Check className="h-3 w-3 text-emerald-600" />
              ) : null}
            </span>
          </button>
        </div>
      </CardContent>
    </Card>
  )
}

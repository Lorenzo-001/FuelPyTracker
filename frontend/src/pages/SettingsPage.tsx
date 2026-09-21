import { Settings, Save, Database, Shield } from "lucide-react"
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-extrabold tracking-tight flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-muted text-foreground">
            <Settings className="h-5 w-5" />
          </div>
          Impostazioni Sistema
        </h2>
        <p className="text-sm text-muted-foreground mt-1">
          Configurazione delle preferenze veicolo, valute, soglie di avviso e connessione API.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Veicolo Predefinito */}
        <Card>
          <CardHeader>
            <CardTitle>Profilo Veicolo Predefinito</CardTitle>
            <CardDescription>
              Configura i dati identificativi del veicolo primario tracciato.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-muted-foreground">Nome Modello</label>
              <Input defaultValue="BMW Serie 1 (118d)" />
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-muted-foreground">Targa</label>
              <Input defaultValue="AB 123 CD" />
            </div>
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-muted-foreground">Chilometraggio Iniziale</label>
              <Input type="number" defaultValue="114500" />
            </div>
          </CardContent>
          <CardFooter className="border-t border-border/60 pt-4 flex justify-end">
            <Button variant="emerald" size="sm" className="gap-1.5">
              <Save className="h-4 w-4" />
              Salva Veicolo
            </Button>
          </CardFooter>
        </Card>

        {/* Backend & Parametri Architetturali */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Infrastruttura & API Backend</CardTitle>
              <Database className="h-4 w-4 text-emerald-400" />
            </div>
            <CardDescription>
              Stato della sincronizzazione con il server FastAPI Python.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4 text-sm">
            <div className="p-3 rounded-lg bg-muted/20 border border-border/60 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Endpoint Base API:</span>
                <span className="font-mono text-xs text-foreground font-semibold">/api</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Reverse Proxy Vite:</span>
                <span className="font-mono text-xs text-emerald-400 font-semibold">http://127.0.0.1:8000</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Database SQLAlchemy:</span>
                <Badge variant="success" className="text-[10px]">Attivo (fuel_tracker.db)</Badge>
              </div>
            </div>

            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Shield className="h-4 w-4 text-emerald-400" />
              <span>Autenticazione JWT abilitata con refresh automatico.</span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

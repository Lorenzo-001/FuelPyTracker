import { Settings, Save, Database, Shield, Bell, Layers, PanelRight, Sparkles } from "lucide-react"
import { toast } from "sonner"
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"
import {
  Dialog,
  DialogTrigger,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
  DialogClose,
} from "@/components/ui/dialog"
import {
  Sheet,
  SheetTrigger,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
  SheetFooter,
  SheetClose,
} from "@/components/ui/sheet"

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

      {/* Showcase Tooling UI Fase 4.1 */}
      <Card className="border-emerald-500/30 bg-emerald-950/10 shadow-lg">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-emerald-400" />
              <CardTitle className="text-base text-emerald-300">
                Collaudo Kit UI & Componenti Interattivi (Step 4.1)
              </CardTitle>
            </div>
            <Badge variant="success" className="text-xs">
              Pronto per la Fase 4
            </Badge>
          </div>
          <CardDescription>
            Testa in tempo reale le notifiche Toast Sonner, le finestre Modali Dialog, il cassetto laterale Sheet e le schede Tabs.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-wrap items-center gap-3">
            {/* Test Toast Success */}
            <Button
              variant="emerald"
              size="sm"
              onClick={() =>
                toast.success("Notifica Toast Sonner attiva!", {
                  description: "Il sistema di feedback reattivo della Fase 4 è operativo.",
                })
              }
              className="gap-1.5"
            >
              <Bell className="h-4 w-4" />
              <span>Test Toast Success</span>
            </Button>

            {/* Test Toast Error */}
            <Button
              variant="outline"
              size="sm"
              onClick={() =>
                toast.error("Test avviso di errore", {
                  description: "Simulazione notifica di errore con styling dark ad alto contrasto.",
                })
              }
            >
              Test Toast Errore
            </Button>

            {/* Test Dialog Modal */}
            <Dialog>
              <DialogTrigger asChild>
                <Button variant="secondary" size="sm" className="gap-1.5">
                  <Layers className="h-4 w-4" />
                  <span>Apri Finestra Modale</span>
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Finestra Modale Accessibile (Dialog)</DialogTitle>
                  <DialogDescription>
                    Questo componente dialog gestisce il focus trapping, lo sfondo oscurato con effetto sfocato e la chiusura con tasto ESC.
                  </DialogDescription>
                </DialogHeader>
                <div className="py-2 text-sm text-muted-foreground">
                  Pronto per ospitare il form di inserimento del <strong>Nuovo Rifornimento</strong> e la conferma eliminazione.
                </div>
                <DialogFooter>
                  <DialogClose asChild>
                    <Button variant="emerald" size="sm">
                      Chiudi Finestra
                    </Button>
                  </DialogClose>
                </DialogFooter>
              </DialogContent>
            </Dialog>

            {/* Test Sheet Drawer */}
            <Sheet>
              <SheetTrigger asChild>
                <Button variant="outline" size="sm" className="gap-1.5">
                  <PanelRight className="h-4 w-4" />
                  <span>Apri Cassetto Laterale (Sheet)</span>
                </Button>
              </SheetTrigger>
              <SheetContent side="right">
                <SheetHeader>
                  <SheetTitle>Side Inspector Dettagli</SheetTitle>
                  <SheetDescription>
                    Pannello scorrevole laterale per ispezionare scontrini, consumi della tratta e note senza uscire dalla lista.
                  </SheetDescription>
                </SheetHeader>
                <div className="py-6 space-y-3 text-sm">
                  <div className="p-3 rounded-lg bg-muted/40 border border-border/60">
                    <div className="text-xs text-muted-foreground">Veicolo Selezionato</div>
                    <div className="font-semibold text-foreground">BMW Serie 1 • 118d</div>
                  </div>
                  <div className="p-3 rounded-lg bg-muted/40 border border-border/60">
                    <div className="text-xs text-muted-foreground">Supporto Mobile</div>
                    <div className="text-emerald-400 font-medium">Diventa Bottom Sheet su smartphone!</div>
                  </div>
                </div>
                <SheetFooter>
                  <SheetClose asChild>
                    <Button variant="outline" size="sm" className="w-full">
                      Chiudi Cassetto
                    </Button>
                  </SheetClose>
                </SheetFooter>
              </SheetContent>
            </Sheet>
          </div>

          {/* Test Tabs */}
          <div className="pt-2 border-t border-border/60">
            <div className="text-xs font-semibold text-muted-foreground mb-2">
              Test Navigazione a Schede (Tabs):
            </div>
            <Tabs defaultValue="desktop" className="w-full">
              <TabsList>
                <TabsTrigger value="desktop">Ergonomia Desktop</TabsTrigger>
                <TabsTrigger value="mobile">Ergonomia Mobile</TabsTrigger>
                <TabsTrigger value="recharts">Recharts Engine</TabsTrigger>
              </TabsList>
              <TabsContent value="desktop" className="p-3 rounded-lg bg-card/60 border border-border/60 text-xs text-muted-foreground">
                Su schermi grandi l'interfaccia adotta layout densi, tabelle complete e finestre modali centrate.
              </TabsContent>
              <TabsContent value="mobile" className="p-3 rounded-lg bg-card/60 border border-border/60 text-xs text-muted-foreground">
                Su schermi touch l'interfaccia passa alla Bottom Navigation Bar e ai cassetti Bottom Sheet dal basso.
              </TabsContent>
              <TabsContent value="recharts" className="p-3 rounded-lg bg-card/60 border border-border/60 text-xs text-muted-foreground">
                Motore Recharts installato e pronto per visualizzare le serie temporali nella Dashboard (Step 4.3).
              </TabsContent>
            </Tabs>
          </div>
        </CardContent>
      </Card>

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
            <Button
              variant="emerald"
              size="sm"
              className="gap-1.5"
              onClick={() => toast.success("Configurazione veicolo salvata!")}
            >
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

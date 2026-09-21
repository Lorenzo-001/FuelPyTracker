import { Wrench, Plus, CheckCircle, Clock } from "lucide-react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"

export default function MaintenancePage() {
  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-extrabold tracking-tight flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-amber-500/10 text-amber-400">
              <Wrench className="h-5 w-5" />
            </div>
            Registro Manutenzioni
          </h2>
          <p className="text-sm text-muted-foreground mt-1">
            Tracciamento interventi ordinari, straordinari e storico officina.
          </p>
        </div>

        <Button variant="emerald" size="sm" className="gap-1.5">
          <Plus className="h-4 w-4" />
          <span>Nuova Manutenzione</span>
        </Button>
      </div>

      {/* Category Pills & Cost Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="text-xs text-muted-foreground font-medium uppercase">Spesa Annuale</div>
          <div className="text-xl font-bold mt-1">€ 420,00</div>
          <div className="text-xs text-emerald-400 mt-1 flex items-center gap-1">
            <CheckCircle className="h-3 w-3" /> In linea con il budget
          </div>
        </Card>

        <Card className="p-4">
          <div className="text-xs text-muted-foreground font-medium uppercase">Tagliandi</div>
          <div className="text-xl font-bold mt-1">1 Eseguito</div>
          <div className="text-xs text-muted-foreground mt-1">Olio + Filtri completati</div>
        </Card>

        <Card className="p-4">
          <div className="text-xs text-muted-foreground font-medium uppercase">Pneumatici</div>
          <div className="text-xl font-bold mt-1">Inverno / Estate</div>
          <div className="text-xs text-amber-400 mt-1 flex items-center gap-1">
            <Clock className="h-3 w-3" /> Cambio gomme consigliato a Nov
          </div>
        </Card>

        <Card className="p-4">
          <div className="text-xs text-muted-foreground font-medium uppercase">Garanzia & Revisione</div>
          <div className="text-xl font-bold mt-1 text-emerald-400">Regolare</div>
          <div className="text-xs text-muted-foreground mt-1">Valida fino a Feb 2027</div>
        </Card>
      </div>

      {/* Maintenance History Skeleton */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Storico Interventi</CardTitle>
          <div className="flex gap-2">
            <Badge variant="outline">Tutti</Badge>
            <Badge variant="outline">Ordinari</Badge>
            <Badge variant="outline">Straordinari</Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {[1, 2, 3].map((item) => (
            <div
              key={item}
              className="flex items-center justify-between p-4 rounded-xl border border-border/60 bg-muted/10 hover:bg-muted/20 transition-all"
            >
              <div className="space-y-2 flex-1">
                <div className="flex items-center gap-2">
                  <Skeleton className="h-5 w-32" />
                  <Skeleton className="h-5 w-20 rounded-full" />
                </div>
                <Skeleton className="h-4 w-64" />
              </div>
              <div className="text-right space-y-1">
                <Skeleton className="h-6 w-20 ml-auto" />
                <Skeleton className="h-3 w-16 ml-auto" />
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  )
}

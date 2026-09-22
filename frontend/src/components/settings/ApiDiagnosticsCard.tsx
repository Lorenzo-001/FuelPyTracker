import { Database, Activity, RefreshCw, CheckCircle2, XCircle } from "lucide-react"
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { useSystemHealth } from "@/hooks/useSystemHealth"

export function ApiDiagnosticsCard() {
  const { data: health, isLoading, isError, refetch, isFetching } = useSystemHealth()

  const isHealthy = !isError && health?.status === "ok"

  return (
    <Card className="border-border/60 bg-card/60 backdrop-blur-sm shadow-md">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
              <Database className="h-5 w-5" />
            </div>
            <div>
              <CardTitle className="text-base font-bold">
                Infrastruttura & Diagnostica API
              </CardTitle>
              <CardDescription className="text-xs text-muted-foreground mt-0.5">
                Stato di funzionamento del backend FastAPI e del database relazionale.
              </CardDescription>
            </div>
          </div>

          <Badge
            variant={isHealthy ? "success" : isError ? "destructive" : "warning"}
            className="text-xs gap-1.5"
          >
            {isHealthy ? (
              <>
                <CheckCircle2 className="h-3 w-3" />
                Backend Connesso
              </>
            ) : isError ? (
              <>
                <XCircle className="h-3 w-3" />
                Backend Non Raggiungibile
              </>
            ) : (
              <>
                <Activity className="h-3 w-3 animate-pulse" />
                Verifica in corso...
              </>
            )}
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-3.5 text-xs">
        <div className="p-3.5 rounded-xl bg-muted/20 border border-border/50 space-y-2.5">
          <div className="flex items-center justify-between">
            <span className="text-muted-foreground">Endpoint Healthcheck:</span>
            <span className="font-mono font-semibold text-foreground">/api/health</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-muted-foreground">Reverse Proxy Vite:</span>
            <span className="font-mono text-emerald-400 font-semibold">
              http://127.0.0.1:8000
            </span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-muted-foreground">Database Engine:</span>
            <span className="font-medium text-foreground">SQLite (fuel_tracker.db)</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-muted-foreground">Versione Servizio:</span>
            <span className="font-mono text-muted-foreground">
              {health?.version || "2.0.0-rc1"}
            </span>
          </div>
          {health?.timestamp && (
            <div className="flex items-center justify-between">
              <span className="text-muted-foreground">Ultimo Heartbeat:</span>
              <span className="font-mono text-muted-foreground">
                {new Date(health.timestamp).toLocaleTimeString("it-IT")}
              </span>
            </div>
          )}
        </div>
      </CardContent>

      <CardFooter className="border-t border-border/60 pt-4 flex items-center justify-between">
        <span className="text-[11px] text-muted-foreground">
          Ping automatico attivo ogni 15 secondi.
        </span>

        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={() => refetch()}
          disabled={isLoading || isFetching}
          className="gap-1.5 text-xs"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${isFetching ? "animate-spin text-emerald-400" : ""}`} />
          <span>Verifica Ora</span>
        </Button>
      </CardFooter>
    </Card>
  )
}

import { Activity, CheckCircle2, AlertTriangle, XCircle, ShieldCheck } from "lucide-react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import type { HealthScoreSummary } from "@/types"

interface CarHealthWidgetProps {
  healthScore?: HealthScoreSummary
  currentKm?: number
}

export function CarHealthWidget({ healthScore, currentKm }: CarHealthWidgetProps) {
  const score = healthScore?.score ?? 100
  const color = healthScore?.status_color ?? "green"
  const issues = healthScore?.issues ?? []

  // SVG circular calculation
  const radius = 38
  const circumference = 2 * Math.PI * radius
  const strokeDashoffset = circumference - (score / 100) * circumference

  const colorClasses = {
    green: {
      stroke: "#10b981",
      bgBadge: "border-emerald-500/30 bg-emerald-500/10 text-emerald-400",
      label: "Salute Eccellente",
      icon: CheckCircle2,
    },
    orange: {
      stroke: "#f59e0b",
      bgBadge: "border-amber-500/30 bg-amber-500/10 text-amber-400",
      label: "Attenzione Richiesta",
      icon: AlertTriangle,
    },
    red: {
      stroke: "#ef4444",
      bgBadge: "border-red-500/30 bg-red-500/10 text-red-400",
      label: "Intervento Critico",
      icon: XCircle,
    },
  }[color] || {
    stroke: "#10b981",
    bgBadge: "border-emerald-500/30 bg-emerald-500/10 text-emerald-400",
    label: "Salute Eccellente",
    icon: CheckCircle2,
  }

  const StatusIcon = colorClasses.icon

  return (
    <Card className="shadow-sm hover:border-border transition-all">
      <CardHeader className="flex flex-row items-center justify-between pb-3">
        <CardTitle className="text-base font-bold flex items-center gap-2">
          <Activity className="h-5 w-5 text-emerald-400" />
          Car Health Score
        </CardTitle>
        <Badge variant="outline" className={colorClasses.bgBadge}>
          {colorClasses.label}
        </Badge>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Circular Progress & KPI Summary */}
        <div className="flex items-center gap-5 p-3 rounded-xl bg-muted/20 border border-border/60">
          <div className="relative h-24 w-24 shrink-0 flex items-center justify-center">
            <svg className="h-full w-full -rotate-90 transform" viewBox="0 0 96 96">
              {/* Background Track */}
              <circle
                cx="48"
                cy="48"
                r={radius}
                className="stroke-muted/40"
                strokeWidth="7"
                fill="transparent"
              />
              {/* Colored Progress Ring */}
              <circle
                cx="48"
                cy="48"
                r={radius}
                stroke={colorClasses.stroke}
                strokeWidth="7"
                strokeDasharray={circumference}
                strokeDashoffset={strokeDashoffset}
                strokeLinecap="round"
                fill="transparent"
                className="transition-all duration-1000 ease-out"
              />
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
              <span className="text-2xl font-black tracking-tighter text-foreground">
                {score}
              </span>
              <span className="text-[10px] text-muted-foreground font-semibold uppercase -mt-1">
                / 100
              </span>
            </div>
          </div>

          <div className="space-y-1 text-xs">
            <div className="font-semibold text-foreground flex items-center gap-1.5">
              <ShieldCheck className="h-4 w-4 text-emerald-400" />
              <span>Algoritmo di Gamification V2</span>
            </div>
            <p className="text-muted-foreground leading-relaxed">
              Il punteggio calcola l'usura stimata, le scadenze temporali e la regolarità dei tagliandi su {currentKm ? `${currentKm.toLocaleString("it-IT")} km` : "chilometraggio totale"}.
            </p>
          </div>
        </div>

        {/* Issues List or All Clear State */}
        <div className="space-y-2">
          <div className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Diagnostica Attiva
          </div>
          {issues.length === 0 ? (
            <div className="flex items-center gap-2.5 p-3 rounded-lg border border-emerald-500/20 bg-emerald-500/10 text-xs text-emerald-300">
              <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />
              <span>Tutti i controlli meccanici e le scadenze risultano in perfetto ordine.</span>
            </div>
          ) : (
            <div className="space-y-1.5">
              {issues.map((issue, idx) => (
                <div
                  key={idx}
                  className="flex items-start gap-2 p-2.5 rounded-lg border border-amber-500/30 bg-amber-500/10 text-xs text-amber-200"
                >
                  <StatusIcon className="h-3.5 w-3.5 text-amber-400 shrink-0 mt-0.5" />
                  <span>{issue}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

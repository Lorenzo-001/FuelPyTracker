import { Link } from "react-router-dom"
import { Compass, Home } from "lucide-react"
import { Button } from "@/components/ui/button"

export default function NotFoundPage() {
  return (
    <div className="min-h-[60vh] flex flex-col items-center justify-center text-center p-6 space-y-4">
      <div className="h-16 w-16 rounded-2xl bg-muted/40 border border-border/70 flex items-center justify-center text-emerald-400 mb-2">
        <Compass className="h-8 w-8 animate-spin-slow" />
      </div>
      <h2 className="text-4xl font-extrabold tracking-tight">404</h2>
      <h3 className="text-lg font-semibold text-foreground">Pagina non trovata</h3>
      <p className="text-sm text-muted-foreground max-w-md">
        La sezione richiesta non esiste o è stata spostata. Torna alla dashboard principale per continuare la navigazione.
      </p>
      <Button asChild variant="emerald" className="gap-2 mt-2">
        <Link to="/">
          <Home className="h-4 w-4" />
          <span>Torna alla Dashboard</span>
        </Link>
      </Button>
    </div>
  )
}

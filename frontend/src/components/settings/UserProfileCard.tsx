import { User, LogOut, ShieldCheck, KeyRound, AlertCircle, Loader2 } from "lucide-react"
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { useCurrentUser, useLogout } from "@/hooks/useAuth"
import { Link } from "react-router-dom"

export function UserProfileCard() {
  const { data: user, isLoading, isError } = useCurrentUser()
  const logoutMutation = useLogout()

  const handleLogout = () => {
    logoutMutation.mutate()
  }

  return (
    <Card className="border-border/60 bg-card/60 backdrop-blur-sm shadow-md">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
              <User className="h-5 w-5" />
            </div>
            <div>
              <CardTitle className="text-base font-bold">
                Profilo Utente & Sessione
              </CardTitle>
              <CardDescription className="text-xs text-muted-foreground mt-0.5">
                Stato dell&apos;identità autenticata e parametri di sessione JWT.
              </CardDescription>
            </div>
          </div>

          {user && (
            <Badge
              variant={user.is_demo ? "warning" : "success"}
              className="text-xs gap-1.5"
            >
              {user.is_demo ? (
                <>
                  <AlertCircle className="h-3 w-3" />
                  Modalità Demo Sandbox
                </>
              ) : (
                <>
                  <ShieldCheck className="h-3 w-3" />
                  Account Autenticato
                </>
              )}
            </Badge>
          )}
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {isLoading ? (
          <div className="flex items-center justify-center p-6 text-muted-foreground">
            <Loader2 className="h-5 w-5 animate-spin mr-2" />
            <span className="text-xs">Caricamento credenziali profilo...</span>
          </div>
        ) : isError || !user ? (
          <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs flex items-start gap-2.5">
            <AlertCircle className="h-4 w-4 shrink-0 mt-0.5" />
            <div>
              <div className="font-semibold">Nessuna sessione attiva rilevata</div>
              <div className="text-[11px] text-amber-200/80 mt-0.5">
                Stai utilizzando l&apos;applicazione con l&apos;utente demo predefinito di sistema.
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-3">
            <div className="flex items-center gap-3.5 p-3 rounded-xl bg-muted/20 border border-border/50">
              <div className="h-10 w-10 rounded-full bg-gradient-to-br from-emerald-400 to-emerald-600 flex items-center justify-center text-slate-950 font-bold shadow-md shadow-emerald-500/20">
                {user.email.substring(0, 2).toUpperCase()}
              </div>
              <div className="space-y-0.5 overflow-hidden">
                <div className="text-sm font-semibold text-foreground truncate">
                  {user.email}
                </div>
                <div className="text-[11px] font-mono text-muted-foreground truncate">
                  ID: {user.id}
                </div>
              </div>
            </div>

            <div className="text-xs text-muted-foreground space-y-1.5 p-3 rounded-lg bg-muted/10 border border-border/40">
              <div className="flex items-center justify-between">
                <span>Tipo Sessione:</span>
                <span className="font-medium text-foreground">
                  {user.is_demo ? "Demo Sandbox (Memoria/File Locale)" : "Bearer Token JWT (Supabase)"}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span>Persistenza Token:</span>
                <span className="font-mono text-[11px] text-emerald-400">
                  LocalStorage (fpt_access_token)
                </span>
              </div>
            </div>
          </div>
        )}
      </CardContent>

      <CardFooter className="border-t border-border/60 pt-4 flex items-center justify-between">
        <Button asChild variant="outline" size="sm" className="gap-1.5 text-xs">
          <Link to="/login">
            <KeyRound className="h-3.5 w-3.5" />
            <span>Accedi o Cambia Account</span>
          </Link>
        </Button>

        <Button
          variant="destructive"
          size="sm"
          onClick={handleLogout}
          disabled={logoutMutation.isPending}
          className="gap-1.5 text-xs"
        >
          {logoutMutation.isPending ? (
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
          ) : (
            <LogOut className="h-3.5 w-3.5" />
          )}
          <span>Disconnetti</span>
        </Button>
      </CardFooter>
    </Card>
  )
}

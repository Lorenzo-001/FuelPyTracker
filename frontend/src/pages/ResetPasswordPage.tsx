import React, { useState } from "react"
import { useNavigate, useLocation, Link } from "react-router-dom"
import { Fuel, Lock, KeyRound, ArrowRight, Loader2, CheckCircle2, AlertTriangle, Eye, EyeOff } from "lucide-react"
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { authApi } from "@/services/api/authApi"
import { toast } from "sonner"

export default function ResetPasswordPage() {
  const navigate = useNavigate()
  const location = useLocation()

  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [isSuccess, setIsSuccess] = useState(false)

  // Estrazione token da hash (#access_token=...&type=recovery) o da query params (?code=... o ?access_token=...)
  const { accessToken, refreshToken, tokenError } = React.useMemo(() => {
    let token: string | null = null
    let refToken: string | null = null
    let errorDesc: string | null = null

    // 1. Controlla hash fragment (Implicit flow Supabase)
    if (typeof window !== "undefined" && window.location.hash) {
      const hashParams = new URLSearchParams(window.location.hash.replace(/^#/, ""))
      token = hashParams.get("access_token")
      refToken = hashParams.get("refresh_token")
      errorDesc = hashParams.get("error_description")
    }

    // 2. Controlla query search params se non presente in hash
    if (!token && location.search) {
      const searchParams = new URLSearchParams(location.search)
      token = searchParams.get("access_token") || searchParams.get("code")
      refToken = searchParams.get("refresh_token")
      errorDesc = searchParams.get("error_description")
    }

    if (errorDesc) {
      return {
        accessToken: null,
        refreshToken: null,
        tokenError: "Il link di recupero è scaduto o non è valido. Richiedi un nuovo link.",
      }
    }
    if (token) {
      return {
        accessToken: token,
        refreshToken: refToken,
        tokenError: null,
      }
    }
    return {
      accessToken: null,
      refreshToken: null,
      tokenError: "Nessun token di recupero rilevato. Utilizza il link ricevuto via email.",
    }
  }, [location])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!accessToken) {
      toast.error("Token mancante o scaduto. Richiedi un nuovo link di recupero.")
      return
    }

    if (password.length < 8) {
      toast.error("Password troppo corta", {
        description: "La nuova password deve contenere almeno 8 caratteri.",
      })
      return
    }

    if (password !== confirmPassword) {
      toast.error("Le password non coincidono", {
        description: "Verifica di aver digitato la stessa password in entrambi i campi.",
      })
      return
    }

    setIsLoading(true)
    try {
      const res = await authApi.confirmPasswordReset({
        access_token: accessToken,
        new_password: password,
        refresh_token: refreshToken,
      })

      setIsSuccess(true)
      toast.success("Password impostata!", {
        description: res.message || "Puoi accedere ora con la nuova password.",
      })
    } catch (err: unknown) {
      const errorMsg =
        err instanceof Error ? err.message : "Impossibile aggiornare la password"
      toast.error("Errore recupero", {
        description: errorMsg,
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-background">
      <div className="w-full max-w-md space-y-6">
        <Card className="border-border/80 shadow-2xl bg-card/90 backdrop-blur-md">
          <CardHeader className="space-y-1 text-center">
            <div className="mx-auto h-12 w-12 rounded-2xl bg-gradient-to-br from-emerald-400 to-emerald-600 flex items-center justify-center text-slate-950 shadow-lg shadow-emerald-500/25 mb-2">
              <Fuel className="h-6 w-6" />
            </div>
            <CardTitle className="text-2xl font-bold tracking-tight">
              FuelPyTracker
            </CardTitle>
            <CardDescription className="text-xs text-muted-foreground">
              Reimposta la password di accesso al tuo profilo
            </CardDescription>
          </CardHeader>

          {tokenError ? (
            <CardContent className="space-y-4 pt-2 text-center">
              <div className="mx-auto h-12 w-12 rounded-full bg-amber-500/15 border border-amber-500/30 flex items-center justify-center text-amber-400">
                <AlertTriangle className="h-6 w-6" />
              </div>
              <div className="space-y-1.5">
                <h3 className="text-sm font-semibold text-foreground">
                  Link non valido o scaduto
                </h3>
                <p className="text-xs text-muted-foreground leading-relaxed">
                  {tokenError}
                </p>
              </div>
              <div className="pt-2">
                <Button
                  variant="emerald"
                  className="w-full text-xs font-semibold gap-1.5"
                  onClick={() => navigate("/login")}
                >
                  <span>Torna alla Schermata di Accesso</span>
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          ) : isSuccess ? (
            <CardContent className="space-y-4 pt-2 text-center">
              <div className="mx-auto h-12 w-12 rounded-full bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400 animate-in zoom-in-75">
                <CheckCircle2 className="h-6 w-6" />
              </div>
              <div className="space-y-1.5">
                <h3 className="text-sm font-semibold text-foreground">
                  Password aggiornata con successo!
                </h3>
                <p className="text-xs text-muted-foreground leading-relaxed">
                  La tua nuova credenziale è attiva. Ora puoi effettuare il login con la nuova password.
                </p>
              </div>
              <div className="pt-2">
                <Button
                  variant="emerald"
                  className="w-full text-xs font-semibold gap-1.5"
                  onClick={() => navigate("/login")}
                >
                  <span>Accedi Subito</span>
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </div>
            </CardContent>
          ) : (
            <form onSubmit={handleSubmit}>
              <CardContent className="space-y-4 pt-2">
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-muted-foreground flex items-center gap-1.5">
                    <Lock className="h-3.5 w-3.5 text-emerald-400" />
                    Nuova Password (min 8 caratteri)
                  </label>
                  <div className="relative">
                    <Input
                      type={showPassword ? "text" : "password"}
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="••••••••"
                      required
                      minLength={8}
                      disabled={isLoading}
                      className="text-xs pr-9"
                      autoFocus
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-2.5 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors focus:outline-none"
                    >
                      {showPassword ? (
                        <EyeOff className="h-3.5 w-3.5" />
                      ) : (
                        <Eye className="h-3.5 w-3.5" />
                      )}
                    </button>
                  </div>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-muted-foreground flex items-center gap-1.5">
                    <KeyRound className="h-3.5 w-3.5 text-emerald-400" />
                    Conferma Nuova Password
                  </label>
                  <Input
                    type={showPassword ? "text" : "password"}
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Ripeti la nuova password"
                    required
                    minLength={8}
                    disabled={isLoading}
                    className="text-xs"
                  />
                </div>

                <div className="space-y-1 text-[11px] text-muted-foreground bg-muted/30 p-2.5 rounded-lg border border-border/50">
                  <div className="flex items-center gap-1.5 font-medium">
                    <span className={password.length >= 8 ? "text-emerald-400 font-bold" : "text-muted-foreground"}>
                      {password.length >= 8 ? "✓" : "○"}
                    </span>
                    <span>Lunghezza minima di 8 caratteri</span>
                  </div>
                  <div className="flex items-center gap-1.5 font-medium">
                    <span className={confirmPassword && password === confirmPassword ? "text-emerald-400 font-bold" : "text-muted-foreground"}>
                      {confirmPassword && password === confirmPassword ? "✓" : "○"}
                    </span>
                    <span>Le due password corrispondono</span>
                  </div>
                </div>
              </CardContent>

              <CardFooter className="flex flex-col gap-3 pt-2">
                <Button
                  type="submit"
                  variant="emerald"
                  className="w-full gap-2 font-semibold"
                  disabled={isLoading || password.length < 8 || password !== confirmPassword}
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      <span>Aggiornamento in corso...</span>
                    </>
                  ) : (
                    <>
                      <span>Imposta Nuova Password</span>
                      <ArrowRight className="h-4 w-4" />
                    </>
                  )}
                </Button>

                <div className="text-center pt-1">
                  <Link
                    to="/login"
                    className="text-[11px] text-muted-foreground hover:text-emerald-400 transition-colors"
                  >
                    Annulla e torna al login
                  </Link>
                </div>
              </CardFooter>
            </form>
          )}
        </Card>
      </div>
    </div>
  )
}

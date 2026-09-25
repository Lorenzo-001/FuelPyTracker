import React, { useState } from "react"
import { Navigate } from "react-router-dom"
import { Fuel, Lock, Mail, ArrowRight, Loader2, ShieldCheck, UserPlus, KeyRound } from "lucide-react"
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card"
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useLogin, useRegister } from "@/hooks/useAuth"
import { authStorage } from "@/services/api/client"
import { isPublicDemoMode } from "@/lib/demo"
import { toast } from "sonner"

export default function LoginPage() {
  const loginMutation = useLogin()
  const registerMutation = useRegister()

  const [activeTab, setActiveTab] = useState<"login" | "register">("login")

  // Login form state
  const [loginEmail, setLoginEmail] = useState("")
  const [loginPassword, setLoginPassword] = useState("")

  // Register form state
  const [regEmail, setRegEmail] = useState("")
  const [regPassword, setRegPassword] = useState("")
  const [regConfirmPassword, setRegConfirmPassword] = useState("")

  // Se l'utente ha già una sessione attiva (non demo temporanea), reindirizza direttamente alla dashboard
  const token = authStorage.getToken()
  if (token && !isPublicDemoMode()) {
    return <Navigate to="/" replace />
  }

  const handleLoginSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    loginMutation.mutate({
      email: loginEmail.trim(),
      password: loginPassword,
    })
  }

  const handleRegisterSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (regPassword !== regConfirmPassword) {
      toast.error("Le password non coincidono", {
        description: "Assicurati di digitare la stessa password in entrambi i campi.",
      })
      return
    }

    if (regPassword.length < 6) {
      toast.error("Password troppo breve", {
        description: "La password deve contenere almeno 6 caratteri.",
      })
      return
    }

    registerMutation.mutate(
      {
        email: regEmail.trim(),
        password: regPassword,
      },
      {
        onSuccess: () => {
          // Pre-compila l'email nel login e passa alla schermata di accesso
          setLoginEmail(regEmail.trim())
          setActiveTab("login")
        },
      }
    )
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
              Gestisci consumi, scadenze, costi e manutenzioni del tuo veicolo.
            </CardDescription>
          </CardHeader>

          <Tabs
            value={activeTab}
            onValueChange={(val) => setActiveTab(val as "login" | "register")}
            className="w-full"
          >
            <div className="px-6 pb-2">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="login" className="text-xs font-semibold gap-1.5">
                  <Lock className="h-3.5 w-3.5" />
                  <span>Accedi</span>
                </TabsTrigger>
                <TabsTrigger value="register" className="text-xs font-semibold gap-1.5">
                  <UserPlus className="h-3.5 w-3.5" />
                  <span>Registrati</span>
                </TabsTrigger>
              </TabsList>
            </div>

            {/* TAB LOGIN */}
            <TabsContent value="login">
              <form onSubmit={handleLoginSubmit}>
                <CardContent className="space-y-4 pt-2">
                  <div className="space-y-1.5">
                    <label className="text-xs font-medium text-muted-foreground flex items-center gap-1.5">
                      <Mail className="h-3.5 w-3.5 text-emerald-400" />
                      Email Utente
                    </label>
                    <Input
                      type="email"
                      value={loginEmail}
                      onChange={(e) => setLoginEmail(e.target.value)}
                      placeholder="latuaemail@dominio.it"
                      required
                      disabled={loginMutation.isPending}
                      className="text-xs"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-medium text-muted-foreground flex items-center gap-1.5">
                      <Lock className="h-3.5 w-3.5 text-emerald-400" />
                      Password
                    </label>
                    <Input
                      type="password"
                      value={loginPassword}
                      onChange={(e) => setLoginPassword(e.target.value)}
                      placeholder="••••••••"
                      required
                      disabled={loginMutation.isPending}
                      className="text-xs"
                    />
                  </div>
                </CardContent>

                <CardFooter className="flex flex-col gap-3 pt-2">
                  <Button
                    type="submit"
                    variant="emerald"
                    className="w-full gap-2 font-semibold"
                    disabled={loginMutation.isPending}
                  >
                    {loginMutation.isPending ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        <span>Autenticazione in corso...</span>
                      </>
                    ) : (
                      <>
                        <span>Accedi alla Piattaforma</span>
                        <ArrowRight className="h-4 w-4" />
                      </>
                    )}
                  </Button>

                  <div className="flex items-center justify-center gap-1.5 text-[11px] text-muted-foreground mt-2">
                    <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" />
                    <span>Autenticazione protetta (Supabase / SQLite)</span>
                  </div>
                </CardFooter>
              </form>
            </TabsContent>

            {/* TAB REGISTRATI */}
            <TabsContent value="register">
              <form onSubmit={handleRegisterSubmit}>
                <CardContent className="space-y-4 pt-2">
                  <div className="space-y-1.5">
                    <label className="text-xs font-medium text-muted-foreground flex items-center gap-1.5">
                      <Mail className="h-3.5 w-3.5 text-emerald-400" />
                      Email per il nuovo account
                    </label>
                    <Input
                      type="email"
                      value={regEmail}
                      onChange={(e) => setRegEmail(e.target.value)}
                      placeholder="latuaemail@dominio.it"
                      required
                      disabled={registerMutation.isPending}
                      className="text-xs"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-medium text-muted-foreground flex items-center gap-1.5">
                      <Lock className="h-3.5 w-3.5 text-emerald-400" />
                      Password
                    </label>
                    <Input
                      type="password"
                      value={regPassword}
                      onChange={(e) => setRegPassword(e.target.value)}
                      placeholder="Almeno 6 caratteri"
                      required
                      disabled={registerMutation.isPending}
                      className="text-xs"
                    />
                  </div>

                  <div className="space-y-1.5">
                    <label className="text-xs font-medium text-muted-foreground flex items-center gap-1.5">
                      <KeyRound className="h-3.5 w-3.5 text-emerald-400" />
                      Conferma Password
                    </label>
                    <Input
                      type="password"
                      value={regConfirmPassword}
                      onChange={(e) => setRegConfirmPassword(e.target.value)}
                      placeholder="Ripeti la password"
                      required
                      disabled={registerMutation.isPending}
                      className="text-xs"
                    />
                  </div>
                </CardContent>

                <CardFooter className="flex flex-col gap-3 pt-2">
                  <Button
                    type="submit"
                    variant="emerald"
                    className="w-full gap-2 font-semibold"
                    disabled={registerMutation.isPending}
                  >
                    {registerMutation.isPending ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        <span>Creazione profilo...</span>
                      </>
                    ) : (
                      <>
                        <span>Crea Account</span>
                        <UserPlus className="h-4 w-4" />
                      </>
                    )}
                  </Button>

                  <div className="flex items-center justify-center gap-1.5 text-[11px] text-muted-foreground mt-2">
                    <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" />
                    <span>I tuoi dati rimangono privati e protetti</span>
                  </div>
                </CardFooter>
              </form>
            </TabsContent>
          </Tabs>
        </Card>
      </div>
    </div>
  )
}


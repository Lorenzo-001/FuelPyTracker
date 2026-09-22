import React, { useState } from "react"
import { Link } from "react-router-dom"
import { Fuel, Lock, Mail, ArrowRight, ArrowLeft, Loader2, Sparkles, ShieldCheck } from "lucide-react"
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useLogin } from "@/hooks/useAuth"

export default function LoginPage() {
  const loginMutation = useLogin()
  const [email, setEmail] = useState("utente@fuelpytracker.com")
  const [password, setPassword] = useState("password123")

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    loginMutation.mutate({
      email: email.trim(),
      password,
    })
  }

  const handleDemoLogin = () => {
    loginMutation.mutate({
      email: "demo@fuelpytracker.com",
      password: "demo",
    })
  }

  return (
    <div className="min-h-[80vh] flex items-center justify-center p-4">
      <div className="w-full max-w-md space-y-6">
        {/* Torna alla Dashboard */}
        <Link
          to="/"
          className="inline-flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="h-3.5 w-3.5" />
          <span>Torna alla Dashboard</span>
        </Link>

        <Card className="border-border/80 shadow-2xl bg-card/80 backdrop-blur-md">
          <CardHeader className="space-y-1 text-center">
            <div className="mx-auto h-12 w-12 rounded-2xl bg-gradient-to-br from-emerald-400 to-emerald-600 flex items-center justify-center text-slate-950 shadow-lg shadow-emerald-500/25 mb-2">
              <Fuel className="h-6 w-6" />
            </div>
            <CardTitle className="text-2xl font-bold tracking-tight">
              FuelPyTracker
            </CardTitle>
            <CardDescription className="text-xs text-muted-foreground">
              Accedi alla tua area personale per gestire consumi, scadenze e costi veicolo.
            </CardDescription>
          </CardHeader>

          <form onSubmit={handleSubmit}>
            <CardContent className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-muted-foreground flex items-center gap-1.5">
                  <Mail className="h-3.5 w-3.5 text-emerald-400" />
                  Email Utente
                </label>
                <Input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="nome@dominio.it"
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
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
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

              <div className="relative w-full my-1">
                <div className="absolute inset-0 flex items-center">
                  <span className="w-full border-t border-border/60" />
                </div>
                <div className="relative flex justify-center text-[10px] uppercase">
                  <span className="bg-card px-2 text-muted-foreground font-semibold">oppure</span>
                </div>
              </div>

              {/* Accesso Rapido Sandbox Demo */}
              <Button
                type="button"
                variant="outline"
                onClick={handleDemoLogin}
                disabled={loginMutation.isPending}
                className="w-full gap-2 text-xs border-emerald-500/30 hover:bg-emerald-950/20 text-emerald-300"
              >
                <Sparkles className="h-3.5 w-3.5 text-emerald-400" />
                <span>Accedi in Modalità Demo Sandbox</span>
              </Button>

              <div className="flex items-center justify-center gap-1.5 text-[11px] text-muted-foreground mt-2">
                <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" />
                <span>Sessione protetta con token Bearer JWT</span>
              </div>
            </CardFooter>
          </form>
        </Card>
      </div>
    </div>
  )
}

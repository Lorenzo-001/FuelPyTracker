import React, { useState } from "react"
import { useNavigate, Link } from "react-router-dom"
import { Fuel, Lock, User, ArrowRight, ArrowLeft } from "lucide-react"
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

export default function LoginPage() {
  const navigate = useNavigate()
  const [username, setUsername] = useState("admin")
  const [password, setPassword] = useState("password")

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // Simulated login for bootstrap shell
    navigate("/")
  }

  return (
    <div className="min-h-[80vh] flex items-center justify-center p-4">
      <div className="w-full max-w-md space-y-6">
        {/* Back Link */}
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
            <CardDescription>
              Inserisci le tue credenziali per accedere alla piattaforma di gestione.
            </CardDescription>
          </CardHeader>

          <form onSubmit={handleSubmit}>
            <CardContent className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-muted-foreground flex items-center gap-1.5">
                  <User className="h-3.5 w-3.5" />
                  Nome Utente o Email
                </label>
                <Input
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="admin"
                  required
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-xs font-medium text-muted-foreground flex items-center gap-1.5">
                  <Lock className="h-3.5 w-3.5" />
                  Password
                </label>
                <Input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                />
              </div>
            </CardContent>

            <CardFooter className="flex flex-col gap-3 pt-2">
              <Button type="submit" variant="emerald" className="w-full gap-2 font-semibold">
                <span>Accedi alla Piattaforma</span>
                <ArrowRight className="h-4 w-4" />
              </Button>
              <p className="text-[11px] text-center text-muted-foreground">
                Integrazione completa con <code>/api/auth/token</code> (Fase 4).
              </p>
            </CardFooter>
          </form>
        </Card>
      </div>
    </div>
  )
}

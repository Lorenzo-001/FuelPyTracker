import React, { useState } from "react"
import {
  KeyRound,
  Lock,
  Eye,
  EyeOff,
  CheckCircle2,
  Loader2,
} from "lucide-react"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { authApi } from "@/services/api/authApi"
import { toast } from "sonner"

export function UserPasswordCard() {
  const [currentPassword, setCurrentPassword] = useState("")
  const [newPassword, setNewPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [showCurrentPass, setShowCurrentPass] = useState(false)
  const [showNewPass, setShowNewPass] = useState(false)
  const [isChangingPass, setIsChangingPass] = useState(false)

  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!currentPassword) {
      toast.error("Inserisci la password attuale per confermare la tua identità.")
      return
    }

    if (newPassword.length < 8) {
      toast.error("Password troppo corta", {
        description: "La nuova password deve contenere almeno 8 caratteri.",
      })
      return
    }

    if (currentPassword === newPassword) {
      toast.error("Password identica", {
        description: "La nuova password deve essere diversa da quella attuale.",
      })
      return
    }

    if (newPassword !== confirmPassword) {
      toast.error("Le password non coincidono", {
        description: "Verifica che la conferma coincida con la nuova password.",
      })
      return
    }

    setIsChangingPass(true)
    try {
      const res = await authApi.changePassword({
        current_password: currentPassword,
        new_password: newPassword,
      })
      toast.success("Password modificata!", {
        description: res.message || "La tua credenziale di accesso è stata aggiornata con successo.",
      })
      setCurrentPassword("")
      setNewPassword("")
      setConfirmPassword("")
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Errore durante l'aggiornamento della password"
      toast.error("Operazione fallita", { description: msg })
    } finally {
      setIsChangingPass(false)
    }
  }

  return (
    <Card className="border-border/60 bg-card/60 backdrop-blur-sm shadow-md">
      <CardHeader>
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 shrink-0">
            <KeyRound className="h-5 w-5" />
          </div>
          <div>
            <CardTitle className="text-base font-bold">
              Sicurezza Password
            </CardTitle>
            <CardDescription className="text-xs text-muted-foreground mt-0.5">
              Aggiorna la password dell&apos;account con verifica preliminare della credenziale attuale.
            </CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        <form onSubmit={handlePasswordSubmit} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-1.5 sm:col-span-2">
              <label className="text-xs font-medium text-muted-foreground flex items-center gap-1.5">
                <Lock className="h-3.5 w-3.5 text-emerald-400" />
                Password Attuale
              </label>
              <div className="relative">
                <Input
                  type={showCurrentPass ? "text" : "password"}
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                  placeholder="Digita la password attuale"
                  required
                  disabled={isChangingPass}
                  className="text-xs pr-9"
                />
                <button
                  type="button"
                  onClick={() => setShowCurrentPass(!showCurrentPass)}
                  className="absolute right-2.5 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors focus:outline-none"
                >
                  {showCurrentPass ? <EyeOff className="h-3.5 w-3.5" /> : <Eye className="h-3.5 w-3.5" />}
                </button>
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-medium text-muted-foreground flex items-center gap-1.5">
                <KeyRound className="h-3.5 w-3.5 text-emerald-400" />
                Nuova Password (min 8 car.)
              </label>
              <div className="relative">
                <Input
                  type={showNewPass ? "text" : "password"}
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder="Almeno 8 caratteri"
                  required
                  minLength={8}
                  disabled={isChangingPass}
                  className="text-xs pr-9"
                />
                <button
                  type="button"
                  onClick={() => setShowNewPass(!showNewPass)}
                  className="absolute right-2.5 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors focus:outline-none"
                >
                  {showNewPass ? <EyeOff className="h-3.5 w-3.5" /> : <Eye className="h-3.5 w-3.5" />}
                </button>
              </div>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-medium text-muted-foreground flex items-center gap-1.5">
                <KeyRound className="h-3.5 w-3.5 text-emerald-400" />
                Conferma Nuova Password
              </label>
              <Input
                type={showNewPass ? "text" : "password"}
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Ripeti la nuova password"
                required
                minLength={8}
                disabled={isChangingPass}
                className="text-xs"
              />
            </div>
          </div>

          {/* Checklist Validazione Password */}
          <div className="space-y-1 text-[11px] text-muted-foreground bg-muted/20 p-3 rounded-lg border border-border/40">
            <div className="flex items-center gap-1.5 font-medium">
              <span className={newPassword.length >= 8 ? "text-emerald-400 font-bold" : "text-muted-foreground"}>
                {newPassword.length >= 8 ? "✓" : "○"}
              </span>
              <span>Lunghezza minima di 8 caratteri</span>
            </div>
            <div className="flex items-center gap-1.5 font-medium">
              <span className={newPassword && currentPassword && newPassword !== currentPassword ? "text-emerald-400 font-bold" : "text-muted-foreground"}>
                {newPassword && currentPassword && newPassword !== currentPassword ? "✓" : "○"}
              </span>
              <span>Diversa dalla password attuale</span>
            </div>
            <div className="flex items-center gap-1.5 font-medium">
              <span className={confirmPassword && newPassword === confirmPassword ? "text-emerald-400 font-bold" : "text-muted-foreground"}>
                {confirmPassword && newPassword === confirmPassword ? "✓" : "○"}
              </span>
              <span>Le password coincidono</span>
            </div>
          </div>

          <div className="flex justify-end pt-1">
            <Button
              type="submit"
              variant="emerald"
              disabled={
                isChangingPass ||
                !currentPassword ||
                newPassword.length < 8 ||
                newPassword !== confirmPassword ||
                newPassword === currentPassword
              }
              className="text-xs font-semibold gap-1.5 w-full sm:w-auto"
            >
              {isChangingPass ? (
                <>
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                  <span>Verifica & Aggiornamento...</span>
                </>
              ) : (
                <>
                  <CheckCircle2 className="h-3.5 w-3.5" />
                  <span>Aggiorna Password</span>
                </>
              )}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  )
}

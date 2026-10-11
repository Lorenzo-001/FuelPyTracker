import React, { useState } from "react"
import { Mail, KeyRound, ArrowRight, Loader2, CheckCircle2 } from "lucide-react"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { authApi } from "@/services/api/authApi"
import { toast } from "sonner"

interface ForgotPasswordModalProps {
  isOpen: boolean
  onClose: () => void
  defaultEmail?: string
}

export function ForgotPasswordModal({
  isOpen,
  onClose,
  defaultEmail = "",
}: ForgotPasswordModalProps) {
  const [email, setEmail] = useState(defaultEmail)
  const [isLoading, setIsLoading] = useState(false)
  const [isSuccess, setIsSuccess] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const cleanEmail = email.trim()
    if (!cleanEmail) {
      toast.error("Inserisci un indirizzo email valido.")
      return
    }

    setIsLoading(true)
    try {
      const res = await authApi.resetPassword(cleanEmail)
      setIsSuccess(true)
      toast.success("Richiesta inviata", {
        description: res.message || "Controlla la tua casella email.",
      })
    } catch (err: unknown) {
      const errorMsg =
        err instanceof Error ? err.message : "Errore durante l'invio della richiesta"
      toast.error("Invio non riuscito", {
        description: errorMsg,
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleClose = () => {
    setIsSuccess(false)
    setIsLoading(false)
    onClose()
  }

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && handleClose()}>
      <DialogContent className="sm:max-w-md bg-card/95 border-border shadow-2xl backdrop-blur-md">
        <DialogHeader className="space-y-2 text-center sm:text-left">
          <div className="mx-auto sm:mx-0 h-10 w-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 mb-1">
            <KeyRound className="h-5 w-5" />
          </div>
          <DialogTitle className="text-lg font-bold tracking-tight">
            Recupera la tua Password
          </DialogTitle>
          <DialogDescription className="text-xs text-muted-foreground">
            Inserisci l'indirizzo email associato al tuo account. Ti invieremo un link sicuro per impostare una nuova password.
          </DialogDescription>
        </DialogHeader>

        {isSuccess ? (
          <div className="py-4 space-y-4 text-center">
            <div className="mx-auto h-12 w-12 rounded-full bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400 animate-in zoom-in-75">
              <CheckCircle2 className="h-6 w-6" />
            </div>
            <div className="space-y-1.5">
              <h4 className="text-sm font-semibold text-foreground">
                Email inviata con successo
              </h4>
              <p className="text-xs text-muted-foreground max-w-xs mx-auto leading-relaxed">
                Se l'indirizzo <span className="text-emerald-400 font-medium">{email}</span> è registrato nei nostri sistemi, riceverai a breve un link valido per reimpostare la password.
              </p>
            </div>
            <div className="pt-2">
              <Button
                variant="outline"
                className="w-full text-xs font-medium"
                onClick={handleClose}
              >
                Torna alla schermata di accesso
              </Button>
            </div>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4 pt-2">
            <div className="space-y-1.5">
              <label className="text-xs font-medium text-muted-foreground flex items-center gap-1.5">
                <Mail className="h-3.5 w-3.5 text-emerald-400" />
                Indirizzo Email
              </label>
              <Input
                type="email"
                placeholder="latuaemail@dominio.it"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                disabled={isLoading}
                className="text-xs"
                autoFocus
              />
            </div>

            <div className="flex flex-col-reverse sm:flex-row sm:justify-end gap-2 pt-2">
              <Button
                type="button"
                variant="ghost"
                onClick={handleClose}
                disabled={isLoading}
                className="text-xs"
              >
                Annulla
              </Button>
              <Button
                type="submit"
                variant="emerald"
                disabled={isLoading || !email.trim()}
                className="text-xs font-semibold gap-1.5"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="h-3.5 w-3.5 animate-spin" />
                    <span>Invio in corso...</span>
                  </>
                ) : (
                  <>
                    <span>Invia Link di Recupero</span>
                    <ArrowRight className="h-3.5 w-3.5" />
                  </>
                )}
              </Button>
            </div>
          </form>
        )}
      </DialogContent>
    </Dialog>
  )
}

import React, { useState } from "react"
import {
  Mail,
  ShieldCheck,
  Loader2,
} from "lucide-react"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { useCurrentUser } from "@/hooks/useAuth"
import { authApi } from "@/services/api/authApi"
import { toast } from "sonner"

export function UserEmailCard() {
  const { data: user } = useCurrentUser()
  const [newEmail, setNewEmail] = useState("")
  const [isChangingEmail, setIsChangingEmail] = useState(false)

  const handleEmailSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    const cleanEmail = newEmail.trim()

    if (!cleanEmail) {
      toast.error("Inserisci un indirizzo email valido.")
      return
    }

    if (user?.email && cleanEmail.toLowerCase() === user.email.toLowerCase()) {
      toast.error("Indirizzo identico", {
        description: "L'indirizzo email inserito coincide con quello attuale.",
      })
      return
    }

    setIsChangingEmail(true)
    try {
      const res = await authApi.changeEmail({
        new_email: cleanEmail,
      })
      toast.success("Richiesta inviata!", {
        description: res.message || "Controlla la casella di posta per confermare l'indirizzo.",
      })
      setNewEmail("")
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Errore durante la richiesta di cambio email"
      toast.error("Operazione fallita", { description: msg })
    } finally {
      setIsChangingEmail(false)
    }
  }

  return (
    <Card className="border-border/60 bg-card/60 backdrop-blur-sm shadow-md">
      <CardHeader>
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 shrink-0">
            <Mail className="h-5 w-5" />
          </div>
          <div>
            <CardTitle className="text-base font-bold">
              Modifica Indirizzo Email
            </CardTitle>
            <CardDescription className="text-xs text-muted-foreground mt-0.5">
              Cambia l&apos;email di accesso dell&apos;account con conferma di sicurezza a doppio indirizzo.
            </CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        <form onSubmit={handleEmailSubmit} className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-muted-foreground flex items-center gap-1.5">
              <Mail className="h-3.5 w-3.5 text-emerald-400" />
              Nuovo Indirizzo Email
            </label>
            <Input
              type="email"
              value={newEmail}
              onChange={(e) => setNewEmail(e.target.value)}
              placeholder="nuovoindirizzo@dominio.it"
              required
              disabled={isChangingEmail}
              className="text-xs"
            />
          </div>

          <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-[11px] text-emerald-300 flex items-start gap-2">
            <ShieldCheck className="h-4 w-4 shrink-0 mt-0.5 text-emerald-400" />
            <div className="leading-relaxed">
              Per salvaguardare la sicurezza del tuo account, riceverai un messaggio di convalida sia all&apos;indirizzo attuale che al nuovo. Il cambio diventerà effettivo una volta confermato il link.
            </div>
          </div>

          <div className="flex justify-end pt-1">
            <Button
              type="submit"
              variant="emerald"
              disabled={isChangingEmail || !newEmail.trim()}
              className="text-xs font-semibold gap-1.5 w-full sm:w-auto"
            >
              {isChangingEmail ? (
                <>
                  <Loader2 className="h-3.5 w-3.5 animate-spin" />
                  <span>Invio richiesta...</span>
                </>
              ) : (
                <>
                  <Mail className="h-3.5 w-3.5" />
                  <span>Richiedi Cambio Email</span>
                </>
              )}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  )
}

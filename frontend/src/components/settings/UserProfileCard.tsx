import { useState } from "react"
import {
  User,
  LogOut,
  ShieldCheck,
  AlertCircle,
  Loader2,
  Copy,
  Check,
  Palette,
} from "lucide-react"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { useCurrentUser, useLogout } from "@/hooks/useAuth"
import { useTheme } from "@/hooks/useTheme"
import { LogoutConfirmDialog } from "@/components/auth/LogoutConfirmDialog"
import { ThemeSelectionModal } from "@/components/theme/ThemeSelectionModal"
import { toast } from "sonner"

export { UserPasswordCard } from "./UserPasswordCard"
export { UserEmailCard } from "./UserEmailCard"

export function UserProfileCard() {
  const { data: user, isLoading, isError } = useCurrentUser()
  const { currentConfig } = useTheme()
  const logoutMutation = useLogout()
  const [logoutDialogOpen, setLogoutDialogOpen] = useState(false)
  const [themeModalOpen, setThemeModalOpen] = useState(false)
  const [copiedId, setCopiedId] = useState(false)

  const handleCopyId = () => {
    if (!user?.id) return
    navigator.clipboard.writeText(user.id)
    setCopiedId(true)
    toast.success("ID Utente copiato negli appunti")
    setTimeout(() => setCopiedId(false), 2000)
  }

  return (
    <>
      <Card className="border-border/60 bg-card/60 backdrop-blur-sm shadow-md">
        <CardHeader>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 items-start">
            <div className="flex items-start sm:items-center gap-3">
              <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 shrink-0 mt-0.5 sm:mt-0">
                <User className="h-5 w-5" />
              </div>
              <div>
                <CardTitle className="text-base font-bold">
                  Profilo Utente & Sessione
                </CardTitle>
                <CardDescription className="text-xs text-muted-foreground mt-0.5">
                  Identità autenticata e parametri operativi di sicurezza.
                </CardDescription>
              </div>
            </div>

            {user && (
              <Badge
                variant={user.is_demo ? "warning" : "success"}
                className="text-xs gap-1.5 shrink-0 self-start sm:self-auto"
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
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-3.5 rounded-xl bg-muted/20 border border-border/50">
                <div className="flex items-center gap-3.5 min-w-0">
                  <div className="h-11 w-11 rounded-full bg-gradient-to-br from-emerald-400 to-emerald-600 flex items-center justify-center text-slate-950 font-bold shadow-md shadow-emerald-500/20 shrink-0">
                    {user.email.substring(0, 2).toUpperCase()}
                  </div>
                  <div className="space-y-0.5 min-w-0">
                    <div className="text-sm font-semibold text-foreground truncate">
                      {user.email}
                    </div>
                    <div className="text-[11px] font-mono text-muted-foreground truncate flex items-center gap-1.5">
                      <span>ID: {user.id}</span>
                      <button
                        type="button"
                        onClick={handleCopyId}
                        className="text-muted-foreground hover:text-emerald-400 transition-colors focus:outline-none p-0.5 rounded"
                        title="Copia ID Utente"
                      >
                        {copiedId ? (
                          <Check className="h-3 w-3 text-emerald-400" />
                        ) : (
                          <Copy className="h-3 w-3" />
                        )}
                      </button>
                    </div>
                  </div>
                </div>

                <Button
                  variant="destructive"
                  size="sm"
                  onClick={() => setLogoutDialogOpen(true)}
                  disabled={logoutMutation.isPending}
                  className="gap-1.5 text-xs w-full sm:w-auto shrink-0"
                >
                  {logoutMutation.isPending ? (
                    <Loader2 className="h-3.5 w-3.5 animate-spin" />
                  ) : (
                    <LogOut className="h-3.5 w-3.5" />
                  )}
                  <span>Disconnetti</span>
                </Button>
              </div>

              <div className="text-xs text-muted-foreground space-y-1.5 p-3 rounded-lg bg-muted/10 border border-border/40">
                <div className="flex items-center justify-between">
                  <span>Tipo Sessione:</span>
                  <span className="font-medium text-foreground">
                    {user.is_demo ? "Demo Sandbox (Memoria/File Locale)" : "Bearer Token JWT (Supabase)"}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span>Persistenza Autenticazione:</span>
                  <span className="font-mono text-[11px] text-emerald-400">
                    LocalStorage (fpt_access_token)
                  </span>
                </div>
                <div className="flex items-center justify-between pt-1 border-t border-border/30">
                  <span>Tema Grafico:</span>
                  <button
                    type="button"
                    onClick={() => setThemeModalOpen(true)}
                    className="flex items-center gap-1.5 font-medium text-emerald-400 hover:text-emerald-300 hover:underline transition-colors focus:outline-none"
                    title="Modifica tema grafico"
                  >
                    <Palette className="h-3 w-3" />
                    <span>{currentConfig.name} (Modifica)</span>
                  </button>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      <LogoutConfirmDialog
        open={logoutDialogOpen}
        onOpenChange={setLogoutDialogOpen}
        onConfirm={() => {
          logoutMutation.mutate()
          setLogoutDialogOpen(false)
        }}
        isLoading={logoutMutation.isPending}
      />

      <ThemeSelectionModal
        open={themeModalOpen}
        onOpenChange={setThemeModalOpen}
      />
    </>
  )
}

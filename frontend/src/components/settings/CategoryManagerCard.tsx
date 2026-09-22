import React, { useState } from "react"
import { Wrench, Bell, Plus, X, Tag, Loader2, Sparkles } from "lucide-react"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import type { AppSettingsResponse } from "@/types/settings"
import {
  useAddMaintenanceCategory,
  useDeleteMaintenanceCategory,
  useAddReminderCategory,
  useDeleteReminderCategory,
} from "@/hooks/useSettings"
import { toast } from "sonner"

interface CategoryManagerCardProps {
  settings: AppSettingsResponse
}

export function CategoryManagerCard({ settings }: CategoryManagerCardProps) {
  // Hook mutazioni manutenzione
  const addMaintMutation = useAddMaintenanceCategory()
  const deleteMaintMutation = useDeleteMaintenanceCategory()

  // Hook mutazioni promemoria
  const addRemMutation = useAddReminderCategory()
  const deleteRemMutation = useDeleteReminderCategory()

  // Stati input locali
  const [newMaintInput, setNewMaintInput] = useState("")
  const [newRemInput, setNewRemInput] = useState("")

  // Categorie correnti
  const maintenanceCategories = settings.maintenance_types || []
  const reminderCategories = settings.reminder_types || []

  // Gestione aggiunta manutenzione
  const handleAddMaintenance = (e?: React.FormEvent) => {
    if (e) e.preventDefault()
    const trimmed = newMaintInput.trim()
    if (!trimmed) return

    if (
      maintenanceCategories.some(
        (c) => c.toLowerCase() === trimmed.toLowerCase()
      )
    ) {
      toast.error(`La categoria "${trimmed}" esiste già tra le manutenzioni.`)
      return
    }

    addMaintMutation.mutate(trimmed, {
      onSuccess: () => setNewMaintInput(""),
    })
  }

  // Gestione aggiunta promemoria
  const handleAddReminder = (e?: React.FormEvent) => {
    if (e) e.preventDefault()
    const trimmed = newRemInput.trim()
    if (!trimmed) return

    if (
      reminderCategories.some(
        (c) => c.toLowerCase() === trimmed.toLowerCase()
      )
    ) {
      toast.error(`La categoria "${trimmed}" esiste già tra i promemoria.`)
      return
    }

    addRemMutation.mutate(trimmed, {
      onSuccess: () => setNewRemInput(""),
    })
  }

  return (
    <Card className="border-border/60 bg-card/60 backdrop-blur-sm shadow-md">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
              <Tag className="h-5 w-5" />
            </div>
            <div>
              <CardTitle className="text-base font-bold">
                Gestione Categorie & Tag Interattivi
              </CardTitle>
              <CardDescription className="text-xs text-muted-foreground mt-0.5">
                Personalizza le etichette selezionabili nei moduli di registrazione interventi e controlli periodici.
              </CardDescription>
            </div>
          </div>
          <Badge variant="outline" className="text-xs gap-1 border-border/80">
            <Sparkles className="h-3 w-3 text-emerald-400" />
            Sincronizzazione Live
          </Badge>
        </div>
      </CardHeader>

      <CardContent className="space-y-8">
        {/* Sezione 1: Categorie Manutenzione */}
        <div className="space-y-3.5">
          <div className="flex items-center justify-between border-b border-border/40 pb-2">
            <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              <Wrench className="h-4 w-4 text-emerald-400" />
              <span>Tipologie di Manutenzione & Officina ({maintenanceCategories.length})</span>
            </div>
          </div>

          <p className="text-xs text-muted-foreground">
            Queste categorie compaiono nelle pillole di selezione rapida durante l&apos;inserimento di una nuova spesa di officina.
          </p>

          {/* Tag Cloud Interattivo */}
          <div className="flex flex-wrap gap-2 min-h-[36px] items-center p-3 rounded-xl bg-muted/20 border border-border/50">
            {maintenanceCategories.length === 0 ? (
              <span className="text-xs text-muted-foreground italic">
                Nessuna categoria definita. Aggiungine una sotto.
              </span>
            ) : (
              maintenanceCategories.map((cat) => {
                const isDeleting =
                  deleteMaintMutation.isPending &&
                  deleteMaintMutation.variables === cat

                return (
                  <span
                    key={cat}
                    className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-300 border border-emerald-500/25 shadow-sm transition-all hover:border-emerald-500/50"
                  >
                    <span>{cat}</span>
                    <button
                      type="button"
                      onClick={() => deleteMaintMutation.mutate(cat)}
                      disabled={deleteMaintMutation.isPending}
                      className="p-0.5 -mr-1 rounded-full hover:bg-emerald-500/20 text-emerald-400 hover:text-emerald-200 transition-colors disabled:opacity-50"
                      title={`Rimuovi categoria ${cat}`}
                    >
                      {isDeleting ? (
                        <Loader2 className="h-3 w-3 animate-spin" />
                      ) : (
                        <X className="h-3 w-3" />
                      )}
                    </button>
                  </span>
                )
              })
            )}
          </div>

          {/* Form Inserimento Nuovo Tag Manutenzione */}
          <form onSubmit={handleAddMaintenance} className="flex gap-2 max-w-md">
            <Input
              value={newMaintInput}
              onChange={(e) => setNewMaintInput(e.target.value)}
              placeholder="Es. Filtro Aria, Candele, Cinghia..."
              className="h-9 text-xs"
              disabled={addMaintMutation.isPending}
            />
            <Button
              type="submit"
              variant="emerald"
              size="sm"
              disabled={!newMaintInput.trim() || addMaintMutation.isPending}
              className="gap-1.5 text-xs font-semibold shrink-0"
            >
              {addMaintMutation.isPending ? (
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
              ) : (
                <Plus className="h-3.5 w-3.5" />
              )}
              <span>Aggiungi</span>
            </Button>
          </form>
        </div>

        {/* Sezione 2: Categorie Promemoria */}
        <div className="space-y-3.5 pt-2">
          <div className="flex items-center justify-between border-b border-border/40 pb-2">
            <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              <Bell className="h-4 w-4 text-cyan-400" />
              <span>Controlli Periodici & Promemoria ({reminderCategories.length})</span>
            </div>
          </div>

          <p className="text-xs text-muted-foreground">
            Questi promemoria ricorrenti definiscono le routine cicliche visualizzate nella schermata Promemoria.
          </p>

          {/* Tag Cloud Interattivo Promemoria */}
          <div className="flex flex-wrap gap-2 min-h-[36px] items-center p-3 rounded-xl bg-muted/20 border border-border/50">
            {reminderCategories.length === 0 ? (
              <span className="text-xs text-muted-foreground italic">
                Nessuna categoria promemoria configurata.
              </span>
            ) : (
              reminderCategories.map((cat) => {
                const isDeleting =
                  deleteRemMutation.isPending &&
                  deleteRemMutation.variables === cat

                return (
                  <span
                    key={cat}
                    className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-cyan-500/10 text-cyan-300 border border-cyan-500/25 shadow-sm transition-all hover:border-cyan-500/50"
                  >
                    <span>{cat}</span>
                    <button
                      type="button"
                      onClick={() => deleteRemMutation.mutate(cat)}
                      disabled={deleteRemMutation.isPending}
                      className="p-0.5 -mr-1 rounded-full hover:bg-cyan-500/20 text-cyan-400 hover:text-cyan-200 transition-colors disabled:opacity-50"
                      title={`Rimuovi promemoria ${cat}`}
                    >
                      {isDeleting ? (
                        <Loader2 className="h-3 w-3 animate-spin" />
                      ) : (
                        <X className="h-3 w-3" />
                      )}
                    </button>
                  </span>
                )
              })
            )}
          </div>

          {/* Form Inserimento Nuovo Tag Promemoria */}
          <form onSubmit={handleAddReminder} className="flex gap-2 max-w-md">
            <Input
              value={newRemInput}
              onChange={(e) => setNewRemInput(e.target.value)}
              placeholder="Es. Pressione Gomme, Livello Refrigerante..."
              className="h-9 text-xs"
              disabled={addRemMutation.isPending}
            />
            <Button
              type="submit"
              variant="outline"
              size="sm"
              disabled={!newRemInput.trim() || addRemMutation.isPending}
              className="gap-1.5 text-xs font-semibold shrink-0 border-cyan-500/30 text-cyan-300 hover:bg-cyan-950/20 hover:text-cyan-200"
            >
              {addRemMutation.isPending ? (
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
              ) : (
                <Plus className="h-3.5 w-3.5" />
              )}
              <span>Aggiungi</span>
            </Button>
          </form>
        </div>
      </CardContent>
    </Card>
  )
}

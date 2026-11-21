import { useState } from "react"
import {
  CalendarClock,
  Plus,
  History,
  AlertCircle,
  CheckCircle2,
  RefreshCw,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Skeleton } from "@/components/ui/skeleton"
import { useReminders } from "@/hooks/useReminders"
import { ReminderCard } from "@/components/reminders/ReminderCard"
import { ReminderFormModal } from "@/components/reminders/ReminderFormModal"
import { ReminderHistoryModal } from "@/components/reminders/ReminderHistoryModal"
import type { ReminderResponse } from "@/types"

export default function RemindersPage() {
  const [isFormOpen, setIsFormOpen] = useState(false)
  const [isHistoryOpen, setIsHistoryOpen] = useState(false)
  const [editingReminder, setEditingReminder] = useState<ReminderResponse | null>(null)

  const { data: reminders, isLoading, isError, refetch } = useReminders()

  const overdueCount = reminders?.filter((r) => r.is_overdue).length || 0
  const urgentCount =
    reminders?.filter((r) => r.progress >= 0.7 && !r.is_overdue).length || 0

  const handleStartCreate = () => {
    setEditingReminder(null)
    setIsFormOpen(true)
  }

  const handleStartEdit = (reminder: ReminderResponse) => {
    setEditingReminder(reminder)
    setIsFormOpen(true)
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-extrabold tracking-tight flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-rose-500/10 text-rose-400">
              <CalendarClock className="h-5 w-5" />
            </div>
            Scadenze & Promemoria di Routine
          </h2>
          <p className="text-sm text-muted-foreground mt-1">
            Controlli ciclici chilometrici e temporali per preservare l&apos;affidabilità e la sicurezza dell&apos;auto.
          </p>
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <Button
            variant="outline"
            size="sm"
            className="gap-1.5 flex-1 sm:flex-none border-border/80 hover:border-emerald-500/50"
            onClick={() => setIsHistoryOpen(true)}
          >
            <History className="h-4 w-4 text-emerald-400" />
            <span>Storico Controlli</span>
          </Button>

          <Button
            variant="emerald"
            size="sm"
            className="gap-1.5 flex-1 sm:flex-none"
            onClick={handleStartCreate}
          >
            <Plus className="h-4 w-4" />
            <span>Nuovo Promemoria</span>
          </Button>
        </div>
      </div>

      {/* Urgent Warning Banner (if overdue or approaching threshold) */}
      {overdueCount > 0 ? (
        <div className="rounded-2xl border border-rose-500/40 bg-rose-500/10 p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-sm animate-in fade-in-50">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-rose-500/20 text-rose-400 shrink-0">
              <AlertCircle className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-rose-300">
                {overdueCount} {overdueCount === 1 ? "controllo scaduto" : "controlli scaduti"} richiedono verifica immediata
              </h3>
              <p className="text-xs text-rose-200/80 mt-0.5">
                Il limite chilometrico o temporale è stato superato. Esegui il controllo e premi &quot;Segna come Eseguito&quot;.
              </p>
            </div>
          </div>
          <Badge variant="destructive" className="shrink-0 self-start sm:self-auto">
            Azione Richiesta
          </Badge>
        </div>
      ) : urgentCount > 0 ? (
        <div className="rounded-2xl border border-amber-500/40 bg-amber-500/10 p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-sm animate-in fade-in-50">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-amber-500/20 text-amber-400 shrink-0">
              <AlertCircle className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-amber-300">
                {urgentCount} {urgentCount === 1 ? "controllo in avvicinamento" : "controlli in avvicinamento"}
              </h3>
              <p className="text-xs text-amber-200/80 mt-0.5">
                Alcune verifiche periodiche hanno superato il 70% del ciclo pianificato.
              </p>
            </div>
          </div>
          <Badge variant="warning" className="shrink-0 self-start sm:self-auto">
            In Scadenza
          </Badge>
        </div>
      ) : (
        <div className="rounded-2xl border border-emerald-500/20 bg-emerald-500/5 p-4 flex items-center justify-between gap-3">
          <div className="flex items-center gap-2.5 text-xs text-muted-foreground">
            <CheckCircle2 className="h-4 w-4 text-emerald-400" />
            <span>Tutti i controlli e le verifiche di routine sono attualmente in regola.</span>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => refetch()}
            className="h-8 w-8 p-0 text-muted-foreground hover:text-foreground"
          >
            <RefreshCw className="h-3.5 w-3.5" />
          </Button>
        </div>
      )}

      {/* Main Grid of Reminders */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-48 w-full rounded-2xl" />
          ))}
        </div>
      ) : isError ? (
        <div className="p-12 text-center text-muted-foreground space-y-3 rounded-2xl border border-border/60">
          <p className="text-rose-400 text-sm">
            Si è verificato un errore durante il recupero dei promemoria.
          </p>
          <Button variant="outline" size="sm" onClick={() => refetch()}>
            Riprova
          </Button>
        </div>
      ) : !reminders || reminders.length === 0 ? (
        <div className="p-12 text-center text-muted-foreground space-y-3 rounded-2xl border border-dashed border-border/60">
          <div className="mx-auto w-12 h-12 rounded-full bg-muted/40 flex items-center justify-center text-muted-foreground">
            <CalendarClock className="h-6 w-6" />
          </div>
          <p className="text-sm font-medium">Nessun promemoria configurato.</p>
          <p className="text-xs text-muted-foreground">
            Crea il tuo primo promemoria ricorrente per non dimenticare controlli pressione, livelli o filtri.
          </p>
          <Button variant="emerald" size="sm" onClick={handleStartCreate} className="mt-2">
            <Plus className="h-4 w-4 mr-1.5" />
            Configura Promemoria
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {reminders.map((rem) => (
            <ReminderCard
              key={rem.id}
              reminder={rem}
              onEdit={handleStartEdit}
            />
          ))}
        </div>
      )}

      {/* Form Modal: Nuovo / Modifica */}
      <ReminderFormModal
        open={isFormOpen}
        onOpenChange={setIsFormOpen}
        initialData={editingReminder}
      />

      {/* History Log Modal */}
      <ReminderHistoryModal
        open={isHistoryOpen}
        onOpenChange={setIsHistoryOpen}
      />
    </div>
  )
}

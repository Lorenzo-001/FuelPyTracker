import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { settingsApi } from "@/services/api/settingsApi"
import type { AppSettingsResponse, AppSettingsUpdate } from "@/types/settings"
import { toast } from "sonner"

export const SETTINGS_QUERY_KEY = ["settings"] as const

/**
 * Hook per leggere la configurazione utente, le soglie e le categorie attive.
 */
export function useSettings() {
  return useQuery<AppSettingsResponse>({
    queryKey: SETTINGS_QUERY_KEY,
    queryFn: () => settingsApi.getSettings(),
    staleTime: 1000 * 60, // 1 minuto
  })
}

/**
 * Mutazione per aggiornare soglie di spesa, limiti di importazione o preferenze OCR.
 */
export function useUpdateSettings() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (payload: AppSettingsUpdate) => settingsApi.updateSettings(payload),
    onSuccess: (updated) => {
      queryClient.setQueryData(SETTINGS_QUERY_KEY, updated)
      queryClient.invalidateQueries({ queryKey: SETTINGS_QUERY_KEY })
      toast.success("Impostazioni salvate con successo!")
    },
    onError: (err: Error) => {
      toast.error(`Impossibile salvare le impostazioni: ${err.message}`)
    },
  })
}

/**
 * Mutazione per aggiungere una tipologia di manutenzione.
 */
export function useAddMaintenanceCategory() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (category: string) => settingsApi.addMaintenanceCategory(category),
    onSuccess: (updated) => {
      queryClient.setQueryData(SETTINGS_QUERY_KEY, updated)
      queryClient.invalidateQueries({ queryKey: SETTINGS_QUERY_KEY })
      queryClient.invalidateQueries({ queryKey: ["maintenance"] })
      toast.success("Categoria manutenzione aggiunta")
    },
    onError: (err: Error) => {
      toast.error(`Errore aggiunta categoria: ${err.message}`)
    },
  })
}

/**
 * Mutazione per eliminare una tipologia di manutenzione.
 */
export function useDeleteMaintenanceCategory() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (category: string) => settingsApi.deleteMaintenanceCategory(category),
    onSuccess: (updated) => {
      queryClient.setQueryData(SETTINGS_QUERY_KEY, updated)
      queryClient.invalidateQueries({ queryKey: SETTINGS_QUERY_KEY })
      queryClient.invalidateQueries({ queryKey: ["maintenance"] })
      toast.success("Categoria manutenzione rimossa")
    },
    onError: (err: Error) => {
      toast.error(`Errore rimozione categoria: ${err.message}`)
    },
  })
}

/**
 * Mutazione per aggiungere una categoria di promemoria.
 */
export function useAddReminderCategory() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (category: string) => settingsApi.addReminderCategory(category),
    onSuccess: (updated) => {
      queryClient.setQueryData(SETTINGS_QUERY_KEY, updated)
      queryClient.invalidateQueries({ queryKey: SETTINGS_QUERY_KEY })
      queryClient.invalidateQueries({ queryKey: ["reminders"] })
      toast.success("Categoria promemoria aggiunta")
    },
    onError: (err: Error) => {
      toast.error(`Errore aggiunta promemoria: ${err.message}`)
    },
  })
}

/**
 * Mutazione per eliminare una categoria di promemoria.
 */
export function useDeleteReminderCategory() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (category: string) => settingsApi.deleteReminderCategory(category),
    onSuccess: (updated) => {
      queryClient.setQueryData(SETTINGS_QUERY_KEY, updated)
      queryClient.invalidateQueries({ queryKey: SETTINGS_QUERY_KEY })
      queryClient.invalidateQueries({ queryKey: ["reminders"] })
      toast.success("Categoria promemoria rimossa")
    },
    onError: (err: Error) => {
      toast.error(`Errore rimozione promemoria: ${err.message}`)
    },
  })
}

import { apiClient } from "./client"
import type {
  AppSettingsResponse,
  AppSettingsUpdate,
  CategoryOperationRequest,
} from "@/types/settings"

export const settingsApi = {
  /**
   * Recupera le impostazioni operative e le categorie utente attuali.
   */
  getSettings: (): Promise<AppSettingsResponse> => {
    return apiClient.get<AppSettingsResponse>("/settings")
  },

  /**
   * Aggiorna parzialmente o totalmente le soglie operative e i limiti.
   */
  updateSettings: (payload: AppSettingsUpdate): Promise<AppSettingsResponse> => {
    return apiClient.put<AppSettingsResponse>("/settings", payload)
  },

  /**
   * Aggiunge una nuova tipologia di manutenzione.
   */
  addMaintenanceCategory: (category: string): Promise<AppSettingsResponse> => {
    const payload: CategoryOperationRequest = { category }
    return apiClient.post<AppSettingsResponse>("/settings/maintenance-categories", payload)
  },

  /**
   * Rimuove una tipologia di manutenzione esistente.
   */
  deleteMaintenanceCategory: (category: string): Promise<AppSettingsResponse> => {
    return apiClient.delete<AppSettingsResponse>(
      `/settings/maintenance-categories/${encodeURIComponent(category)}`
    )
  },

  /**
   * Aggiunge una nuova categoria per i promemoria.
   */
  addReminderCategory: (category: string): Promise<AppSettingsResponse> => {
    const payload: CategoryOperationRequest = { category }
    return apiClient.post<AppSettingsResponse>("/settings/reminder-categories", payload)
  },

  /**
   * Rimuove una categoria dai promemoria.
   */
  deleteReminderCategory: (category: string): Promise<AppSettingsResponse> => {
    return apiClient.delete<AppSettingsResponse>(
      `/settings/reminder-categories/${encodeURIComponent(category)}`
    )
  },
}

import { apiClient } from "./client"
import type {
  ReminderResponse,
  ReminderCreate,
  ReminderUpdate,
  ReminderExecutionRequest,
} from "@/types"

export interface ReminderHistoryItem {
  id: number
  user_id: string
  reminder_id: number
  date_checked: string
  km_checked: number
  notes?: string | null
}

export const remindersApi = {
  getReminders: (): Promise<ReminderResponse[]> => {
    return apiClient.get<ReminderResponse[]>("/reminders")
  },

  getReminderById: (id: number): Promise<ReminderResponse> => {
    return apiClient.get<ReminderResponse>(`/reminders/${id}`)
  },

  createReminder: (data: ReminderCreate): Promise<ReminderResponse> => {
    return apiClient.post<ReminderResponse>("/reminders", data)
  },

  updateReminder: (id: number, data: ReminderUpdate): Promise<ReminderResponse> => {
    return apiClient.put<ReminderResponse>(`/reminders/${id}`, data)
  },

  deleteReminder: (id: number): Promise<{ success: boolean; message: string }> => {
    return apiClient.delete<{ success: boolean; message: string }>(`/reminders/${id}`)
  },

  completeReminder: (
    id: number,
    data: ReminderExecutionRequest = {}
  ): Promise<ReminderResponse> => {
    return apiClient.post<ReminderResponse>(`/reminders/${id}/complete`, data)
  },

  getHistory: (limit: number = 20): Promise<ReminderHistoryItem[]> => {
    return apiClient.get<ReminderHistoryItem[]>("/reminders/history", {
      params: { limit },
    })
  },
}

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { remindersApi, type ReminderHistoryItem } from "@/services/api/remindersApi"
import type {
  ReminderResponse,
  ReminderCreate,
  ReminderUpdate,
  ReminderExecutionRequest,
} from "@/types"

export const REMINDER_KEYS = {
  all: ["reminders"] as const,
  list: () => [...REMINDER_KEYS.all, "list"] as const,
  history: (limit?: number) => [...REMINDER_KEYS.all, "history", limit] as const,
}

export function useReminders() {
  return useQuery<ReminderResponse[]>({
    queryKey: REMINDER_KEYS.list(),
    queryFn: () => remindersApi.getReminders(),
    staleTime: 1000 * 60 * 2,
  })
}

export function useReminderHistory(limit: number = 20) {
  return useQuery<ReminderHistoryItem[]>({
    queryKey: REMINDER_KEYS.history(limit),
    queryFn: () => remindersApi.getHistory(limit),
    staleTime: 1000 * 60 * 2,
  })
}

export function useCreateReminder() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: ReminderCreate) => remindersApi.createReminder(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: REMINDER_KEYS.all })
      queryClient.invalidateQueries({ queryKey: ["dashboard"] })
    },
  })
}

export function useUpdateReminder() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: ReminderUpdate }) =>
      remindersApi.updateReminder(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: REMINDER_KEYS.all })
      queryClient.invalidateQueries({ queryKey: ["dashboard"] })
    },
  })
}

export function useDeleteReminder() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: number) => remindersApi.deleteReminder(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: REMINDER_KEYS.all })
      queryClient.invalidateQueries({ queryKey: ["dashboard"] })
    },
  })
}

export function useCompleteReminder() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data?: ReminderExecutionRequest }) =>
      remindersApi.completeReminder(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: REMINDER_KEYS.all })
      queryClient.invalidateQueries({ queryKey: ["dashboard"] })
    },
  })
}

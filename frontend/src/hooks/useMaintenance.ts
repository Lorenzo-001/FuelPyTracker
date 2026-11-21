import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { maintenanceApi } from "@/services/api/maintenanceApi"
import type {
  MaintenanceResponse,
  MaintenanceCreate,
  MaintenanceUpdate,
  MaintenanceDeadlineResponse,
} from "@/types"

export const MAINTENANCE_KEYS = {
  all: ["maintenance"] as const,
  lists: () => [...MAINTENANCE_KEYS.all, "list"] as const,
  list: (year?: number, expense_type?: string) =>
    [...MAINTENANCE_KEYS.lists(), { year, expense_type }] as const,
  categories: () => [...MAINTENANCE_KEYS.all, "categories"] as const,
  deadlines: () => [...MAINTENANCE_KEYS.all, "deadlines"] as const,
}

export function useMaintenances(year?: number, expense_type?: string) {
  return useQuery<MaintenanceResponse[]>({
    queryKey: MAINTENANCE_KEYS.list(year, expense_type),
    queryFn: () => maintenanceApi.getMaintenances(year, expense_type),
    staleTime: 1000 * 60 * 2,
  })
}

export function useMaintenanceCategories() {
  return useQuery<string[]>({
    queryKey: MAINTENANCE_KEYS.categories(),
    queryFn: () => maintenanceApi.getCategories(),
    staleTime: 1000 * 60 * 5,
  })
}

export function useMaintenanceDeadlines() {
  return useQuery<MaintenanceDeadlineResponse[]>({
    queryKey: MAINTENANCE_KEYS.deadlines(),
    queryFn: () => maintenanceApi.getDeadlines(),
    staleTime: 1000 * 60 * 2,
  })
}

export function useCreateMaintenance() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: MaintenanceCreate) => maintenanceApi.createMaintenance(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: MAINTENANCE_KEYS.all })
      queryClient.invalidateQueries({ queryKey: ["dashboard"] })
    },
  })
}

export function useUpdateMaintenance() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: MaintenanceUpdate }) =>
      maintenanceApi.updateMaintenance(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: MAINTENANCE_KEYS.all })
      queryClient.invalidateQueries({ queryKey: ["dashboard"] })
    },
  })
}

export function useDeleteMaintenance() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: number) => maintenanceApi.deleteMaintenance(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: MAINTENANCE_KEYS.all })
      queryClient.invalidateQueries({ queryKey: ["dashboard"] })
    },
  })
}

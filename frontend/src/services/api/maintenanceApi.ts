import { apiClient } from "./client"
import type {
  MaintenanceResponse,
  MaintenanceCreate,
  MaintenanceUpdate,
  MaintenanceDeadlineResponse,
} from "@/types"

export const maintenanceApi = {
  getMaintenances: (
    year?: number,
    expense_type?: string
  ): Promise<MaintenanceResponse[]> => {
    return apiClient.get<MaintenanceResponse[]>("/maintenance", {
      params: {
        ...(year ? { year } : {}),
        ...(expense_type ? { expense_type } : {}),
      },
    })
  },

  getMaintenanceById: (id: number): Promise<MaintenanceResponse> => {
    return apiClient.get<MaintenanceResponse>(`/maintenance/${id}`)
  },

  createMaintenance: (data: MaintenanceCreate): Promise<MaintenanceResponse> => {
    return apiClient.post<MaintenanceResponse>("/maintenance", data)
  },

  updateMaintenance: (
    id: number,
    data: MaintenanceUpdate
  ): Promise<MaintenanceResponse> => {
    return apiClient.put<MaintenanceResponse>(`/maintenance/${id}`, data)
  },

  deleteMaintenance: (id: number): Promise<{ success: boolean; message: string }> => {
    return apiClient.delete<{ success: boolean; message: string }>(`/maintenance/${id}`)
  },

  getCategories: (): Promise<string[]> => {
    return apiClient.get<string[]>("/maintenance/categories")
  },

  getDeadlines: (): Promise<MaintenanceDeadlineResponse[]> => {
    return apiClient.get<MaintenanceDeadlineResponse[]>("/maintenance/deadlines")
  },
}

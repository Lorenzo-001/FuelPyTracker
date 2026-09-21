import { apiClient } from "./client"
import type { HealthCheckResponse } from "@/types"

export const systemApi = {
  getHealth: (): Promise<HealthCheckResponse> => {
    return apiClient.get<HealthCheckResponse>("/health")
  },
}

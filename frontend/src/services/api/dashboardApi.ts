import { apiClient } from "./client"
import type {
  DashboardSummaryResponse,
  DashboardChartsResponse,
  TripCalculationRequest,
  TripCalculationResponse,
} from "@/types"

export const dashboardApi = {
  getSummary: (): Promise<DashboardSummaryResponse> => {
    return apiClient.get<DashboardSummaryResponse>("/dashboard/summary")
  },

  getCharts: (): Promise<DashboardChartsResponse> => {
    return apiClient.get<DashboardChartsResponse>("/dashboard/charts")
  },

  calculateTrip: (
    payload: TripCalculationRequest
  ): Promise<TripCalculationResponse> => {
    return apiClient.post<TripCalculationResponse>(
      "/dashboard/trip-calculator",
      payload
    )
  },
}

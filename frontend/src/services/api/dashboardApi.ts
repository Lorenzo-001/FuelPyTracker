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

  getCharts: (time_range: string = "all"): Promise<DashboardChartsResponse> => {
    return apiClient.get<DashboardChartsResponse>("/dashboard/charts", {
      params: { time_range },
    })
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

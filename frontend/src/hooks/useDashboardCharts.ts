import { useQuery } from "@tanstack/react-query"
import { dashboardApi } from "@/services/api/dashboardApi"

export function useDashboardCharts(timeRange: string = "ytd") {
  return useQuery({
    queryKey: ["dashboard", "charts", timeRange],
    queryFn: () => dashboardApi.getCharts(timeRange),
    staleTime: 60000,
    retry: 1,
  })
}

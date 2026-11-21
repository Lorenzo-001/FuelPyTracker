import { useQuery } from "@tanstack/react-query"
import { dashboardApi } from "@/services/api/dashboardApi"

export function useDashboardSummary(time_range: string = "ytd") {
  return useQuery({
    queryKey: ["dashboard", "summary", time_range],
    queryFn: () => dashboardApi.getSummary(time_range),
    staleTime: 60000, // 1 minute
    retry: 1,
  })
}

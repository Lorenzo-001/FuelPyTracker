import { useQuery } from "@tanstack/react-query"
import { dashboardApi } from "@/services/api/dashboardApi"

export function useDashboardSummary() {
  return useQuery({
    queryKey: ["dashboard", "summary"],
    queryFn: () => dashboardApi.getSummary(),
    staleTime: 60000, // 1 minute
    retry: 1,
  })
}

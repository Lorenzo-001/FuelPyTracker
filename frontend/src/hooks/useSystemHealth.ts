import { useQuery } from "@tanstack/react-query"
import { systemApi } from "@/services/api/systemApi"

export function useSystemHealth() {
  return useQuery({
    queryKey: ["system", "health"],
    queryFn: () => systemApi.getHealth(),
    refetchInterval: 15000, // Check backend pulse every 15 seconds
    retry: 1,
    staleTime: 10000,
  })
}

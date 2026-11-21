import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { fuelApi } from "@/services/api/fuelApi"
import type {
  RefuelingResponse,
  RefuelingCreate,
  RefuelingUpdate,
  RefuelingValidationRequest,
} from "@/types"

export const FUEL_KEYS = {
  all: ["fuel"] as const,
  lists: () => [...FUEL_KEYS.all, "list"] as const,
  list: (year?: number) => [...FUEL_KEYS.lists(), { year }] as const,
  detail: (id: number) => [...FUEL_KEYS.all, "detail", id] as const,
}

export function useRefuelings(year?: number) {
  return useQuery<RefuelingResponse[]>({
    queryKey: FUEL_KEYS.list(year),
    queryFn: () => fuelApi.getRefuelings(year),
    staleTime: 1000 * 60 * 2, // 2 minuti
  })
}

export function useCreateRefueling() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data: RefuelingCreate) => fuelApi.createRefueling(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FUEL_KEYS.all })
      queryClient.invalidateQueries({ queryKey: ["dashboard"] })
    },
  })
}

export function useUpdateRefueling() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: RefuelingUpdate }) =>
      fuelApi.updateRefueling(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FUEL_KEYS.all })
      queryClient.invalidateQueries({ queryKey: ["dashboard"] })
    },
  })
}

export function useDeleteRefueling() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (id: number) => fuelApi.deleteRefueling(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: FUEL_KEYS.all })
      queryClient.invalidateQueries({ queryKey: ["dashboard"] })
    },
  })
}

export function useValidateRefueling() {
  return useMutation({
    mutationFn: (data: RefuelingValidationRequest) => fuelApi.validateRefueling(data),
  })
}

export function useScanReceiptOcr() {
  return useMutation({
    mutationFn: (file: File) => fuelApi.scanReceiptOcr(file),
  })
}

export function useOcrStatus() {
  return useQuery({
    queryKey: ["ocr", "status"],
    queryFn: () => fuelApi.getOcrStatus(),
    staleTime: 1000 * 60 * 5, // 5 minuti
  })
}

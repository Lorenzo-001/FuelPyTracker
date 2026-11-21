import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { reportsApi } from "@/services/api/reportsApi"
import type {
  ExportStatsResponse,
  PDFReportRequest,
  ImportCommitPayload,
  ImportCommitResponse,
  ImportPreviewResponse,
  ImportRevalidatePayload,
} from "@/types"

export const REPORT_KEYS = {
  all: ["reports"] as const,
  stats: () => [...REPORT_KEYS.all, "stats"] as const,
}

export function useExportStats() {
  return useQuery<ExportStatsResponse>({
    queryKey: REPORT_KEYS.stats(),
    queryFn: () => reportsApi.getStats(),
    staleTime: 1000 * 60 * 2,
  })
}

export function useDownloadExcel() {
  return useMutation({
    mutationFn: () => reportsApi.downloadExcel(),
  })
}

export function useDownloadTemplate() {
  return useMutation({
    mutationFn: () => reportsApi.downloadTemplate(),
  })
}

export function useGeneratePdf() {
  return useMutation({
    mutationFn: (params: PDFReportRequest) => reportsApi.generatePdf(params),
  })
}

export function usePreviewImport() {
  return useMutation<ImportPreviewResponse, Error, File>({
    mutationFn: (file: File) => reportsApi.previewImport(file),
  })
}

export function useRevalidateImport() {
  return useMutation<ImportPreviewResponse, Error, ImportRevalidatePayload>({
    mutationFn: (payload: ImportRevalidatePayload) => reportsApi.revalidateImport(payload),
  })
}

export function useCommitImport() {
  const queryClient = useQueryClient()

  return useMutation<ImportCommitResponse, Error, ImportCommitPayload>({
    mutationFn: (payload: ImportCommitPayload) => reportsApi.commitImport(payload),
    onSuccess: () => {
      // Invalida tutti i domini aggiornati dall'importazione massiva
      queryClient.invalidateQueries({ queryKey: ["fuel"] })
      queryClient.invalidateQueries({ queryKey: ["maintenance"] })
      queryClient.invalidateQueries({ queryKey: ["dashboard"] })
      queryClient.invalidateQueries({ queryKey: ["reports"] })
      queryClient.invalidateQueries({ queryKey: ["reminders"] })
    },
  })
}

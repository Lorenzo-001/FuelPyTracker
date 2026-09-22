import { apiClient, triggerFileDownload } from "./client"
import type {
  ExportStatsResponse,
  PDFReportRequest,
  ImportPreviewResponse,
  ImportCommitPayload,
  ImportCommitResponse,
  ImportRevalidatePayload,
} from "@/types"

export const reportsApi = {
  /**
   * Recupera statistiche rapide sull'archivio esportabile (conteggio pieni e tagliandi).
   */
  getStats: async (): Promise<ExportStatsResponse> => {
    return apiClient.get<ExportStatsResponse>("/reports/stats")
  },

  /**
   * Genera e avvia il download dell'archivio Excel multi-foglio con stili professionali.
   */
  downloadExcel: async (): Promise<void> => {
    const { blob, filename } = await apiClient.getBlob("/reports/excel")
    triggerFileDownload(blob, filename || `fuelpytracker_backup_${new Date().toISOString().split("T")[0]}.xlsx`)
  },

  /**
   * Scarica il modello Excel vuoto pre-formattato con intestazioni e colonne standard.
   */
  downloadTemplate: async (): Promise<void> => {
    const { blob, filename } = await apiClient.getBlob("/reports/template")
    triggerFileDownload(blob, filename || "FuelPyTracker_Template.xlsx")
  },

  /**
   * Compila e scarica il Libretto Manutenzione Digitale in formato PDF.
   */
  generatePdf: async (params: PDFReportRequest): Promise<void> => {
    const { blob, filename } = await apiClient.postBlob("/reports/pdf", params)
    const fallbackName = `Libretto_Manutenzione_${params.plate.toUpperCase().trim() || "veicolo"}.pdf`
    triggerFileDownload(blob, filename || fallbackName)
  },

  /**
   * Carica un file CSV o Excel per l'analisi preliminare di staging pre-commit.
   */
  previewImport: async (file: File): Promise<ImportPreviewResponse> => {
    const formData = new FormData()
    formData.append("file", file)
    return apiClient.post<ImportPreviewResponse>("/reports/import/preview", formData)
  },

  /**
   * Ri-valida asincronamente le righe corrette dall'utente in staging.
   */
  revalidateImport: async (payload: ImportRevalidatePayload): Promise<ImportPreviewResponse> => {
    return apiClient.post<ImportPreviewResponse>("/reports/import/revalidate", payload)
  },

  /**
   * Esegue il commit transazionale delle righe convalidate salvandole a database.
   */
  commitImport: async (payload: ImportCommitPayload): Promise<ImportCommitResponse> => {
    return apiClient.post<ImportCommitResponse>("/reports/import/commit", payload)
  },
}

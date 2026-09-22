import { apiClient } from "./client"
import type {
  RefuelingResponse,
  RefuelingCreate,
  RefuelingUpdate,
  RefuelingValidationRequest,
  RefuelingValidationResponse,
  OCRScanResponse,
} from "@/types"

export const fuelApi = {
  getRefuelings: (year?: number): Promise<RefuelingResponse[]> => {
    return apiClient.get<RefuelingResponse[]>("/fuel", {
      params: year ? { year } : undefined,
    })
  },

  getRefuelingById: (id: number): Promise<RefuelingResponse> => {
    return apiClient.get<RefuelingResponse>(`/fuel/${id}`)
  },

  createRefueling: (data: RefuelingCreate): Promise<RefuelingResponse> => {
    return apiClient.post<RefuelingResponse>("/fuel", data)
  },

  updateRefueling: (id: number, data: RefuelingUpdate): Promise<RefuelingResponse> => {
    return apiClient.put<RefuelingResponse>(`/fuel/${id}`, data)
  },

  deleteRefueling: (id: number): Promise<{ success: boolean; message: string }> => {
    return apiClient.delete<{ success: boolean; message: string }>(`/fuel/${id}`)
  },

  validateRefueling: (
    data: RefuelingValidationRequest
  ): Promise<RefuelingValidationResponse> => {
    return apiClient.post<RefuelingValidationResponse>("/fuel/validate", data)
  },

  scanReceiptOcr: (file: File): Promise<OCRScanResponse> => {
    const formData = new FormData()
    formData.append("file", file)
    return apiClient.post<OCRScanResponse>("/fuel/ocr", formData)
  },
}


export interface ExportStatsResponse {
  refuelings_count: number
  maintenances_count: number
  years_available: number[]
}

export interface PDFReportRequest {
  owner_name: string
  plate: string
  car_model: string
  year?: number | null
}

export interface ImportSummary {
  new?: number
  update?: number
  warning?: number
  error?: number
  ok?: number
  [key: string]: number | undefined
}

export interface ImportPreviewResponse {
  success: boolean
  global_error?: string | null
  fuel_rows: Record<string, unknown>[]
  fuel_summary: ImportSummary
  maintenance_rows: Record<string, unknown>[]
  maintenance_summary: ImportSummary
}

export interface ImportCommitRowFuel {
  date: string
  total_km: number
  price_per_liter: number
  total_cost: number
  liters: number
  is_full_tank: boolean
  notes?: string | null
  db_id?: number | null
  status: string
}

export interface ImportCommitRowMaintenance {
  date: string
  total_km: number
  expense_type: string
  cost: number
  description?: string | null
  expiry_km?: number | null
  expiry_date?: string | null
  db_id?: number | null
  status: string
}

export interface ImportCommitPayload {
  fuel_rows: ImportCommitRowFuel[]
  maintenance_rows: ImportCommitRowMaintenance[]
}

export interface ImportCommitResponse {
  success: boolean
  fuel_inserted: number
  fuel_updated: number
  maintenance_inserted: number
  maintenance_updated: number
  message: string
}

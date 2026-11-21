export interface MaintenanceBase {
  date: string
  total_km: number
  expense_type: string
  cost: number
  description?: string | null
  expiry_km?: number | null
  expiry_date?: string | null
}

export type MaintenanceCreate = MaintenanceBase

export interface MaintenanceUpdate {
  date?: string
  total_km?: number
  expense_type?: string
  cost?: number
  description?: string | null
  expiry_km?: number | null
  expiry_date?: string | null
}

export interface MaintenanceResponse extends MaintenanceBase {
  id: number
  user_id: string
}

export interface MaintenanceDeadlineResponse {
  id: number
  expense_type: string
  date: string
  total_km: number
  cost: number
  expiry_km: number | null
  expiry_date: string | null
  km_left: number | null
  days_left: number | null
  priority: number
  status_color: string
  predicted_date: string | null
}

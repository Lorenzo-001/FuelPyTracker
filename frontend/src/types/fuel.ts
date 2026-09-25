export interface RefuelingBase {
  date: string
  total_km: number
  price_per_liter: number
  total_cost: number
  liters: number
  is_full_tank: boolean
  notes?: string | null
}

export type RefuelingCreate = RefuelingBase

export interface RefuelingUpdate {
  date?: string
  total_km?: number
  price_per_liter?: number
  total_cost?: number
  liters?: number
  is_full_tank?: boolean
  notes?: string | null
}

export interface RefuelingResponse extends RefuelingBase {
  id: number
  user_id: string
  delta_km: number | null
  km_per_liter: number | null
  days_since_last: number | null
}

export interface RefuelingValidationRequest {
  date: string
  km: number
  price: number
  cost: number
  is_full: boolean
}

export interface RefuelingValidationResponse {
  is_valid: boolean
  message: string
  prev_km: number | null
  next_km: number | null
}

export interface OCRScanResponse {
  success: boolean
  total_cost: number | null
  price_per_liter: number | null
  liters: number | null
  date: string | null
  station_name: string | null
  raw_text: string | null
}

export interface OCRStatusResponse {
  available: boolean
  is_demo: boolean
  message: string
}

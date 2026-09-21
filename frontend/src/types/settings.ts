export interface AppSettingsResponse {
  price_fluctuation_cents: number
  max_total_cost: number
  max_accumulated_partial_cost: number
  reminder_types: string[]
  maintenance_types: string[]
  import_kml_min: number
  import_kml_max: number
  import_kml_error: number
  import_kmd_max: number
  ocr_add_station_to_notes: boolean
  ocr_add_liters_to_notes: boolean
}

export interface AppSettingsUpdate {
  price_fluctuation_cents?: number
  max_total_cost?: number
  max_accumulated_partial_cost?: number
  reminder_types?: string[]
  maintenance_types?: string[]
  import_kml_min?: number
  import_kml_max?: number
  import_kml_error?: number
  import_kmd_max?: number
  ocr_add_station_to_notes?: boolean
  ocr_add_liters_to_notes?: boolean
}

export interface CategoryOperationRequest {
  category: string
}

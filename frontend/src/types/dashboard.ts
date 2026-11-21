export interface LastRefuelingSummary {
  date: string | null
  total_cost: number | null
  price_per_liter: number | null
  liters: number | null
}

export interface HealthScoreSummary {
  score: number
  status_color: string
  issues: string[]
}

export interface PartialAccumulationAlert {
  accumulated_cost: number
  partials_count: number
  is_warning: boolean
  max_threshold: number
}

export interface DashboardSummaryResponse {
  current_km: number
  last_refueling: LastRefuelingSummary | null
  health_score: HealthScoreSummary
  partial_alert: PartialAccumulationAlert
  total_fuel_cost: number
  total_maintenance_cost: number
  total_spent: number
  avg_km_per_liter: number
}

export interface PriceTrendPoint {
  date: string
  price_per_liter: number
}

export interface EfficiencyPoint {
  date: string
  km_per_liter: number
}

export interface MonthlySpendingPoint {
  month: string
  label: string
  fuel_cost: number
  maintenance_cost: number
  total_cost: number
}

export interface DashboardChartsResponse {
  price_trend: PriceTrendPoint[]
  efficiency: EfficiencyPoint[]
  monthly_spending: MonthlySpendingPoint[]
}

export interface TripCalculationRequest {
  distance_km: number
  expected_fuel_price?: number
}

export interface TripCalculationResponse {
  distance_km: number
  estimated_liters: number
  estimated_cost: number
  avg_km_per_liter_used: number
  fuel_price_used: number
}

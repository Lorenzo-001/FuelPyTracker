export interface ReminderBase {
  title: string
  frequency_km?: number | null
  frequency_days?: number | null
  notes?: string | null
}

export interface ReminderCreate extends ReminderBase {
  current_km?: number | null
  current_date?: string | null
}

export interface ReminderUpdate {
  title?: string
  frequency_km?: number | null
  frequency_days?: number | null
  is_active?: boolean
  notes?: string | null
}

export interface ReminderResponse extends ReminderBase {
  id: number
  user_id: string
  last_km_check: number | null
  last_date_check: string | null
  is_active: boolean
  target_km: number | null
  target_date: string | null
  remaining_km: number | null
  remaining_days: number | null
  progress: number
  is_overdue: boolean
  status_message: string
}

export interface ReminderExecutionRequest {
  check_date?: string | null
  check_km?: number | null
  notes?: string | null
}

export interface ReminderExecutionResponse {
  reminder_id: number
  last_km_check: number | null
  last_date_check: string | null
  next_target_km: number | null
  next_target_date: string | null
  message: string
}

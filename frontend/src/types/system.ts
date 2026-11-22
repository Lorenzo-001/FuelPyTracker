export interface HealthCheckResponse {
  status: string
  version?: string
  app?: string
  database?: string
  demo_mode?: boolean
  writes_disabled?: boolean
  timestamp?: string
}

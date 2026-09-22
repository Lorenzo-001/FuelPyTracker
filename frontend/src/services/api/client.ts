/**
 * Client HTTP centralizzato per FuelPyTracker V2.
 * Gestisce l'inoltro delle richieste a FastAPI tramite il reverse proxy Vite (/api),
 * l'iniezione del token Bearer JWT e la tipizzazione delle risposte e degli errori.
 */

export class ApiError extends Error {
  public status: number
  public details?: unknown

  constructor(message: string, status: number, details?: unknown) {
    super(message)
    this.name = "ApiError"
    this.status = status
    this.details = details
  }
}

const TOKEN_STORAGE_KEY = "fpt_access_token"

export const authStorage = {
  getToken: (): string | null => {
    try {
      return localStorage.getItem(TOKEN_STORAGE_KEY)
    } catch {
      return null
    }
  },
  setToken: (token: string): void => {
    try {
      localStorage.setItem(TOKEN_STORAGE_KEY, token)
    } catch {
      // Ignore storage errors in restricted contexts
    }
  },
  removeToken: (): void => {
    try {
      localStorage.removeItem(TOKEN_STORAGE_KEY)
    } catch {
      // Ignore storage errors
    }
  },
}

interface RequestOptions extends Omit<RequestInit, "body"> {
  body?: unknown
  params?: Record<string, string | number | boolean | undefined | null>
}

class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string = "/api") {
    this.baseUrl = baseUrl
  }

  private buildUrl(endpoint: string, params?: RequestOptions["params"]): string {
    // If endpoint starts with http or /health, don't prepend baseUrl
    const base = endpoint.startsWith("http")
      ? endpoint
      : endpoint.startsWith("/health")
        ? endpoint
        : `${this.baseUrl}${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`

    if (!params) return base

    const searchParams = new URLSearchParams()
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        searchParams.append(key, String(value))
      }
    })

    const queryString = searchParams.toString()
    return queryString ? `${base}?${queryString}` : base
  }

  async request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
    const { body, params, headers = {}, ...customConfig } = options

    const token = authStorage.getToken()
    const defaultHeaders: Record<string, string> = {
      Accept: "application/json",
    }

    if (!(body instanceof FormData)) {
      defaultHeaders["Content-Type"] = "application/json"
    }

    if (token) {
      defaultHeaders["Authorization"] = `Bearer ${token}`
    } else {
      // In dev/demo environment without login, use default demo user
      defaultHeaders["X-User-Id"] = "00000000-0000-4000-8000-000000000001"
    }

    const config: RequestInit = {
      ...customConfig,
      headers: {
        ...defaultHeaders,
        ...(headers as Record<string, string>),
      },
    }

    if (body !== undefined) {
      config.body = body instanceof FormData ? body : JSON.stringify(body)
    }

    const url = this.buildUrl(endpoint, params)

    try {
      const response = await fetch(url, config)

      if (!response.ok) {
        let errorDetail: unknown = null
        let errorMessage = `Errore di rete (${response.status} ${response.statusText})`

        try {
          const errorData = await response.json()
          errorDetail = errorData
          if (errorData.detail) {
            errorMessage =
              typeof errorData.detail === "string"
                ? errorData.detail
                : JSON.stringify(errorData.detail)
          } else if (errorData.message) {
            errorMessage = errorData.message
          }
        } catch {
          // Response was not JSON
        }

        throw new ApiError(errorMessage, response.status, errorDetail)
      }

      // Handle 204 No Content
      if (response.status === 204) {
        return {} as T
      }

      return (await response.json()) as T
    } catch (err: unknown) {
      if (err instanceof ApiError) {
        throw err
      }
      const message = err instanceof Error ? err.message : "Errore sconosciuto di connessione"
      throw new ApiError(message, 0, err)
    }
  }

  get<T>(endpoint: string, options?: RequestOptions): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: "GET" })
  }

  post<T>(endpoint: string, body?: unknown, options?: RequestOptions): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: "POST", body })
  }

  put<T>(endpoint: string, body?: unknown, options?: RequestOptions): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: "PUT", body })
  }

  delete<T>(endpoint: string, options?: RequestOptions): Promise<T> {
    return this.request<T>(endpoint, { ...options, method: "DELETE" })
  }
}

export const apiClient = new ApiClient()

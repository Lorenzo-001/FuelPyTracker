import { apiClient, authStorage } from "./client"
import type {
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  UserResponse,
  MessageResponse,
} from "@/types/auth"

export const authApi = {
  /**
   * Autentica l'utente e memorizza il token JWT in local storage.
   */
  login: async (payload: LoginRequest): Promise<TokenResponse> => {
    const res = await apiClient.post<TokenResponse>("/auth/login", payload)
    if (res.access_token) {
      authStorage.setToken(res.access_token)
    }
    return res
  },

  /**
   * Registra un nuovo account.
   */
  register: (payload: RegisterRequest): Promise<MessageResponse> => {
    return apiClient.post<MessageResponse>("/auth/register", payload)
  },

  /**
   * Effettua il logout rimuovendo il token locale.
   */
  logout: async (): Promise<MessageResponse> => {
    try {
      const res = await apiClient.post<MessageResponse>("/auth/logout")
      authStorage.removeToken()
      return res
    } catch {
      authStorage.removeToken()
      return { message: "Logout effettuato.", success: true }
    }
  },

  /**
   * Recupera il profilo dell'utente correntemente autenticato o in sessione demo.
   */
  getMe: (): Promise<UserResponse> => {
    return apiClient.get<UserResponse>("/auth/me")
  },

  /**
   * Richiede il recupero password via email.
   */
  resetPassword: (email: string): Promise<MessageResponse> => {
    return apiClient.post<MessageResponse>("/auth/reset-password", { email })
  },
}

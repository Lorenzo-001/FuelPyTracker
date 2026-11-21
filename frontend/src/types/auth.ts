export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
}

export interface UserResponse {
  id: string
  email: string
  is_demo: boolean
}

export interface TokenResponse {
  access_token: string
  token_type: string
  user: UserResponse
}

export interface PasswordResetConfirmRequest {
  access_token: string
  new_password: string
  refresh_token?: string | null
}

export interface PasswordChangeRequest {
  current_password: string
  new_password: string
}

export interface EmailChangeRequest {
  new_email: string
}

export interface MessageResponse {
  message: string
  success: boolean
}

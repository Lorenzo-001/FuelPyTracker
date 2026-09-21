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

export interface MessageResponse {
  message: string
  success: boolean
}

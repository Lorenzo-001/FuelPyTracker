import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import { authApi } from "@/services/api/authApi"
import type { LoginRequest, UserResponse } from "@/types/auth"
import { toast } from "sonner"
import { useNavigate } from "react-router-dom"

export const AUTH_QUERY_KEY = ["auth", "me"] as const

/**
 * Hook per leggere il profilo dell'utente autenticato o in sessione demo.
 */
export function useCurrentUser() {
  return useQuery<UserResponse>({
    queryKey: AUTH_QUERY_KEY,
    queryFn: () => authApi.getMe(),
    staleTime: 1000 * 60 * 5, // 5 minuti
    retry: false,
  })
}

/**
 * Mutazione per eseguire l'autenticazione utente.
 */
export function useLogin() {
  const queryClient = useQueryClient()
  const navigate = useNavigate()

  return useMutation({
    mutationFn: (credentials: LoginRequest) => authApi.login(credentials),
    onSuccess: (data) => {
      queryClient.setQueryData(AUTH_QUERY_KEY, data.user)
      queryClient.invalidateQueries({ queryKey: AUTH_QUERY_KEY })
      toast.success("Accesso effettuato con successo!", {
        description: data.user.is_demo
          ? "Sei in modalità dimostrativa Sandbox."
          : `Benvenuto, ${data.user.email}`,
      })
      navigate("/")
    },
    onError: (err: Error) => {
      toast.error(`Accesso fallito: ${err.message}`)
    },
  })
}

/**
 * Mutazione per registrare un nuovo account.
 */
export function useRegister() {
  return useMutation({
    mutationFn: (credentials: { email: string; password: string }) =>
      authApi.register(credentials),
    onSuccess: (data) => {
      toast.success("Registrazione completata!", {
        description: data.message || "Account registrato con successo. Ora puoi accedere.",
      })
    },
    onError: (err: Error) => {
      toast.error(`Registrazione fallita: ${err.message}`)
    },
  })
}


/**
 * Mutazione per effettuare il logout.
 */
export function useLogout() {
  const queryClient = useQueryClient()
  const navigate = useNavigate()

  return useMutation({
    mutationFn: () => authApi.logout(),
    onSuccess: () => {
      queryClient.clear()
      toast.info("Sessione terminata.")
      navigate("/login")
    },
    onError: (err: Error) => {
      toast.error(`Errore durante il logout: ${err.message}`)
    },
  })
}

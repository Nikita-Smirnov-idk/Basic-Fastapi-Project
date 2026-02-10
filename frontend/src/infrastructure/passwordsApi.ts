import type { AuthMessage } from "@/domain/auth/types/auth"
import { httpRequest } from "@/pkg/httpClient"

export async function recoverPassword(email: string): Promise<AuthMessage> {
  return httpRequest<AuthMessage>({
    path: `/users/passwords/recovery/${encodeURIComponent(email)}`,
    method: "POST",
  })
}

export async function resetPassword(token: string, newPassword: string): Promise<AuthMessage> {
  return httpRequest<AuthMessage>({
    path: "/users/passwords/reset/",
    method: "POST",
    body: { token, new_password: newPassword },
  })
}


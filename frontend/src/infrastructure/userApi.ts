import type { User } from "@/domain/user/types/user"
import type { AuthMessage } from "@/domain/auth/types/auth"
import { httpRequest } from "@/pkg/httpClient"

export async function getCurrentUser(): Promise<User> {
  return httpRequest<User>({
    path: "/users/me",
    method: "GET",
  })
}

export async function deleteCurrentUser(): Promise<AuthMessage> {
  return httpRequest<AuthMessage>({
    path: "/users/me",
    method: "DELETE",
  })
}


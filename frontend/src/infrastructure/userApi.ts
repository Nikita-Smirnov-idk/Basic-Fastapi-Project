import type { User } from "@/domain/user/types/user"
import type { AuthMessage } from "@/domain/auth/types/auth"
import { httpRequest } from "@/pkg/httpClient"

export interface GetCurrentUserOptions {
  skipTokenRefresh?: boolean
  skipErrorToast?: boolean
}

export async function getCurrentUser(options?: GetCurrentUserOptions): Promise<User> {
  return httpRequest<User>({
    path: "/users/me",
    method: "GET",
    skipTokenRefresh: options?.skipTokenRefresh,
    skipErrorToast: options?.skipErrorToast,
  })
}

export async function deleteCurrentUser(): Promise<AuthMessage> {
  return httpRequest<AuthMessage>({
    path: "/users/me",
    method: "DELETE",
  })
}


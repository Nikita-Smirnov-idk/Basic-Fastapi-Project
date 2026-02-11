import type { User } from "@/domain/user/types/user"
import type { AuthMessage } from "@/domain/auth/types/auth"
import type { GetCurrentUserOptions } from "@/infrastructure/userApi"
import { deleteCurrentUser, getCurrentUser } from "@/infrastructure/userApi"

export async function getMe(options?: GetCurrentUserOptions): Promise<User> {
  return getCurrentUser(options)
}

export async function deleteMe(): Promise<AuthMessage> {
  return deleteCurrentUser()
}


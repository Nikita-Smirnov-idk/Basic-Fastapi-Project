import type { User } from "@/domain/user/types/user"
import type { AuthMessage } from "@/domain/auth/types/auth"
import { deleteCurrentUser, getCurrentUser } from "@/infrastructure/userApi"

export async function getMe(): Promise<User> {
  return getCurrentUser()
}

export async function deleteMe(): Promise<AuthMessage> {
  return deleteCurrentUser()
}


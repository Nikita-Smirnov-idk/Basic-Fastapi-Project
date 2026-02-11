import { useCallback } from "react"
import type { AuthMessage } from "@/domain/auth/types/auth"
import { deleteMe } from "@/use_cases/userService"
import { useUserStore } from "@/pkg/stores/userStore"

export function useCurrentUser() {
  const { user, loading, error, fetchUser, clear } = useUserStore()
  const refetch = useCallback(() => void fetchUser(true), [fetchUser])

  const deleteAccount = async (): Promise<AuthMessage> => {
    const result = await deleteMe()
    clear()
    return result
  }

  return { user, loading, error, refetch, deleteAccount }
}


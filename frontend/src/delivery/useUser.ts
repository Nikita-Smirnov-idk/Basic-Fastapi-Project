import { useEffect, useState } from "react"

import type { User } from "@/domain/user/types/user"
import type { AuthMessage } from "@/domain/auth/types/auth"
import { deleteMe, getMe } from "@/application/userService"

export function useCurrentUser() {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    ;(async () => {
      try {
        const me = await getMe()
        setUser(me)
      } catch (e) {
        setError((e as Error).message)
      } finally {
        setLoading(false)
      }
    })()
  }, [])

  const deleteAccount = async (): Promise<AuthMessage> => {
    const result = await deleteMe()
    setUser(null)
    return result
  }

  return { user, loading, error, deleteAccount }
}


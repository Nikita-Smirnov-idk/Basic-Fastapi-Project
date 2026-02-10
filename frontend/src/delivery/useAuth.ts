import { useCallback, useState } from "react"

import type { AuthMessage, SessionsList } from "@/domain/auth/types/auth"
import { getSessions, loginUser, logoutUser } from "@/application/authService"

export function useLogin() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [message, setMessage] = useState<AuthMessage | null>(null)

  const login = async (email: string, password: string) => {
    setLoading(true)
    setError(null)
    try {
      const result = await loginUser(email, password)
      setMessage(result)
      return result
    } catch (e) {
      setError((e as Error).message)
      throw e
    } finally {
      setLoading(false)
    }
  }

  return { login, loading, error, message }
}

export function useLogout() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const logout = async () => {
    setLoading(true)
    setError(null)
    try {
      await logoutUser()
    } catch (e) {
      setError((e as Error).message)
      throw e
    } finally {
      setLoading(false)
    }
  }

  return { logout, loading, error }
}

export function useSessions() {
  const [data, setData] = useState<SessionsList | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await getSessions()
      setData(result)
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setLoading(false)
    }
  }, [])

  return { data, loading, error, load }
}


import { useState } from "react"

import type { AuthMessage } from "@/domain/auth/types/auth"
import {
  requestPasswordRecovery,
  submitPasswordReset,
} from "@/use_cases/passwordsService"

export function usePasswordRecovery() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [message, setMessage] = useState<AuthMessage | null>(null)

  const recover = async (email: string) => {
    setLoading(true)
    setError(null)
    try {
      const result = await requestPasswordRecovery(email)
      setMessage(result)
      return result
    } catch (e) {
      setError((e as Error).message)
      throw e
    } finally {
      setLoading(false)
    }
  }

  return { recover, loading, error, message }
}

export function usePasswordReset() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [message, setMessage] = useState<AuthMessage | null>(null)

  const reset = async (token: string, newPassword: string) => {
    setLoading(true)
    setError(null)
    try {
      const result = await submitPasswordReset(token, newPassword)
      setMessage(result)
      return result
    } catch (e) {
      setError((e as Error).message)
      throw e
    } finally {
      setLoading(false)
    }
  }

  return { reset, loading, error, message }
}


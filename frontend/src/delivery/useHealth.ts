import { useEffect, useState } from "react"

import type { HealthStatus } from "@/domain/utils/types/utils"
import { getHealthStatus } from "@/application/utilsService"

export function useHealth() {
  const [status, setStatus] = useState<HealthStatus | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await getHealthStatus()
      setStatus(data)
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
  }, [])

  return { status, loading, error, reload: load }
}


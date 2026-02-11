import { useEffect, useState } from "react"

import type { HomePageData } from "@/domain/home/types/home"
import { getHomePageData } from "@/use_cases/homeService"

interface UseHomeState {
  data: HomePageData | null
  isLoading: boolean
  error: Error | null
}

export function useHome(): UseHomeState {
  const [state, setState] = useState<UseHomeState>({
    data: null,
    isLoading: true,
    error: null,
  })

  useEffect(() => {
    let cancelled = false

    ;(async () => {
      try {
        const data = await getHomePageData()
        if (cancelled) return
        setState({ data, isLoading: false, error: null })
      } catch (error) {
        if (cancelled) return
        setState({ data: null, isLoading: false, error: error as Error })
      }
    })()

    return () => {
      cancelled = true
    }
  }, [])

  return state
}


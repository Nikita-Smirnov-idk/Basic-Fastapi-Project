import { useCallback, useEffect, useState } from "react"

import type {
  YCCompanies,
  YCSearchMeta,
  YCSyncState,
} from "@/domain/yc/types/yc"
import {
  getExportUrl,
  getMeta,
  getSyncState,
  listCompanies,
  triggerSync,
} from "@/application/ycService"

export function useYCCompanies() {
  const [companies, setCompanies] = useState<YCCompanies | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await listCompanies()
      setCompanies(data)
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
  }, [])

  return { companies, loading, error, reload: load }
}

export function useYCMeta() {
  const [meta, setMeta] = useState<YCSearchMeta | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await getMeta()
      setMeta(data)
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void load()
  }, [])

  return { meta, loading, error, reload: load }
}

export function useYCSync() {
  const [syncState, setSyncState] = useState<YCSyncState | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [message, setMessage] = useState<string | null>(null)

  const loadState = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await getSyncState()
      setSyncState(data)
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setLoading(false)
    }
  }, [])

  const syncNow = async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await triggerSync()
      setMessage(res.message)
      await loadState()
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setLoading(false)
    }
  }

  const exportUrl = getExportUrl()

  return { syncState, loading, error, message, syncNow, exportUrl, reload: loadState }
}


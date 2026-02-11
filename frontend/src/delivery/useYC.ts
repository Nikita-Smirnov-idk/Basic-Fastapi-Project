import { useCallback, useEffect, useState } from "react"

import type {
  YCCompanies,
  YCSearchMeta,
  YCSyncState,
} from "@/domain/yc/types/yc"
import type { YCCompanyFilters } from "@/infrastructure/ycApi"
import {
  getMeta,
  getSyncState,
  listCompanies,
  triggerSync,
} from "@/use_cases/ycService"

const FREE_PAGE_SIZE = 15
const PAID_PAGE_SIZE = 50

export function useYCCompanies(
  filters: YCCompanyFilters = {},
  page: number = 1,
) {
  const [companies, setCompanies] = useState<YCCompanies | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const skip = (page - 1) * PAID_PAGE_SIZE

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await listCompanies({ ...filters, skip })
      setCompanies(data)
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setLoading(false)
    }
  }, [skip, filters.q, filters.batch, filters.year, filters.status_filter, filters.industry, filters.is_hiring, filters.nonprofit, filters.top_company])

  useEffect(() => {
    void load()
  }, [load])

  const isPaid = companies !== null && companies.data.length !== FREE_PAGE_SIZE
  const pageSize = isPaid ? PAID_PAGE_SIZE : FREE_PAGE_SIZE
  const totalPages = companies
    ? isPaid
      ? Math.max(1, Math.ceil(companies.count / pageSize))
      : 1
    : 1
  const canNext = page < totalPages
  const canPrev = page > 1

  return {
    companies,
    loading,
    error,
    reload: load,
    pageSize,
    totalPages,
    page,
    canNext,
    canPrev,
    isPaid,
  }
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

  return { syncState, loading, error, message, syncNow, reload: loadState }
}


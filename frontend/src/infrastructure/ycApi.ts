import type {
  YCCompanies,
  YCSearchMeta,
  YCSyncState,
} from "@/domain/yc/types/yc"
import { httpRequest } from "@/pkg/httpClient"

export interface YCCompanyFilters {
  q?: string
  batch?: string
  year?: number
  status_filter?: string
  industry?: string
  is_hiring?: boolean
  nonprofit?: boolean
  top_company?: boolean
  skip?: number
  limit?: number
}

export async function listYCCompanies(
  filters: YCCompanyFilters = {},
): Promise<YCCompanies> {
  const { limit: _omit, ...query } = filters
  return httpRequest<YCCompanies>({
    path: "/yc/companies",
    method: "GET",
    query: query as Record<string, string | number | boolean | undefined>,
  })
}

export async function getYCMeta(): Promise<YCSearchMeta> {
  return httpRequest<YCSearchMeta>({
    path: "/yc/meta",
    method: "GET",
  })
}

export async function getYCSyncState(): Promise<YCSyncState> {
  return httpRequest<YCSyncState>({
    path: "/admin/sync-state",
    method: "GET",
  })
}

export async function syncYCNow(): Promise<{ message: string }> {
  return httpRequest<{ message: string }>({
    path: "/admin/sync",
    method: "POST",
  })
}


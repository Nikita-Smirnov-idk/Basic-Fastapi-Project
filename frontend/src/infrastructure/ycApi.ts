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
  return httpRequest<YCCompanies>({
    path: "/yc/companies",
    method: "GET",
    query: filters as Record<string, string | number | boolean | undefined>,
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
    path: "/yc/sync-state",
    method: "GET",
  })
}

export async function syncYCNow(): Promise<{ message: string }> {
  return httpRequest<{ message: string }>({
    path: "/yc/sync",
    method: "POST",
  })
}

export function getYCExportUrl(): string {
  const base =
    import.meta.env.VITE_API_URL ??
    (typeof window !== "undefined" ? window.location.origin : "http://localhost:8000")
  const url = new URL("/api/v1/yc/export", base)
  return url.toString()
}


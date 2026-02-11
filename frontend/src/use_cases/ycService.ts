import type {
  YCCompanies,
  YCSearchMeta,
  YCSyncState,
} from "@/domain/yc/types/yc"
import {
  getYCMeta,
  getYCSyncState,
  listYCCompanies,
  syncYCNow,
  type YCCompanyFilters,
} from "@/infrastructure/ycApi"

export async function listCompanies(
  filters: YCCompanyFilters = {},
): Promise<YCCompanies> {
  return listYCCompanies(filters)
}

export async function getMeta(): Promise<YCSearchMeta> {
  return getYCMeta()
}

export async function getSyncState(): Promise<YCSyncState> {
  return getYCSyncState()
}

export async function triggerSync(): Promise<{ message: string }> {
  return syncYCNow()
}


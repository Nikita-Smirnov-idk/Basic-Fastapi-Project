import type { HealthStatus } from "@/domain/utils/types/utils"
import { httpRequest } from "@/pkg/httpClient"

export async function getHealth(): Promise<HealthStatus> {
  const ok = await httpRequest<boolean>({
    path: "/utils/health-check/",
    method: "GET",
  })

  return { ok }
}


import type { HealthStatus } from "@/domain/utils/types/utils"
import { getHealth } from "@/infrastructure/utilsApi"

export async function getHealthStatus(): Promise<HealthStatus> {
  return getHealth()
}


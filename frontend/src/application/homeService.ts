import type { HomePageData } from "@/domain/home/types/home"
import { fetchHomePageData } from "@/infrastructure/homeApi"

export async function getHomePageData(): Promise<HomePageData> {
  // Здесь можно добавить дополнительные сценарии: логирование, кэш, метрики и т.д.
  return fetchHomePageData()
}


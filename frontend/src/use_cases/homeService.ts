import type { HomePageData } from "@/domain/home/types/home"
import { fetchHomePageData } from "@/infrastructure/homeApi"

export async function getHomePageData(): Promise<HomePageData> {
  return fetchHomePageData()
}


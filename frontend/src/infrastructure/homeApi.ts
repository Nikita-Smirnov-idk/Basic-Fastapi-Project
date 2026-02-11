import type { HomePageData } from "@/domain/home/types/home"

export async function fetchHomePageData(): Promise<HomePageData> {
  return {
    title: "FeatureBoard",
    subtitle: "Feature catalog and YC companies",
    description:
      "This is the home page. It can be connected to real backend data (YC directory, users, etc.).",
  }
}


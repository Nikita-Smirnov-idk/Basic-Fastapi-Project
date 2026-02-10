import type { HomePageData } from "@/domain/home/types/home"

export async function fetchHomePageData(): Promise<HomePageData> {
  return {
    title: "FeatureBoard",
    subtitle: "Каталог фич и YC-компаний",
    description:
      "Это базовая главная страница. Дальше сюда можно будет подвязать реальные данные из backend (YC directory, пользователи и т.п.).",
  }
}


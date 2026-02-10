import type { HomePageData } from "@/domain/home/types/home"
// import { httpRequest } from "@/pkg/httpClient"

// В реальном приложении данные можно получать с бэкенда (например, /api/home).
// Пока что вернем мок, чтобы интерфейс сразу работал.
export async function fetchHomePageData(): Promise<HomePageData> {
  return {
    title: "FeatureBoard",
    subtitle: "Каталог фич и YC-компаний",
    description:
      "Это базовая главная страница. Дальше сюда можно будет подвязать реальные данные из backend (YC directory, пользователи и т.п.).",
  }
}


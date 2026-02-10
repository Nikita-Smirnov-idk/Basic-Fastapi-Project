import { Link } from "@tanstack/react-router"

import { useHome } from "@/delivery"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

export function HomePage() {
  const { data, isLoading, error } = useHome()

  if (isLoading) {
    return (
      <main className="flex min-h-[70vh] items-center justify-center">
        <p className="text-muted-foreground">Загружаем главную страницу…</p>
      </main>
    )
  }

  if (error || !data) {
    return (
      <main className="flex min-h-[70vh] items-center justify-center">
        <p className="text-destructive">
          Не удалось загрузить данные главной страницы
        </p>
      </main>
    )
  }

  return (
    <main className="flex min-h-[70vh] items-center justify-center px-4">
      <Card className="max-w-2xl w-full">
        <CardHeader>
          <CardTitle className="text-3xl font-bold">{data.title}</CardTitle>
          <CardDescription className="text-base">
            {data.subtitle}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <p className="text-muted-foreground">{data.description}</p>

          <div className="flex flex-wrap gap-3">
            <Link to="/login">
              <Button size="lg">Войти</Button>
            </Link>
            <Link to="/signup">
              <Button variant="outline" size="lg">
                Зарегистрироваться
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    </main>
  )
}

export default HomePage


import { Link } from "@tanstack/react-router"
import { useHealth } from "@/delivery"

export function HealthPage() {
  const { status, loading, error } = useHealth()

  return (
    <main className="flex min-h-screen items-center justify-center p-4 bg-gradient-to-br from-background via-background to-muted/20">
      <section className="w-full max-w-md rounded-2xl border bg-card text-card-foreground shadow-xl p-8 space-y-6 text-center">
        <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto">
          <span className="text-3xl">🏥</span>
        </div>

        <h1 className="text-3xl font-bold">Health Check</h1>

        {loading && (
          <div className="space-y-4">
            <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto" />
            <p className="text-muted-foreground">Проверяем статус...</p>
          </div>
        )}

        {error && (
          <div className="rounded-lg border bg-destructive/10 border-destructive/20 p-4">
            <p className="text-destructive">Ошибка: {error}</p>
          </div>
        )}

        {status && (
          <div className="space-y-4">
            <div
              className={`w-20 h-20 rounded-full flex items-center justify-center mx-auto ${
                status.ok
                  ? "bg-green-500/20"
                  : "bg-destructive/20"
              }`}
            >
              <span className="text-4xl">
                {status.ok ? "✅" : "❌"}
              </span>
            </div>
            <p
              className={`text-xl font-semibold ${
                status.ok ? "text-green-600 dark:text-green-400" : "text-destructive"
              }`}
            >
              {status.ok ? "Backend работает" : "Backend недоступен"}
            </p>
          </div>
        )}

        <Link
          to="/"
          className="inline-flex items-center justify-center rounded-lg bg-primary px-6 py-3 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors shadow-md"
        >
          На главную
        </Link>
      </section>
    </main>
  )
}

export default HealthPage


import { useEffect } from "react"
import { Link } from "@tanstack/react-router"
import { toast } from "sonner"
import { useYCSync } from "@/delivery"

const adminYCSyncLoadedRef = { current: false }

export function AdminYCSyncPage() {
  const { syncState, loading, exportUrl, syncNow, reload } = useYCSync()

  useEffect(() => {
    if (adminYCSyncLoadedRef.current) return
    adminYCSyncLoadedRef.current = true
    void reload()
    return () => {
      setTimeout(() => {
        adminYCSyncLoadedRef.current = false
      }, 0)
    }
  }, [reload])

  const handleSync = async () => {
    try {
      await syncNow()
      toast.success("Синхронизация запущена")
    } catch (error) {
      console.error("Sync error:", error)
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20 p-4 md:p-8">
      <div className="max-w-6xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl md:text-4xl font-bold">YC Синхронизация</h1>
            <p className="text-muted-foreground mt-1">
              Управление синхронизацией данных Y Combinator
            </p>
          </div>
          <div className="flex gap-2">
            <button
              className="inline-flex items-center justify-center rounded-lg border bg-background px-4 py-2 text-sm hover:bg-accent transition-colors disabled:opacity-50"
              onClick={reload}
              disabled={loading}
            >
              🔄 Обновить
            </button>
            <Link
              to="/"
              className="inline-flex items-center justify-center rounded-lg border bg-background px-4 py-2 text-sm hover:bg-accent transition-colors"
            >
              ← На главную
            </Link>
          </div>
        </div>

        <div className="flex gap-2 border-b pb-4">
          <Link
            to="/admin"
            className="px-4 py-2 rounded-lg hover:bg-accent text-sm font-medium transition-colors"
          >
            Дашборд
          </Link>
          <Link
            to="/admin/users"
            className="px-4 py-2 rounded-lg hover:bg-accent text-sm font-medium transition-colors"
          >
            Пользователи
          </Link>
          <Link
            to="/admin/yc-sync"
            className="px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium"
          >
            YC Синхронизация
          </Link>
        </div>

        <section className="rounded-2xl border bg-card text-card-foreground shadow-lg p-6 space-y-4">
          <h2 className="text-xl font-semibold flex items-center gap-2">
            <span>🔄</span> Управление синхронизацией
          </h2>

          <div className="flex flex-wrap items-center gap-3">
            <button
              className="inline-flex items-center justify-center rounded-lg bg-primary px-6 py-3 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-md"
              onClick={handleSync}
              disabled={loading}
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-primary-foreground border-t-transparent rounded-full animate-spin mr-2" />
                  Синхронизация...
                </>
              ) : (
                <>🚀 Запустить синхронизацию</>
              )}
            </button>

            <a
              href={exportUrl}
              className="inline-flex items-center justify-center rounded-lg border bg-background px-6 py-3 text-sm font-medium hover:bg-accent transition-colors"
              target="_blank"
              rel="noreferrer"
            >
              📥 Экспорт CSV
            </a>
          </div>
        </section>

        {syncState && (
          <section className="rounded-2xl border bg-card text-card-foreground shadow-lg p-6 space-y-4">
            <h2 className="text-xl font-semibold flex items-center gap-2">
              <span>📊</span> Статус синхронизации
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="rounded-lg border bg-background/50 p-4 space-y-2">
                <p className="text-xs text-muted-foreground uppercase tracking-wide">
                  Последний запуск
                </p>
                <p className="text-sm font-medium">
                  {syncState.last_started_at
                    ? new Date(syncState.last_started_at).toLocaleString("ru-RU")
                    : "Не запускалась"}
                </p>
              </div>

              <div className="rounded-lg border bg-background/50 p-4 space-y-2">
                <p className="text-xs text-muted-foreground uppercase tracking-wide">
                  Последнее завершение
                </p>
                <p className="text-sm font-medium">
                  {syncState.last_finished_at
                    ? new Date(syncState.last_finished_at).toLocaleString("ru-RU")
                    : "Не завершалась"}
                </p>
              </div>

              <div className="rounded-lg border bg-background/50 p-4 space-y-2">
                <p className="text-xs text-muted-foreground uppercase tracking-wide">
                  Последний успешный запуск
                </p>
                <p className="text-sm font-medium">
                  {syncState.last_success_at
                    ? new Date(syncState.last_success_at).toLocaleString("ru-RU")
                    : "Не было успешных"}
                </p>
              </div>

              <div className="rounded-lg border bg-background/50 p-4 space-y-2">
                <p className="text-xs text-muted-foreground uppercase tracking-wide">
                  Последнее количество компаний
                </p>
                <p className="text-sm font-medium">
                  {syncState.last_item_count ?? "—"}
                </p>
              </div>
            </div>

            {syncState.last_error && (
              <div className="rounded-lg border bg-destructive/10 border-destructive/20 p-4">
                <p className="text-xs text-muted-foreground uppercase tracking-wide mb-2">
                  Последняя ошибка
                </p>
                <p className="text-sm text-destructive font-mono">
                  {syncState.last_error}
                </p>
              </div>
            )}
          </section>
        )}
      </div>
    </main>
  )
}

export default AdminYCSyncPage

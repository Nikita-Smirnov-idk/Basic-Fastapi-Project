import { useEffect } from "react"
import { Link } from "@tanstack/react-router"
import { useAdminDashboard } from "@/delivery"

const adminDashboardLoadedRef = { current: false }

export function AdminDashboardPage() {
  const { data, loading, error, load } = useAdminDashboard()

  useEffect(() => {
    if (adminDashboardLoadedRef.current) return
    adminDashboardLoadedRef.current = true
    void load()
    return () => {
      setTimeout(() => {
        adminDashboardLoadedRef.current = false
      }, 0)
    }
  }, [load])

  return (
    <main className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20 p-4 md:p-8">
      <div className="max-w-6xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl md:text-4xl font-bold">Админ-панель</h1>
            <p className="text-muted-foreground mt-1">Обзор системы</p>
          </div>
          <Link
            to="/"
            className="inline-flex items-center justify-center rounded-lg border bg-background px-4 py-2 text-sm hover:bg-accent transition-colors"
          >
            ← На главную
          </Link>
        </div>

        <div className="flex gap-2 border-b pb-4">
          <Link
            to="/admin"
            className="px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium"
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
            className="px-4 py-2 rounded-lg hover:bg-accent text-sm font-medium transition-colors"
          >
            YC Синхронизация
          </Link>
        </div>

        {loading && (
          <div className="flex items-center justify-center py-20">
            <div className="text-center space-y-4">
              <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto" />
              <p className="text-muted-foreground">Загружаем данные...</p>
            </div>
          </div>
        )}

        {error && (
          <div className="rounded-xl border bg-destructive/10 border-destructive/20 p-6 text-center">
            <div className="w-12 h-12 rounded-full bg-destructive/20 flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl">⚠️</span>
            </div>
            <h3 className="font-semibold mb-2">Ошибка загрузки</h3>
            <p className="text-sm text-muted-foreground">{error}</p>
          </div>
        )}

        {data && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <StatCard
              icon="👥"
              label="Всего пользователей"
              value={data.total_users}
              color="blue"
            />
            <StatCard
              icon="💳"
              label="Платящих пользователей"
              value={data.paying_users}
              color="green"
            />
            <StatCard
              icon="💰"
              label="Баланс (центы)"
              value={data.total_balance_cents.toLocaleString()}
              color="yellow"
            />
            <StatCard
              icon="🏢"
              label="YC компании"
              value={data.yc_companies_count}
              color="purple"
            />
            <StatCard
              icon="👔"
              label="YC основатели"
              value={data.yc_founders_count}
              color="pink"
            />
          </div>
        )}
      </div>
    </main>
  )
}

interface StatCardProps {
  icon: string
  label: string
  value: string | number
  color: "blue" | "green" | "yellow" | "purple" | "pink"
}

function StatCard({ icon, label, value, color }: StatCardProps) {
  const colorClasses = {
    blue: "from-blue-500/10 to-blue-500/5 border-blue-500/20",
    green: "from-green-500/10 to-green-500/5 border-green-500/20",
    yellow: "from-yellow-500/10 to-yellow-500/5 border-yellow-500/20",
    purple: "from-purple-500/10 to-purple-500/5 border-purple-500/20",
    pink: "from-pink-500/10 to-pink-500/5 border-pink-500/20",
  }

  return (
    <div
      className={`rounded-xl border bg-gradient-to-br ${colorClasses[color]} p-6 space-y-3 transition-transform hover:scale-105 cursor-default`}
    >
      <div className="flex items-center gap-3">
        <div className="text-3xl">{icon}</div>
        <div className="flex-1">
          <p className="text-xs text-muted-foreground uppercase tracking-wide">
            {label}
          </p>
          <p className="text-2xl font-bold mt-1">{value}</p>
        </div>
      </div>
    </div>
  )
}

export default AdminDashboardPage


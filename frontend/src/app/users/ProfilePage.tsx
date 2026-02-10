import { Link, useNavigate } from "@tanstack/react-router"
import { toast } from "sonner"
import { useCurrentUser, useLogout } from "@/delivery"

export function ProfilePage() {
  const navigate = useNavigate()
  const { user, loading, error } = useCurrentUser()
  const { logout, loading: logoutLoading } = useLogout()

  const handleLogout = async () => {
    try {
      await logout()
      toast.success("Вы вышли из системы")
      navigate({ to: "/" })
    } catch (error) {
      console.error("Logout error:", error)
    }
  }

  if (loading) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-gradient-to-br from-background via-background to-muted/20">
        <div className="text-center space-y-4">
          <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-muted-foreground">Загружаем профиль...</p>
        </div>
      </main>
    )
  }

  if (error) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-gradient-to-br from-background via-background to-muted/20">
        <div className="max-w-md w-full mx-4">
          <div className="rounded-2xl border bg-card text-card-foreground shadow-xl p-8 text-center space-y-4">
            <div className="w-16 h-16 rounded-full bg-destructive/10 flex items-center justify-center mx-auto">
              <span className="text-3xl">⚠️</span>
            </div>
            <h2 className="text-xl font-semibold">Ошибка загрузки</h2>
            <p className="text-muted-foreground">{error}</p>
            <Link
              to="/auth/login"
              className="inline-flex items-center justify-center rounded-lg bg-primary px-6 py-3 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors shadow-md"
            >
              Войти
            </Link>
          </div>
        </div>
      </main>
    )
  }

  if (!user) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-gradient-to-br from-background via-background to-muted/20">
        <div className="max-w-md w-full mx-4">
          <div className="rounded-2xl border bg-card text-card-foreground shadow-xl p-8 text-center space-y-4">
            <div className="w-16 h-16 rounded-full bg-muted flex items-center justify-center mx-auto">
              <span className="text-3xl">🔒</span>
            </div>
            <h2 className="text-xl font-semibold">Требуется авторизация</h2>
            <p className="text-muted-foreground">Пожалуйста, войдите в систему</p>
            <Link
              to="/auth/login"
              className="inline-flex items-center justify-center rounded-lg bg-primary px-6 py-3 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors shadow-md"
            >
              Войти
            </Link>
          </div>
        </div>
      </main>
    )
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20 p-4 md:p-8">
      <div className="max-w-3xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl md:text-4xl font-bold">Мой профиль</h1>
            <p className="text-muted-foreground mt-1">Управление аккаунтом</p>
          </div>
          <Link
            to="/"
            className="inline-flex items-center justify-center rounded-lg border bg-background px-4 py-2 text-sm hover:bg-accent transition-colors"
          >
            ← На главную
          </Link>
        </div>

        <section className="rounded-2xl border bg-card text-card-foreground shadow-xl p-8 space-y-6">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center">
              <span className="text-3xl">
                {user.full_name?.[0]?.toUpperCase() || user.email[0].toUpperCase()}
              </span>
            </div>
            <div>
              <h2 className="text-2xl font-bold">{user.full_name || "Без имени"}</h2>
              <p className="text-muted-foreground">{user.email}</p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="rounded-lg border bg-background/50 p-4 space-y-1">
              <p className="text-xs text-muted-foreground uppercase tracking-wide">
                Email
              </p>
              <p className="font-medium">{user.email}</p>
            </div>

            {user.full_name && (
              <div className="rounded-lg border bg-background/50 p-4 space-y-1">
                <p className="text-xs text-muted-foreground uppercase tracking-wide">
                  Полное имя
                </p>
                <p className="font-medium">{user.full_name}</p>
              </div>
            )}

            {user.plan && (
              <div className="rounded-lg border bg-background/50 p-4 space-y-1">
                <p className="text-xs text-muted-foreground uppercase tracking-wide">
                  Тарифный план
                </p>
                <p className="font-medium capitalize">{user.plan}</p>
              </div>
            )}

            {typeof user.balance_cents === "number" && (
              <div className="rounded-lg border bg-background/50 p-4 space-y-1">
                <p className="text-xs text-muted-foreground uppercase tracking-wide">
                  Баланс
                </p>
                <p className="font-medium">${(user.balance_cents / 100).toFixed(2)}</p>
              </div>
            )}
          </div>
        </section>

        <section className="rounded-2xl border bg-card text-card-foreground shadow-xl p-6 space-y-4">
          <h2 className="text-lg font-semibold">Действия</h2>
          <div className="flex flex-wrap gap-3">
            <Link
              to="/auth/sessions"
              className="inline-flex items-center justify-center rounded-lg border bg-background px-4 py-2 text-sm font-medium hover:bg-accent transition-colors"
            >
              🔐 Мои сессии
            </Link>
            <button
              onClick={handleLogout}
              className="inline-flex items-center justify-center rounded-lg border border-destructive bg-destructive/10 px-4 py-2 text-sm font-medium text-destructive hover:bg-destructive/20 transition-colors disabled:opacity-50"
              disabled={logoutLoading}
            >
              {logoutLoading ? "Выходим..." : "🚪 Выйти"}
            </button>
          </div>
        </section>
      </div>
    </main>
  )
}

export default ProfilePage


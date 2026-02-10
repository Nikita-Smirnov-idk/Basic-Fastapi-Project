import { FormEvent, useMemo, useState } from "react"
import { Link, useNavigate } from "@tanstack/react-router"
import { toast } from "sonner"
import { usePasswordReset } from "@/delivery"

function useQueryParam(name: string): string | null {
  if (typeof window === "undefined") return null
  const params = new URLSearchParams(window.location.search)
  return params.get(name)
}

export function ResetPasswordPage() {
  const navigate = useNavigate()
  const token = useQueryParam("token")
  const { reset, loading } = usePasswordReset()
  const [password, setPassword] = useState("")

  const disabled = useMemo(() => !token || !password || loading, [token, password, loading])

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    if (!token) return
    try {
      const result = await reset(token, password)
      toast.success(result.message || "Пароль успешно изменен!")
      navigate({ to: "/auth/login" })
    } catch (error) {
      console.error("Reset password error:", error)
    }
  }

  if (!token) {
    return (
      <main className="flex min-h-screen items-center justify-center p-4 bg-gradient-to-br from-background via-background to-muted/20">
        <section className="w-full max-w-md rounded-2xl border bg-card text-card-foreground shadow-xl p-8 space-y-6 text-center">
          <div className="w-16 h-16 rounded-full bg-destructive/20 flex items-center justify-center mx-auto">
            <span className="text-3xl">⚠️</span>
          </div>
          <div className="space-y-2">
            <h1 className="text-2xl font-bold">Недействительная ссылка</h1>
            <p className="text-muted-foreground">
              Токен не указан. Пожалуйста, перейдите по ссылке из письма ещё раз.
            </p>
          </div>
          <Link
            to="/auth/recover-password"
            className="inline-flex items-center justify-center rounded-lg bg-primary px-6 py-3 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors shadow-md"
          >
            Запросить новую ссылку
          </Link>
        </section>
      </main>
    )
  }

  return (
    <main className="flex min-h-screen items-center justify-center p-4 bg-gradient-to-br from-background via-background to-muted/20">
      <section className="w-full max-w-md rounded-2xl border bg-card text-card-foreground shadow-xl p-8 space-y-6">
        <div className="space-y-2 text-center">
          <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto">
            <span className="text-3xl">🔑</span>
          </div>
          <h1 className="text-3xl font-bold">Сброс пароля</h1>
          <p className="text-muted-foreground">
            Введите новый пароль для вашего аккаунта
          </p>
        </div>

        <form className="space-y-4" onSubmit={handleSubmit}>
          <div className="space-y-2">
            <label className="block text-sm font-medium" htmlFor="password">
              Новый пароль
            </label>
            <input
              id="password"
              type="password"
              className="w-full rounded-lg border border-input bg-background px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary transition-shadow"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={6}
              disabled={loading}
            />
            <p className="text-xs text-muted-foreground">
              Минимум 6 символов
            </p>
          </div>

          <button
            type="submit"
            className="inline-flex w-full items-center justify-center rounded-lg bg-primary px-4 py-3 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-md hover:shadow-lg"
            disabled={disabled}
          >
            {loading ? (
              <>
                <div className="w-4 h-4 border-2 border-primary-foreground border-t-transparent rounded-full animate-spin mr-2" />
                Сохраняем...
              </>
            ) : (
              "Сохранить новый пароль"
            )}
          </button>
        </form>

        <div className="text-center">
          <Link
            to="/auth/login"
            className="text-xs text-muted-foreground hover:text-foreground transition-colors"
          >
            ← Вернуться к входу
          </Link>
        </div>
      </section>
    </main>
  )
}

export default ResetPasswordPage


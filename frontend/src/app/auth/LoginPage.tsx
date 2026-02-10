import { FormEvent, useState } from "react"
import { Link, useNavigate } from "@tanstack/react-router"
import { toast } from "sonner"
import { useLogin } from "@/delivery"

export function LoginPage() {
  const navigate = useNavigate()
  const { login, loading } = useLogin()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    try {
      const result = await login(email, password)
      toast.success(result.message || "Вход выполнен успешно")
      navigate({ to: "/" })
    } catch (error) {
      console.error("Login error:", error)
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center p-4 bg-gradient-to-br from-background via-background to-muted/20">
      <section className="w-full max-w-md rounded-2xl border bg-card text-card-foreground shadow-xl p-8 space-y-6">
        <div className="space-y-2 text-center">
          <h1 className="text-3xl font-bold">Добро пожаловать</h1>
          <p className="text-muted-foreground">Войдите в свой аккаунт</p>
        </div>

        <form className="space-y-4" onSubmit={handleSubmit}>
          <div className="space-y-2">
            <label className="block text-sm font-medium" htmlFor="email">
              Email
            </label>
            <input
              id="email"
              type="email"
              className="w-full rounded-lg border border-input bg-background px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary transition-shadow"
              placeholder="your@email.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={loading}
            />
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <label className="block text-sm font-medium" htmlFor="password">
                Пароль
              </label>
              <Link
                to="/auth/recover-password"
                className="text-xs text-primary hover:text-primary/80 transition-colors"
              >
                Забыли?
              </Link>
            </div>
            <input
              id="password"
              type="password"
              className="w-full rounded-lg border border-input bg-background px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary transition-shadow"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              disabled={loading}
            />
          </div>

          <button
            type="submit"
            className="inline-flex w-full items-center justify-center rounded-lg bg-primary px-4 py-3 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-md hover:shadow-lg"
            disabled={loading}
          >
            {loading ? (
              <>
                <div className="w-4 h-4 border-2 border-primary-foreground border-t-transparent rounded-full animate-spin mr-2" />
                Входим...
              </>
            ) : (
              "Войти"
            )}
          </button>
        </form>

        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t" />
          </div>
          <div className="relative flex justify-center text-xs uppercase">
            <span className="bg-card px-2 text-muted-foreground">или</span>
          </div>
        </div>

        <div className="text-center text-sm">
          <span className="text-muted-foreground">Нет аккаунта? </span>
          <Link
            to="/auth/signup"
            className="text-primary hover:text-primary/80 font-medium transition-colors"
          >
            Зарегистрироваться
          </Link>
        </div>

        <div className="text-center">
          <Link
            to="/"
            className="text-xs text-muted-foreground hover:text-foreground transition-colors"
          >
            ← На главную
          </Link>
        </div>
      </section>
    </main>
  )
}

export default LoginPage


import { FormEvent, useState } from "react"
import { Link } from "@tanstack/react-router"
import { toast } from "sonner"
import { buildGoogleLoginUrl, startSignupFlow } from "@/application/authService"

export function SignupPage() {
  const [email, setEmail] = useState("")
  const [fullName, setFullName] = useState("")
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      const res = await startSignupFlow(email, fullName)
      toast.success(res.message || "Письмо отправлено!")
      setSuccess(true)
    } catch (error) {
      console.error("Signup error:", error)
    } finally {
      setLoading(false)
    }
  }

  const googleUrl = buildGoogleLoginUrl()

  if (success) {
    return (
      <main className="flex min-h-screen items-center justify-center p-4 bg-gradient-to-br from-background via-background to-muted/20">
        <section className="w-full max-w-md rounded-2xl border bg-card text-card-foreground shadow-xl p-8 space-y-6 text-center">
          <div className="w-16 h-16 rounded-full bg-green-500/20 flex items-center justify-center mx-auto">
            <span className="text-4xl">✉️</span>
          </div>
          <div className="space-y-2">
            <h1 className="text-2xl font-bold">Проверьте вашу почту</h1>
            <p className="text-muted-foreground">
              На адрес <span className="font-medium text-foreground">{email}</span> отправлено письмо со ссылкой для завершения регистрации.
            </p>
          </div>
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

  return (
    <main className="flex min-h-screen items-center justify-center p-4 bg-gradient-to-br from-background via-background to-muted/20">
      <section className="w-full max-w-md rounded-2xl border bg-card text-card-foreground shadow-xl p-8 space-y-6">
        <div className="space-y-2 text-center">
          <h1 className="text-3xl font-bold">Создать аккаунт</h1>
          <p className="text-muted-foreground">Начните работу прямо сейчас</p>
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
            <label className="block text-sm font-medium" htmlFor="fullName">
              Полное имя
            </label>
            <input
              id="fullName"
              type="text"
              className="w-full rounded-lg border border-input bg-background px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary transition-shadow"
              placeholder="Иван Иванов"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
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
                Отправляем...
              </>
            ) : (
              "Зарегистрироваться"
            )}
          </button>
        </form>

        <div className="rounded-lg bg-muted/30 p-4">
          <p className="text-xs text-muted-foreground text-center">
            На указанный email придет ссылка для завершения регистрации
          </p>
        </div>

        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t" />
          </div>
          <div className="relative flex justify-center text-xs uppercase">
            <span className="bg-card px-2 text-muted-foreground">или</span>
          </div>
        </div>

        <a
          href={googleUrl}
          className="inline-flex w-full items-center justify-center gap-2 rounded-lg border bg-background px-4 py-3 text-sm font-medium hover:bg-accent transition-colors"
        >
          <svg className="w-5 h-5" viewBox="0 0 24 24">
            <path
              fill="currentColor"
              d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
            />
            <path
              fill="currentColor"
              d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
            />
            <path
              fill="currentColor"
              d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
            />
            <path
              fill="currentColor"
              d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
            />
          </svg>
          Войти через Google
        </a>

        <div className="text-center text-sm">
          <span className="text-muted-foreground">Уже есть аккаунт? </span>
          <Link
            to="/auth/login"
            className="text-primary hover:text-primary/80 font-medium transition-colors"
          >
            Войти
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

export default SignupPage


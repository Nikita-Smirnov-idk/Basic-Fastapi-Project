import { FormEvent, useState } from "react"
import { Link } from "@tanstack/react-router"
import { toast } from "sonner"
import { usePasswordRecovery } from "@/delivery"

export function RecoverPasswordPage() {
  const { recover, loading } = usePasswordRecovery()
  const [email, setEmail] = useState("")
  const [success, setSuccess] = useState(false)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    try {
      const result = await recover(email)
      toast.success(result.message || "Письмо отправлено")
      setSuccess(true)
    } catch (error) {
      console.error("Password recovery error:", error)
    }
  }

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
              На адрес <span className="font-medium text-foreground">{email}</span> отправлено письмо со ссылкой для восстановления пароля.
            </p>
          </div>
          <div className="flex flex-col gap-3">
            <Link
              to="/auth/login"
              className="inline-flex items-center justify-center rounded-lg bg-primary px-6 py-3 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors shadow-md"
            >
              Вернуться к входу
            </Link>
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

  return (
    <main className="flex min-h-screen items-center justify-center p-4 bg-gradient-to-br from-background via-background to-muted/20">
      <section className="w-full max-w-md rounded-2xl border bg-card text-card-foreground shadow-xl p-8 space-y-6">
        <div className="space-y-2 text-center">
          <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto">
            <span className="text-3xl">🔐</span>
          </div>
          <h1 className="text-3xl font-bold">Восстановление пароля</h1>
          <p className="text-muted-foreground">
            Введите ваш email для получения ссылки восстановления
          </p>
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
              "Отправить письмо"
            )}
          </button>
        </form>

        <div className="text-center text-sm space-y-2">
          <Link
            to="/auth/login"
            className="text-primary hover:text-primary/80 font-medium transition-colors block"
          >
            ← Вернуться к входу
          </Link>
          <Link
            to="/"
            className="text-xs text-muted-foreground hover:text-foreground transition-colors block"
          >
            На главную
          </Link>
        </div>
      </section>
    </main>
  )
}

export default RecoverPasswordPage


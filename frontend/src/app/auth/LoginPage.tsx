import { FormEvent, useEffect, useState } from "react"
import { Link, useNavigate, useSearch } from "@tanstack/react-router"
import { toast } from "sonner"
import { useLogin } from "@/delivery"
import { getGoogleLoginUrl } from "@/infrastructure/authApi"

export function LoginPage() {
  const navigate = useNavigate()
  const { signedOut } = useSearch({ from: "/auth/login" })
  const { login, loading } = useLogin()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")

  useEffect(() => {
    if (signedOut) {
      toast.success("You have been signed out")
      navigate({ to: "/auth/login", search: {}, replace: true })
    }
  }, [signedOut, navigate])

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    try {
      const result = await login(email, password)
      toast.success(result.message || "Login successful")
      navigate({ to: "/" })
    } catch (error) {
      toast.error((error as Error).message)
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center p-4 bg-gradient-to-br from-background via-background to-muted/20">
      <section className="w-full max-w-md rounded-2xl border bg-card text-card-foreground shadow-xl p-8 space-y-6">
        <div className="space-y-2 text-center">
          <h1 className="text-3xl font-bold">Welcome</h1>
          <p className="text-muted-foreground">Sign in to your account</p>
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
                Password
              </label>
              <Link
                to="/auth/recover-password"
                className="text-xs text-primary hover:text-primary/80 transition-colors"
              >
                Forgot?
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
                Signing in...
              </>
            ) : (
              "Sign in"
            )}
          </button>
        </form>

        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t" />
          </div>
          <div className="relative flex justify-center text-xs uppercase">
            <span className="bg-card px-2 text-muted-foreground">or</span>
          </div>
        </div>

        <a
          href={getGoogleLoginUrl()}
          className="inline-flex w-full items-center justify-center gap-2 rounded-lg border border-input bg-background px-4 py-3 text-sm font-medium hover:bg-accent transition-colors"
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
          Sign in with Google
        </a>

        <div className="text-center text-sm">
          <span className="text-muted-foreground">Don&apos;t have an account? </span>
          <Link
            to="/auth/signup"
            className="text-primary hover:text-primary/80 font-medium transition-colors"
          >
            Sign up
          </Link>
        </div>

        <div className="text-center">
          <Link
            to="/"
            className="text-xs text-muted-foreground hover:text-foreground transition-colors"
          >
            ← Back to home
          </Link>
        </div>
      </section>
    </main>
  )
}

export default LoginPage


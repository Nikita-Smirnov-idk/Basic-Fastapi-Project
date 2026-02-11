import { Link } from "@tanstack/react-router"
import { Skeleton } from "@/pkg/components"
import { useHome } from "@/delivery"

export function HomePage() {
  const { data, isLoading, error } = useHome()

  if (isLoading) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-gradient-to-br from-background via-background to-muted/20 px-4 py-12">
        <section className="max-w-3xl w-full">
          <div className="rounded-2xl border bg-card p-8 md:p-12 space-y-8">
            <header className="space-y-4 text-center">
              <Skeleton className="h-12 w-64 mx-auto" />
              <Skeleton className="h-6 w-full max-w-2xl mx-auto" />
            </header>
            <Skeleton className="h-32 w-full rounded-lg" />
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <Skeleton className="h-12 w-32 rounded-lg" />
              <Skeleton className="h-12 w-48 rounded-lg" />
            </div>
          </div>
        </section>
      </main>
    )
  }

  if (error || !data) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-gradient-to-br from-background via-background to-muted/20">
        <div className="max-w-md w-full mx-4">
          <div className="rounded-xl border bg-card text-card-foreground shadow-lg p-8 text-center space-y-4">
            <div className="w-16 h-16 rounded-full bg-destructive/10 flex items-center justify-center mx-auto">
              <span className="text-3xl">⚠️</span>
            </div>
            <h2 className="text-xl font-semibold">Load error</h2>
            <p className="text-muted-foreground">
              Failed to load home page data
            </p>
          </div>
        </div>
      </main>
    )
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-gradient-to-br from-background via-background to-muted/20 px-4 py-12">
      <section className="max-w-3xl w-full">
        <div className="rounded-2xl border bg-card text-card-foreground shadow-xl p-8 md:p-12 space-y-8">
          <header className="space-y-4 text-center">
            <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-primary to-primary/60 bg-clip-text text-transparent">
              {data.title}
            </h1>
            <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto">
              {data.subtitle}
            </p>
          </header>

          <div className="rounded-lg bg-muted/30 p-6">
            <p className="text-muted-foreground leading-relaxed">
              {data.description}
            </p>
          </div>

          <div className="flex flex-col sm:flex-row flex-wrap gap-3 justify-center">
            <Link
              to="/auth/login"
              className="inline-flex items-center justify-center rounded-lg bg-primary px-6 py-3 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors shadow-md hover:shadow-lg"
            >
              Sign in
            </Link>
            <Link
              to="/auth/signup"
              className="inline-flex items-center justify-center rounded-lg border-2 border-primary bg-background px-6 py-3 text-sm font-medium text-foreground hover:bg-primary/10 transition-colors"
            >
              Sign up
            </Link>
          </div>

          <div className="flex flex-wrap gap-2 justify-center pt-4 border-t">
            <Link
              to="/auth/recover-password"
              className="text-xs text-muted-foreground hover:text-foreground transition-colors underline-offset-4 hover:underline"
            >
              Forgot password?
            </Link>
            <span className="text-xs text-muted-foreground">•</span>
            <Link
              to="/auth/sessions"
              className="text-xs text-muted-foreground hover:text-foreground transition-colors underline-offset-4 hover:underline"
            >
              My sessions
            </Link>
            <span className="text-xs text-muted-foreground">•</span>
            <Link
              to="/users/me"
              className="text-xs text-muted-foreground hover:text-foreground transition-colors underline-offset-4 hover:underline"
            >
              Profile
            </Link>
            <span className="text-xs text-muted-foreground">•</span>
            <Link
              to="/yc"
              className="text-xs text-muted-foreground hover:text-foreground transition-colors underline-offset-4 hover:underline"
            >
              YC companies
            </Link>
          </div>
        </div>
      </section>
    </main>
  )
}

export default HomePage


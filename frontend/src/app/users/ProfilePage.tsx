import { Link, useNavigate } from "@tanstack/react-router"
import { toast } from "sonner"
import { Skeleton } from "@/pkg/components"
import { useCurrentUser, useLogout } from "@/delivery"
import { useUserStore } from "@/pkg/stores/userStore"

export function ProfilePage() {
  const navigate = useNavigate()
  const { user, loading, error } = useCurrentUser()
  const { logout, loading: logoutLoading } = useLogout()

  const handleLogout = async () => {
    try {
      await logout()
      useUserStore.getState().clear()
      toast.success("You have been signed out")
      navigate({ to: "/" })
    } catch (error) {
      console.error("Logout error:", error)
    }
  }

  if (loading) {
    return (
      <main className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20 p-4 md:p-8">
        <div className="max-w-3xl mx-auto space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <Skeleton className="h-10 w-48 mb-2" />
              <Skeleton className="h-5 w-32" />
            </div>
            <Skeleton className="h-10 w-32 rounded-lg" />
          </div>
          <section className="rounded-2xl border bg-card p-8 space-y-6">
            <div className="flex items-center gap-4">
              <Skeleton className="w-16 h-16 rounded-full" />
              <div className="space-y-2">
                <Skeleton className="h-8 w-48" />
                <Skeleton className="h-5 w-64" />
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="rounded-lg border bg-background/50 p-4 space-y-2">
                  <Skeleton className="h-4 w-24" />
                  <Skeleton className="h-6 w-32" />
                </div>
              ))}
            </div>
          </section>
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
            <h2 className="text-xl font-semibold">Load error</h2>
            <p className="text-muted-foreground">{error}</p>
            <Link
              to="/auth/login"
              className="inline-flex items-center justify-center rounded-lg bg-primary px-6 py-3 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors shadow-md"
            >
              Sign in
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
            <h2 className="text-xl font-semibold">Authentication required</h2>
            <p className="text-muted-foreground">Please sign in to continue</p>
            <Link
              to="/auth/login"
              className="inline-flex items-center justify-center rounded-lg bg-primary px-6 py-3 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors shadow-md"
            >
              Sign in
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
            <h1 className="text-3xl md:text-4xl font-bold">My profile</h1>
            <p className="text-muted-foreground mt-1">Account settings</p>
          </div>
          <Link
            to="/"
            className="inline-flex items-center justify-center rounded-lg border bg-background px-4 py-2 text-sm hover:bg-accent transition-colors"
          >
            ← Back to home
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
              <h2 className="text-2xl font-bold">{user.full_name || "No name"}</h2>
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
                  Full name
                </p>
                <p className="font-medium">{user.full_name}</p>
              </div>
            )}

            {user.plan && (
              <div className="rounded-lg border bg-background/50 p-4 space-y-1">
                <p className="text-xs text-muted-foreground uppercase tracking-wide">
                  Plan
                </p>
                <p className="font-medium capitalize">{user.plan}</p>
              </div>
            )}

            {typeof user.balance_cents === "number" && (
              <div className="rounded-lg border bg-background/50 p-4 space-y-1">
                <p className="text-xs text-muted-foreground uppercase tracking-wide">
                  Balance
                </p>
                <p className="font-medium">${(user.balance_cents / 100).toFixed(2)}</p>
              </div>
            )}
          </div>
        </section>

        <section className="rounded-2xl border bg-card text-card-foreground shadow-xl p-6 space-y-4">
          <h2 className="text-lg font-semibold">Actions</h2>
          <div className="flex flex-wrap gap-3">
            <Link
              to="/auth/sessions"
              className="inline-flex items-center justify-center rounded-lg border bg-background px-4 py-2 text-sm font-medium hover:bg-accent transition-colors"
            >
              🔐 My sessions
            </Link>
            <button
              onClick={handleLogout}
              className="inline-flex items-center justify-center rounded-lg border border-destructive bg-destructive/10 px-4 py-2 text-sm font-medium text-destructive hover:bg-destructive/20 transition-colors disabled:opacity-50"
              disabled={logoutLoading}
            >
              {logoutLoading ? "Signing out..." : "🚪 Sign out"}
            </button>
          </div>
        </section>
      </div>
    </main>
  )
}

export default ProfilePage


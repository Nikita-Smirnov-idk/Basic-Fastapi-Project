import { createFileRoute, redirect } from "@tanstack/react-router"
import { HttpError } from "@/pkg/httpClient"
import { getMe } from "@/use_cases/userService"
import ProfilePage from "@/app/users/ProfilePage"
import { Skeleton } from "@/pkg/components"

function ProfilePagePending() {
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

export const Route = createFileRoute("/users/me")({
  beforeLoad: async () => {
    try {
      await getMe({ skipTokenRefresh: true, skipErrorToast: true })
    } catch (e) {
      if (e instanceof HttpError && e.status === 429) throw e
      throw redirect({ to: "/auth/login" })
    }
  },
  pendingComponent: ProfilePagePending,
  component: ProfilePage,
})

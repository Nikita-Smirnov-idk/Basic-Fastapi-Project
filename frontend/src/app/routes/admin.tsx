import { createFileRoute, redirect } from "@tanstack/react-router"
import { HttpError } from "@/pkg/httpClient"
import { getMe } from "@/use_cases/userService"
import { AdminLayout } from "@/app/admin/AdminLayout"
import { Skeleton } from "@/pkg/components"

function AdminLayoutPending() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20 p-4 md:p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        <Skeleton className="h-8 w-48" />
        <div className="flex gap-4">
          <Skeleton className="h-10 w-32 rounded-lg" />
          <Skeleton className="h-10 w-24 rounded-lg" />
        </div>
        <Skeleton className="h-64 w-full rounded-xl" />
      </div>
    </main>
  )
}

export const Route = createFileRoute("/admin")({
  beforeLoad: async () => {
    try {
      await getMe({ skipTokenRefresh: true, skipErrorToast: true })
    } catch (e) {
      if (e instanceof HttpError && e.status === 429) throw e
      throw redirect({ to: "/auth/login" })
    }
  },
  pendingComponent: AdminLayoutPending,
  component: AdminLayout,
})

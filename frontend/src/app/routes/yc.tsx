import { createFileRoute, redirect } from "@tanstack/react-router"
import { HttpError } from "@/pkg/httpClient"
import { getMe } from "@/use_cases/userService"
import YCCompaniesPage from "@/app/yc/YCCompaniesPage"
import { CompanyRowSkeleton, Skeleton } from "@/pkg/components"

function YCPagePending() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20 p-4 md:p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="flex items-center justify-between flex-wrap gap-4">
          <div>
            <Skeleton className="h-9 w-48" />
            <Skeleton className="h-5 w-64 mt-2" />
          </div>
          <div className="flex gap-2">
            <Skeleton className="h-10 w-20 rounded-lg" />
            <Skeleton className="h-10 w-16 rounded-lg" />
            <Skeleton className="h-10 w-12 rounded-lg" />
            <Skeleton className="h-10 w-12 rounded-lg" />
          </div>
        </div>
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <Skeleton className="h-8 w-32" />
            <Skeleton className="h-5 w-40" />
          </div>
          <div className="flex flex-col gap-4">
            {Array.from({ length: 5 }).map((_, i) => (
              <CompanyRowSkeleton key={i} />
            ))}
          </div>
        </section>
      </div>
    </main>
  )
}

export const Route = createFileRoute("/yc")({
  beforeLoad: async () => {
    try {
      await getMe({ skipTokenRefresh: true, skipErrorToast: true })
    } catch (e) {
      if (e instanceof HttpError && e.status === 429) throw e
      throw redirect({ to: "/auth/login" })
    }
  },
  pendingComponent: YCPagePending,
  component: YCCompaniesPage,
})

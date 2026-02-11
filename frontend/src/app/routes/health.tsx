import { createFileRoute, redirect } from "@tanstack/react-router"
import { HttpError } from "@/pkg/httpClient"
import { getMe } from "@/use_cases/userService"
import HealthPage from "@/app/health/HealthPage"

export const Route = createFileRoute("/health")({
  beforeLoad: async () => {
    try {
      await getMe({ skipTokenRefresh: true, skipErrorToast: true })
    } catch (e) {
      if (e instanceof HttpError && e.status === 429) throw e
      throw redirect({ to: "/auth/login" })
    }
  },
  component: HealthPage,
})

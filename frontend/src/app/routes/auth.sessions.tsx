import { createFileRoute, redirect } from "@tanstack/react-router"
import { HttpError } from "@/pkg/httpClient"
import { getMe } from "@/use_cases/userService"
import SessionsPage from "@/app/auth/SessionsPage"

export const Route = createFileRoute("/auth/sessions")({
  beforeLoad: async () => {
    try {
      await getMe({ skipTokenRefresh: true, skipErrorToast: true })
    } catch (e) {
      if (e instanceof HttpError && e.status === 429) throw e
      throw redirect({ to: "/auth/login" })
    }
  },
  component: SessionsPage,
})

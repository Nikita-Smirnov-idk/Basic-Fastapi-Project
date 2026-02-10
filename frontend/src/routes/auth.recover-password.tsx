import { createFileRoute } from "@tanstack/react-router"
import RecoverPasswordPage from "@/app/auth/RecoverPasswordPage"

export const Route = createFileRoute("/auth/recover-password")({
  component: RecoverPasswordPage,
})

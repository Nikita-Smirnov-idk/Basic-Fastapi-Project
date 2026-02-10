import { createFileRoute } from "@tanstack/react-router"
import ResetPasswordPage from "@/app/auth/ResetPasswordPage"

export const Route = createFileRoute("/auth/reset-password")({
  component: ResetPasswordPage,
})

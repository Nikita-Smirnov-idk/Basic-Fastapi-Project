import { createFileRoute } from "@tanstack/react-router"
import CompleteSignupPage from "@/app/auth/CompleteSignupPage"

export const Route = createFileRoute("/auth/complete-signup")({
  component: CompleteSignupPage,
})

import { createFileRoute } from "@tanstack/react-router"
import LoginPage from "@/app/auth/LoginPage"

export const Route = createFileRoute("/auth/login")({
  validateSearch: (search: Record<string, unknown>): { signedOut?: string } => ({
    signedOut: typeof search.signedOut === "string" ? search.signedOut : undefined,
  }),
  component: LoginPage,
})

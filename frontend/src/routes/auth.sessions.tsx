import { createFileRoute } from "@tanstack/react-router"
import SessionsPage from "@/app/auth/SessionsPage"

export const Route = createFileRoute("/auth/sessions")({
  component: SessionsPage,
})

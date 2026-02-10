import { createFileRoute } from "@tanstack/react-router"
import LoginPage from "@/app/auth/LoginPage"

export const Route = createFileRoute("/auth/login")({
  component: LoginPage,
})

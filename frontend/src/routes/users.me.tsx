import { createFileRoute } from "@tanstack/react-router"
import ProfilePage from "@/app/users/ProfilePage"

export const Route = createFileRoute("/users/me")({
  component: ProfilePage,
})

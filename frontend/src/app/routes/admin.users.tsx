import { createFileRoute } from "@tanstack/react-router"
import AdminUsersPage from "@/app/admin/AdminUsersPage"

export const Route = createFileRoute("/admin/users")({
  component: AdminUsersPage,
})

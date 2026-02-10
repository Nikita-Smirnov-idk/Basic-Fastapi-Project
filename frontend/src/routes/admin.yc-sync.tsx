import { createFileRoute } from "@tanstack/react-router"
import AdminYCSyncPage from "@/app/admin/AdminYCSyncPage"

export const Route = createFileRoute("/admin/yc-sync")({
  component: AdminYCSyncPage,
})

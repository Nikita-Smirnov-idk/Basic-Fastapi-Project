import { createFileRoute } from "@tanstack/react-router"
import HealthPage from "@/app/health/HealthPage"

export const Route = createFileRoute("/health")({
  component: HealthPage,
})

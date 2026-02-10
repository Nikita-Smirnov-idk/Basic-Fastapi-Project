import { createFileRoute } from "@tanstack/react-router"
import YCCompaniesPage from "@/app/yc/YCCompaniesPage"

export const Route = createFileRoute("/yc")({
  component: YCCompaniesPage,
})

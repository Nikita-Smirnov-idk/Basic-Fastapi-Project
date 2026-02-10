import { createFileRoute } from "@tanstack/react-router"
import HomePage from "@/app/home/HomePage"

export const Route = createFileRoute("/")({
  component: HomePage,
})

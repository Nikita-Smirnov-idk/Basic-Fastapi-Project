import { createFileRoute } from "@tanstack/react-router"
import HomePage from "@/app/home/HomePage"

export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
  head: () => ({
    meta: [
      {
        title: "FeatureBoard — главная",
      },
    ],
  }),
})

function Dashboard() {
  return <HomePage />
}

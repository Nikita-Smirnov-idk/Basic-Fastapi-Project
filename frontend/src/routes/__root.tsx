import { Outlet, createRootRoute } from "@tanstack/react-router"
import { Toaster } from "sonner"
import { Header } from "@/app/Header"

export const Route = createRootRoute({
  component: RootComponent,
})

function RootComponent() {
  return (
    <>
      <Header />
      <main className="pt-16">
        <Outlet />
      </main>
      <Toaster position="top-right" richColors closeButton />
    </>
  )
}

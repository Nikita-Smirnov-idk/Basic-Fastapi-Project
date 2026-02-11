import { Outlet, createRootRoute, useNavigate } from "@tanstack/react-router"
import { Toaster } from "sonner"
import { ErrorBoundary } from "react-error-boundary"
import { Header } from "@/app/routes/Header"

export const Route = createRootRoute({
  component: RootComponent,
})

function RouteErrorFallback({
  error,
  resetErrorBoundary,
}: {
  error: Error
  resetErrorBoundary: () => void
}) {
  const navigate = useNavigate()
  return (
    <main className="flex min-h-[50vh] items-center justify-center p-4">
      <section className="w-full max-w-md rounded-xl border bg-card p-6 space-y-4 text-center">
        <h2 className="text-lg font-semibold">Something went wrong</h2>
        <p className="text-sm text-muted-foreground break-all">{error.message}</p>
        <div className="flex gap-2 justify-center flex-wrap">
          <button
            type="button"
            onClick={() => {
              resetErrorBoundary()
              navigate({ to: "/" })
            }}
            className="rounded-lg bg-primary px-4 py-2 text-sm text-primary-foreground"
          >
            Back to home
          </button>
          <button
            type="button"
            onClick={resetErrorBoundary}
            className="rounded-lg border px-4 py-2 text-sm"
          >
            Try again
          </button>
        </div>
      </section>
    </main>
  )
}

function RootComponent() {
  return (
    <>
      <Header />
      <main className="pt-16">
        <ErrorBoundary FallbackComponent={RouteErrorFallback}>
          <Outlet />
        </ErrorBoundary>
      </main>
      <Toaster position="top-right" richColors closeButton />
    </>
  )
}

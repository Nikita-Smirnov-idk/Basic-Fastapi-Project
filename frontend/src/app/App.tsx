import { RouterProvider, createRouter } from "@tanstack/react-router"
import { routeTree } from "../routeTree.gen"

const router = createRouter({
  routeTree,
  defaultNotFoundComponent: () => {
    return (
      <main className="flex min-h-screen items-center justify-center p-4">
        <section className="w-full max-w-md rounded-xl border bg-card text-card-foreground shadow-sm p-6 space-y-4 text-center">
          <h1 className="text-4xl font-bold">404</h1>
          <p className="text-muted-foreground">Страница не найдена</p>
          <a
            href="/"
            className="inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
          >
            На главную
          </a>
        </section>
      </main>
    )
  },
})

declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router
  }
}

export function App() {
  return <RouterProvider router={router} />
}

export default App


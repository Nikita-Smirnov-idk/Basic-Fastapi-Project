export function NotFoundPage() {
  return (
    <main className="flex min-h-screen items-center justify-center flex-col p-4">
      <div className="flex items-center z-10">
        <div className="flex flex-col ml-4 items-center justify-center p-4">
          <span className="text-6xl md:text-8xl font-bold leading-none mb-4">
            404
          </span>
          <span className="text-2xl font-bold mb-2">Page not found</span>
        </div>
      </div>

      <p className="text-lg text-muted-foreground mb-4 text-center z-10">
        This page does not exist. Check the URL or go back to home.
      </p>
      <div className="z-10">
        <a
          href="/"
          className="mt-4 inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
        >
          Back to home
        </a>
      </div>
    </main>
  )
}

export default NotFoundPage


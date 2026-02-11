export function Skeleton({ className = "" }: { className?: string }) {
  return (
    <div className={`animate-pulse bg-muted rounded ${className}`} />
  )
}

export function CompanyRowSkeleton() {
  return (
    <article className="rounded-xl border bg-card p-4 flex flex-row items-stretch gap-6">
      <div className="flex flex-1 min-w-0 flex-row items-center gap-4 flex-wrap">
        <Skeleton className="w-12 h-12 rounded-lg flex-shrink-0" />
        <div className="min-w-0 flex-1 space-y-2">
          <Skeleton className="h-6 w-48" />
          <div className="flex items-center gap-2">
            <Skeleton className="h-5 w-16 rounded-full" />
            <Skeleton className="h-5 w-20 rounded-full" />
          </div>
          <Skeleton className="h-4 w-full max-w-md" />
          <div className="flex items-center gap-4">
            <Skeleton className="h-4 w-24" />
            <Skeleton className="h-4 w-16" />
          </div>
        </div>
      </div>
      <div className="flex flex-col justify-center border-l border-border pl-4 flex-shrink-0 gap-2">
        <Skeleton className="h-8 w-32" />
        <Skeleton className="h-8 w-32" />
        <Skeleton className="h-8 w-32" />
      </div>
    </article>
  )
}

export function PaginationSkeleton() {
  return (
    <div className="flex items-center justify-center gap-2">
      <Skeleton className="h-10 w-20 rounded-lg" />
      <Skeleton className="h-10 w-10 rounded-lg" />
      <Skeleton className="h-10 w-10 rounded-lg" />
      <Skeleton className="h-10 w-10 rounded-lg" />
      <Skeleton className="h-10 w-10 rounded-lg" />
      <Skeleton className="h-10 w-20 rounded-lg" />
    </div>
  )
}

export function HeaderSkeleton() {
  return (
    <div className="flex items-center justify-between h-16 px-4 md:px-8">
      <Skeleton className="h-6 w-32" />
      <Skeleton className="h-10 w-24 rounded-lg" />
    </div>
  )
}

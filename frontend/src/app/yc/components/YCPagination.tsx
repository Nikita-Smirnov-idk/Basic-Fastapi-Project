type Props = {
  page: number
  totalPages: number
  onPage: (page: number) => void
  canPrev: boolean
  canNext: boolean
}

function paginationSlots(current: number, total: number): number[] {
  if (total <= 0) return []
  if (total <= 5) return Array.from({ length: total }, (_, i) => i + 1)
  const a = 1
  const e = total
  const b = Math.round((1 + current) / 2)
  const d = Math.round((current + total) / 2)
  const slots = [a, b, current, d, e].filter((p) => p >= 1 && p <= total)
  return [...new Set(slots)].sort((x, y) => x - y)
}

export function YCPagination({ page, totalPages, onPage, canPrev, canNext }: Props) {
  const slots = paginationSlots(page, totalPages)

  return (
    <div className="flex items-center justify-center gap-2 flex-wrap">
      <button
        type="button"
        className="rounded-lg bg-primary text-primary-foreground px-4 py-2 text-sm font-medium hover:opacity-90 disabled:opacity-50 disabled:pointer-events-none transition-opacity"
        onClick={() => onPage(page - 1)}
        disabled={!canPrev}
        aria-label="Previous page"
      >
        ←
      </button>
      <div className="flex items-center gap-1">
        {slots.map((p, i) => {
          const showEllipsisBefore = i > 0 && p - slots[i - 1] > 1
          return (
            <span key={p} className="flex items-center gap-1">
              {showEllipsisBefore && <span className="text-muted-foreground px-1">…</span>}
              <button
                type="button"
                className={`min-w-[2rem] rounded-lg px-2 py-1.5 text-sm transition-colors ${
                  p === page
                    ? "bg-primary text-primary-foreground font-semibold"
                    : "border bg-background hover:bg-accent"
                }`}
                onClick={() => onPage(p)}
              >
                {p}
              </button>
            </span>
          )
        })}
      </div>
      <button
        type="button"
        className="rounded-lg bg-primary text-primary-foreground px-4 py-2 text-sm font-medium hover:opacity-90 disabled:opacity-50 disabled:pointer-events-none transition-opacity"
        onClick={() => onPage(page + 1)}
        disabled={!canNext}
        aria-label="Next page"
      >
        →
      </button>
    </div>
  )
}

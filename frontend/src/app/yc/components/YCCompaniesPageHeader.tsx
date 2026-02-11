import { Link } from "@tanstack/react-router"

const btnClass =
  "inline-flex items-center justify-center rounded-lg border bg-background px-4 py-2 text-sm hover:bg-accent transition-colors disabled:opacity-50"

type Props = {
  isPaid: boolean
  hasCompanies: boolean
  onFilterToggle: () => void
  onExportCsv: () => void
  onExportJson: () => void
}

export function YCCompaniesPageHeader({
  isPaid,
  hasCompanies,
  onFilterToggle,
  onExportCsv,
  onExportJson,
}: Props) {
  return (
    <div className="flex items-center justify-between flex-wrap gap-4">
      <div>
        <h1 className="text-3xl md:text-4xl font-bold">YC Directory</h1>
        <p className="text-muted-foreground mt-1">Y Combinator companies database</p>
      </div>
      <div className="flex gap-2 flex-wrap">
        <button type="button" className={btnClass} onClick={onFilterToggle} disabled={!isPaid}>
          Filters
        </button>
        <button type="button" className={btnClass} onClick={onExportCsv} disabled={!isPaid || !hasCompanies}>
          CSV
        </button>
        <button type="button" className={btnClass} onClick={onExportJson} disabled={!isPaid || !hasCompanies}>
          JSON
        </button>
        <Link to="/" className={btnClass}>
          Back to home
        </Link>
      </div>
    </div>
  )
}

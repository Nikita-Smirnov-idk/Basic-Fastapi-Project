import type { YCCompanyFilters } from "@/infrastructure/ycApi"
import type { YCSearchMeta } from "@/domain/yc/types/yc"

type Props = {
  filters: YCCompanyFilters
  meta: YCSearchMeta
  onFilter: <K extends keyof YCCompanyFilters>(key: K, value: YCCompanyFilters[K]) => void
  onApply: () => void
}

const inputClass = "w-full rounded-md border bg-background px-3 py-2 text-sm"
const labelClass = "block text-xs text-muted-foreground uppercase tracking-wide mb-1"

export function YCFiltersSection({ filters, meta, onFilter, onApply }: Props) {
  return (
    <section className="rounded-2xl border bg-card text-card-foreground shadow-lg p-6 space-y-4">
      <h2 className="text-lg font-semibold">Filters</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div>
          <label className={labelClass}>Search</label>
          <input
            type="text"
            className={inputClass}
            placeholder="Name, description..."
            value={filters.q ?? ""}
            onChange={(e) => onFilter("q", e.target.value || undefined)}
          />
        </div>
        <div>
          <label className={labelClass}>Batch</label>
          <select className={inputClass} value={filters.batch ?? ""} onChange={(e) => onFilter("batch", e.target.value || undefined)}>
            <option value="">All</option>
            {meta.batches.map((b) => (
              <option key={b} value={b}>{b}</option>
            ))}
          </select>
        </div>
        <div>
          <label className={labelClass}>Year</label>
          <select
            className={inputClass}
            value={filters.year ?? ""}
            onChange={(e) => onFilter("year", e.target.value ? Number(e.target.value) : undefined)}
          >
            <option value="">All</option>
            {meta.years.map((y) => (
              <option key={y} value={y}>{y}</option>
            ))}
          </select>
        </div>
        <div>
          <label className={labelClass}>Status</label>
          <select
            className={inputClass}
            value={filters.status_filter ?? ""}
            onChange={(e) => onFilter("status_filter", e.target.value || undefined)}
          >
            <option value="">All</option>
            {meta.statuses.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>
        <div>
          <label className={labelClass}>Industry</label>
          <select
            className={inputClass}
            value={filters.industry ?? ""}
            onChange={(e) => onFilter("industry", e.target.value || undefined)}
          >
            <option value="">All</option>
            {meta.industries.map((i) => (
              <option key={i} value={i}>{i}</option>
            ))}
          </select>
        </div>
        <div className="flex items-end gap-2">
          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" checked={filters.is_hiring === true} onChange={(e) => onFilter("is_hiring", e.target.checked ? true : undefined)} />
            Hiring
          </label>
          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" checked={filters.nonprofit === true} onChange={(e) => onFilter("nonprofit", e.target.checked ? true : undefined)} />
            Nonprofit
          </label>
          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" checked={filters.top_company === true} onChange={(e) => onFilter("top_company", e.target.checked ? true : undefined)} />
            Top
          </label>
        </div>
      </div>
      <button type="button" className="rounded-lg bg-primary px-4 py-2 text-sm text-primary-foreground" onClick={onApply}>
        Apply
      </button>
    </section>
  )
}

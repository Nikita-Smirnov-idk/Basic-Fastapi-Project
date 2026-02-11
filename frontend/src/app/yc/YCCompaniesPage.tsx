import { useCallback, useEffect, useState } from "react"
import type { YCCompany } from "@/domain/yc/types/yc"
import type { YCCompanyFilters } from "@/infrastructure/ycApi"
import { buildCompaniesCsv, buildCompaniesJson, downloadBlob } from "@/pkg/ycExport"
import { CompanyRowSkeleton } from "@/pkg/components"
import { useCurrentUser, useYCCompanies, useYCMeta } from "@/delivery"
import {
  YCCompaniesPageHeader,
  YCFiltersSection,
  YCCompanyRow,
  YCCompanyModal,
  YCPagination,
} from "./components"

export function YCCompaniesPage() {
  const { refetch: refetchProfile } = useCurrentUser()

  const [page, setPage] = useState(1)
  const [filters, setFilters] = useState<YCCompanyFilters>({})
  const [filterOpen, setFilterOpen] = useState(false)
  const [modalCompany, setModalCompany] = useState<YCCompany | null>(null)

  const { companies, loading, error, pageSize, totalPages, canNext, canPrev, isPaid } =
    useYCCompanies(filters, page)

  const companiesLength = companies?.data.length
  useEffect(() => {
    if (companiesLength === 15) {
      void refetchProfile()
    }
  }, [companiesLength, refetchProfile])

  const { meta } = useYCMeta()

  const setFilter = useCallback(<K extends keyof YCCompanyFilters>(key: K, value: YCCompanyFilters[K]) => {
    setFilters((prev) => ({ ...prev, [key]: value === "" || value === undefined ? undefined : value }))
    setPage(1)
  }, [])

  const applyFilters = useCallback(() => {
    setPage(1)
    setFilterOpen(false)
  }, [])

  const exportCsv = useCallback(() => {
    if (!companies?.data.length) return
    downloadBlob(buildCompaniesCsv(companies.data), "yc_companies.csv", "text/csv;charset=utf-8")
  }, [companies])

  const exportJson = useCallback(() => {
    if (!companies?.data.length) return
    downloadBlob(buildCompaniesJson(companies.data), "yc_companies.json", "application/json")
  }, [companies])

  useEffect(() => {
    if (!modalCompany) return
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setModalCompany(null)
    }
    window.addEventListener("keydown", onKey)
    return () => window.removeEventListener("keydown", onKey)
  }, [modalCompany])

  return (
    <main className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20 p-4 md:p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        <YCCompaniesPageHeader
          isPaid={isPaid}
          hasCompanies={Boolean(companies?.data.length)}
          onFilterToggle={() => setFilterOpen((v) => !v)}
          onExportCsv={exportCsv}
          onExportJson={exportJson}
        />

        {filterOpen && meta && isPaid && (
          <YCFiltersSection filters={filters} meta={meta} onFilter={setFilter} onApply={applyFilters} />
        )}

        <section className="space-y-4">
          <div className="flex items-center justify-between flex-wrap gap-2">
            <h2 className="text-2xl font-semibold">Companies</h2>
            {companies && (
              <span className="text-sm text-muted-foreground">
                Total: <span className="font-semibold">{companies.count}</span>
                {!isPaid && <span className="ml-2">(free: first page, {pageSize} per page)</span>}
              </span>
            )}
          </div>

          {(companies?.data.length ?? 0) > 0 && (
            <YCPagination
              page={page}
              totalPages={totalPages}
              onPage={setPage}
              canPrev={canPrev}
              canNext={canNext}
            />
          )}

          <div className="min-h-[50vh] flex flex-col">
            {loading && !companies && (
              <div className="flex flex-col gap-4">
                {Array.from({ length: 5 }).map((_, i) => (
                  <CompanyRowSkeleton key={i} />
                ))}
              </div>
            )}

            {error && (
              <div className="rounded-xl border bg-destructive/10 border-destructive/20 p-6 text-center">
                <h3 className="font-semibold mb-2">Load error</h3>
                <p className="text-sm text-muted-foreground">{error}</p>
              </div>
            )}

            {!loading && companies && companies.data.length === 0 && (
              <div className="flex flex-1 items-center justify-center py-20">
                <p className="text-muted-foreground">No companies found</p>
              </div>
            )}

            {companies && companies.data.length > 0 && (
              <div className="flex flex-col gap-4">
                {loading && (
                  <div className="flex flex-col gap-4">
                    {Array.from({ length: 3 }).map((_, i) => (
                      <CompanyRowSkeleton key={`skeleton-${i}`} />
                    ))}
                  </div>
                )}
                {companies.data.map((company) => (
                  <YCCompanyRow key={company.yc_id} company={company} onSelect={setModalCompany} />
                ))}
              </div>
            )}
          </div>

          {(companies?.data.length ?? 0) > 0 && (
            <YCPagination
              page={page}
              totalPages={totalPages}
              onPage={setPage}
              canPrev={canPrev}
              canNext={canNext}
            />
          )}

          {modalCompany && <YCCompanyModal company={modalCompany} onClose={() => setModalCompany(null)} />}
        </section>
      </div>
    </main>
  )
}

export default YCCompaniesPage

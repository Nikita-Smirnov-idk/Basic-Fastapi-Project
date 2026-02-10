import { Link } from "@tanstack/react-router"
import { useYCCompanies, useYCMeta } from "@/delivery"

export function YCCompaniesPage() {
  const { companies, loading, error, reload } = useYCCompanies()
  const { meta } = useYCMeta()

  return (
    <main className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20 p-4 md:p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl md:text-4xl font-bold">YC Directory</h1>
            <p className="text-muted-foreground mt-1">
              База данных компаний Y Combinator
            </p>
          </div>
          <div className="flex gap-2">
            <button
              className="inline-flex items-center justify-center rounded-lg border bg-background px-4 py-2 text-sm hover:bg-accent transition-colors disabled:opacity-50"
              onClick={reload}
              disabled={loading}
            >
              🔄 Обновить
            </button>
            <Link
              to="/"
              className="inline-flex items-center justify-center rounded-lg border bg-background px-4 py-2 text-sm hover:bg-accent transition-colors"
            >
              ← На главную
            </Link>
          </div>
        </div>

        {meta && (
          <section className="rounded-2xl border bg-card text-card-foreground shadow-lg p-6 space-y-3">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <span>📊</span> Доступные фильтры
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div className="space-y-1">
                <p className="text-xs text-muted-foreground uppercase tracking-wide">
                  Годы
                </p>
                <p className="font-medium">{meta.years.join(", ")}</p>
              </div>
              <div className="space-y-1">
                <p className="text-xs text-muted-foreground uppercase tracking-wide">
                  Статусы
                </p>
                <p className="font-medium">{meta.statuses.join(", ")}</p>
              </div>
              <div className="space-y-1">
                <p className="text-xs text-muted-foreground uppercase tracking-wide">
                  Индустрии
                </p>
                <p className="font-medium line-clamp-2">
                  {meta.industries.slice(0, 5).join(", ")}
                  {meta.industries.length > 5 && "..."}
                </p>
              </div>
            </div>
          </section>
        )}

        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-semibold flex items-center gap-2">
              <span>🏢</span> Компании
            </h2>
            {companies && (
              <span className="text-sm text-muted-foreground">
                Всего: <span className="font-semibold">{companies.count}</span>
              </span>
            )}
          </div>

          {loading && (
            <div className="flex items-center justify-center py-20">
              <div className="text-center space-y-4">
                <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto" />
                <p className="text-muted-foreground">Загружаем компании...</p>
              </div>
            </div>
          )}

          {error && (
            <div className="rounded-xl border bg-destructive/10 border-destructive/20 p-6 text-center">
              <div className="w-12 h-12 rounded-full bg-destructive/20 flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">⚠️</span>
              </div>
              <h3 className="font-semibold mb-2">Ошибка загрузки</h3>
              <p className="text-sm text-muted-foreground">{error}</p>
            </div>
          )}

          {companies && companies.data.length === 0 && (
            <div className="text-center py-20">
              <p className="text-muted-foreground">Компании не найдены</p>
            </div>
          )}

          {companies && companies.data.length > 0 && (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {companies.data.map((company) => (
                <article
                  key={company.yc_id}
                  className="rounded-xl border bg-card text-card-foreground p-5 space-y-3 hover:shadow-lg transition-shadow"
                >
                  <div className="space-y-1">
                    <h3 className="font-semibold text-lg">{company.name}</h3>
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-xs bg-primary/10 text-primary px-2 py-0.5 rounded-full">
                        {company.batch}
                      </span>
                      <span className="text-xs bg-muted text-muted-foreground px-2 py-0.5 rounded-full">
                        {company.status}
                      </span>
                      {company.top_company && (
                        <span className="text-xs bg-yellow-500/20 text-yellow-700 dark:text-yellow-300 px-2 py-0.5 rounded-full">
                          ⭐ Top
                        </span>
                      )}
                    </div>
                  </div>

                  {company.one_liner && (
                    <p className="text-sm text-muted-foreground line-clamp-2">
                      {company.one_liner}
                    </p>
                  )}

                  <div className="flex items-center gap-4 text-xs text-muted-foreground">
                    {company.industry && (
                      <div className="flex items-center gap-1">
                        <span>🏭</span>
                        <span>{company.industry}</span>
                      </div>
                    )}
                    {company.team_size && (
                      <div className="flex items-center gap-1">
                        <span>👥</span>
                        <span>{company.team_size}</span>
                      </div>
                    )}
                  </div>

                  {(company.is_hiring || company.nonprofit) && (
                    <div className="flex flex-wrap gap-2">
                      {company.is_hiring && (
                        <span className="text-xs bg-green-500/20 text-green-700 dark:text-green-300 px-2 py-1 rounded">
                          💼 Hiring
                        </span>
                      )}
                      {company.nonprofit && (
                        <span className="text-xs bg-blue-500/20 text-blue-700 dark:text-blue-300 px-2 py-1 rounded">
                          🤝 Nonprofit
                        </span>
                      )}
                    </div>
                  )}
                </article>
              ))}
            </div>
          )}
        </section>
      </div>
    </main>
  )
}

export default YCCompaniesPage


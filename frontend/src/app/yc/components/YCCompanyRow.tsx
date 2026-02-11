import type { YCCompany } from "@/domain/yc/types/yc"
import { CompanyLogo } from "./CompanyLogo"
import { FounderLinks } from "./FounderLinks"

type Props = {
  company: YCCompany
  onSelect: (company: YCCompany) => void
}

export function YCCompanyRow({ company, onSelect }: Props) {
  return (
    <article
      role="button"
      tabIndex={0}
      className="rounded-xl border bg-card text-card-foreground p-4 flex flex-row items-stretch gap-6 hover:shadow-lg transition-shadow cursor-pointer"
      onClick={() => onSelect(company)}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault()
          onSelect(company)
        }
      }}
    >
      <div className="flex flex-1 min-w-0 flex-row items-center gap-4 flex-wrap">
        <CompanyLogo logoUrl={company.small_logo_thumb_url} name={company.name} size="sm" />
        <div className="min-w-0 flex-1 space-y-1">
          <h3 className="font-semibold text-lg truncate">{company.name}</h3>
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs bg-primary/10 text-primary px-2 py-0.5 rounded-full">{company.batch}</span>
            <span className="text-xs bg-muted text-muted-foreground px-2 py-0.5 rounded-full">{company.status}</span>
            {company.top_company && (
              <span className="text-xs bg-yellow-500/20 text-yellow-700 dark:text-yellow-300 px-2 py-0.5 rounded-full">Top</span>
            )}
          </div>
          {company.one_liner && <p className="text-sm text-muted-foreground line-clamp-1">{company.one_liner}</p>}
          <div className="flex items-center gap-4 text-xs text-muted-foreground">
            {company.industry && <span>{company.industry}</span>}
            {company.team_size != null && <span>{company.team_size}</span>}
          </div>
          {(company.is_hiring || company.nonprofit) && (
            <div className="flex flex-wrap gap-2">
              {company.is_hiring && (
                <span className="text-xs bg-green-500/20 text-green-700 dark:text-green-300 px-2 py-1 rounded">Hiring</span>
              )}
              {company.nonprofit && (
                <span className="text-xs bg-blue-500/20 text-blue-700 dark:text-blue-300 px-2 py-1 rounded">Nonprofit</span>
              )}
            </div>
          )}
        </div>
      </div>
      {company.founders?.length > 0 && (
        <div className="flex flex-col justify-center border-l border-border pl-4 flex-shrink-0">
          <FounderLinks founders={company.founders} prefix={String(company.yc_id)} rowHeight="h-8 min-h-8" />
        </div>
      )}
    </article>
  )
}

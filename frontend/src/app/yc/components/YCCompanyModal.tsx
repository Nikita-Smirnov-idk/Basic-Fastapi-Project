import type { YCCompany } from "@/domain/yc/types/yc"
import { CompanyLogo } from "./CompanyLogo"
import { FounderLinks } from "./FounderLinks"

type Props = {
  company: YCCompany
  onClose: () => void
}

const companySiteUrl = (c: YCCompany) => c.website || c.url || "#"

export function YCCompanyModal({ company, onClose }: Props) {
  const siteUrl = companySiteUrl(company)
  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
      role="dialog"
      aria-modal="true"
      onClick={onClose}
    >
      <div
        className="rounded-xl border bg-card text-card-foreground p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex justify-between items-start gap-4 mb-4">
          <div className="flex gap-3 min-w-0">
            <a href={siteUrl} target="_blank" rel="noopener noreferrer" className="flex-shrink-0">
              <CompanyLogo logoUrl={company.small_logo_thumb_url} name={company.name} size="md" />
            </a>
            <div className="min-w-0">
              <h2 className="text-xl font-semibold">{company.name}</h2>
              <div className="flex items-center gap-2 flex-wrap mt-1">
                <span className="text-xs bg-primary/10 text-primary px-2 py-0.5 rounded-full">{company.batch}</span>
                <span className="text-xs bg-muted text-muted-foreground px-2 py-0.5 rounded-full">{company.status}</span>
                {company.top_company && (
                  <span className="text-xs bg-yellow-500/20 text-yellow-700 dark:text-yellow-300 px-2 py-0.5 rounded-full">Top</span>
                )}
              </div>
            </div>
          </div>
          <button type="button" className="rounded-lg border bg-background px-3 py-1.5 text-sm hover:bg-accent" onClick={onClose}>
            Close
          </button>
        </div>

        {company.one_liner && <p className="text-sm text-muted-foreground mb-3">{company.one_liner}</p>}

        <dl className="grid grid-cols-1 sm:grid-cols-2 gap-x-4 gap-y-2 text-sm mb-3">
          {company.slug && (
            <>
              <dt className="text-muted-foreground">Slug</dt>
              <dd>{company.slug}</dd>
            </>
          )}
          {company.batch_code && (
            <>
              <dt className="text-muted-foreground">Batch code</dt>
              <dd>{company.batch_code}</dd>
            </>
          )}
          <dt className="text-muted-foreground">Year</dt>
          <dd>{company.year}</dd>
          {company.industry && (
            <>
              <dt className="text-muted-foreground">Industry</dt>
              <dd>{company.industry}</dd>
            </>
          )}
          {company.team_size != null && (
            <>
              <dt className="text-muted-foreground">Team size</dt>
              <dd>{company.team_size}</dd>
            </>
          )}
          {company.all_locations && (
            <>
              <dt className="text-muted-foreground">Locations</dt>
              <dd>{company.all_locations}</dd>
            </>
          )}
        </dl>

        <div className="flex flex-wrap gap-2 mb-3">
          {company.website && (
            <a href={company.website} target="_blank" rel="noopener noreferrer" className="text-primary hover:underline text-sm">
              Website
            </a>
          )}
          <a href={company.url} target="_blank" rel="noopener noreferrer" className="text-primary hover:underline text-sm">
            YC profile
          </a>
        </div>

        {(company.is_hiring || company.nonprofit) && (
          <div className="flex flex-wrap gap-2 mb-3">
            {company.is_hiring && (
              <span className="text-xs bg-green-500/20 text-green-700 dark:text-green-300 px-2 py-1 rounded">Hiring</span>
            )}
            {company.nonprofit && (
              <span className="text-xs bg-blue-500/20 text-blue-700 dark:text-blue-300 px-2 py-1 rounded">Nonprofit</span>
            )}
          </div>
        )}

        {company.tags?.length > 0 && (
          <div className="mb-3">
            <h4 className="text-sm font-medium mb-1">Tags</h4>
            <p className="text-sm text-muted-foreground">{company.tags.join(", ")}</p>
          </div>
        )}
        {(company.industries?.length ?? 0) > 0 && (
          <div className="mb-3">
            <h4 className="text-sm font-medium mb-1">Industries</h4>
            <p className="text-sm text-muted-foreground">{(company.industries ?? []).join(", ")}</p>
          </div>
        )}
        {(company.regions?.length ?? 0) > 0 && (
          <div className="mb-3">
            <h4 className="text-sm font-medium mb-1">Regions</h4>
            <p className="text-sm text-muted-foreground">{(company.regions ?? []).join(", ")}</p>
          </div>
        )}

        {company.founders?.length > 0 && (
          <div className="border-t border-border pt-3">
            <h4 className="text-sm font-medium mb-2">Founders</h4>
            <div className="flex flex-col gap-2">
              <FounderLinks founders={company.founders} prefix={`modal-${company.yc_id}`} nameWidth="w-40" />
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

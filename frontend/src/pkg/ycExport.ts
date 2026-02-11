import type { YCCompany } from "@/domain/yc/types/yc"

function escapeCsvCell(value: string): string {
  const s = String(value ?? "")
  if (s.includes(",") || s.includes('"') || s.includes("\n") || s.includes("\r")) {
    return `"${s.replace(/"/g, '""')}"`
  }
  return s
}

const LINKEDIN_ICON_URL =
  "https://upload.wikimedia.org/wikipedia/commons/8/81/LinkedIn_icon.svg"
const X_ICON_URL =
  "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/X_%28formerly_Twitter%29_logo_late_2025.svg/960px-X_%28formerly_Twitter%29_logo_late_2025.svg.png"

export { LINKEDIN_ICON_URL, X_ICON_URL }

function founderContactWithLink(name: string, url: string | null | undefined): string {
  if (!url) return ""
  return `${name} (${url})`
}

export function buildCompaniesCsv(companies: YCCompany[]): string {
  const headers = [
    "id",
    "name",
    "slug",
    "batch",
    "batch_code",
    "year",
    "status",
    "industry",
    "team_size",
    "website",
    "all_locations",
    "one_liner",
    "small_logo_thumb_url",
    "url",
    "founders",
    "founders_twitter",
    "founders_linkedin",
    "is_hiring",
    "nonprofit",
    "top_company",
    "tags",
    "industries",
    "regions",
  ]
  const rows = companies.map((c) => {
    const founderNames = c.founders?.map((f) => f.name).join("; ") ?? ""
    const founderTwitters =
      c.founders?.map((f) => founderContactWithLink(f.name, f.twitter_url)).filter(Boolean).join("; ") ?? ""
    const founderLinkedins =
      c.founders?.map((f) => founderContactWithLink(f.name, f.linkedin_url)).filter(Boolean).join("; ") ?? ""
    const tags = (c.tags ?? []).join("; ")
    const industries = (c.industries ?? []).join("; ")
    const regions = (c.regions ?? []).join("; ")
    return [
      escapeCsvCell(String(c.yc_id)),
      escapeCsvCell(c.name),
      escapeCsvCell(c.slug),
      escapeCsvCell(c.batch),
      escapeCsvCell(c.batch_code ?? ""),
      escapeCsvCell(String(c.year)),
      escapeCsvCell(c.status),
      escapeCsvCell(c.industry ?? ""),
      escapeCsvCell(String(c.team_size ?? "")),
      escapeCsvCell(c.website ?? ""),
      escapeCsvCell(c.all_locations ?? ""),
      escapeCsvCell(c.one_liner ?? ""),
      escapeCsvCell(c.small_logo_thumb_url ?? ""),
      escapeCsvCell(c.url ?? ""),
      escapeCsvCell(founderNames),
      escapeCsvCell(founderTwitters),
      escapeCsvCell(founderLinkedins),
      escapeCsvCell(c.is_hiring ? "1" : "0"),
      escapeCsvCell(c.nonprofit ? "1" : "0"),
      escapeCsvCell(c.top_company ? "1" : "0"),
      escapeCsvCell(tags),
      escapeCsvCell(industries),
      escapeCsvCell(regions),
    ].join(",")
  })
  return [headers.join(","), ...rows].join("\n")
}

export function buildCompaniesJson(companies: YCCompany[]): string {
  return JSON.stringify(companies, null, 2)
}

export function downloadBlob(content: string, filename: string, mimeType: string): void {
  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const a = document.createElement("a")
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

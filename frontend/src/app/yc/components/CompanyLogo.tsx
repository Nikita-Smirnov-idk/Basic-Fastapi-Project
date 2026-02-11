const MISSING_LOGO_PATH = "/company/thumb/missing.png"

function isMissingLogo(url: string | null | undefined): boolean {
  return Boolean(url?.includes(MISSING_LOGO_PATH))
}

function initials(name: string): string {
  return name.slice(0, 2).toUpperCase()
}

type Props = {
  logoUrl: string | null | undefined
  name: string
  size?: "sm" | "md"
  className?: string
}

const sizeClass = { sm: "w-12 h-12 text-sm", md: "w-14 h-14 text-base" }

export function CompanyLogo({ logoUrl, name, size = "sm", className = "" }: Props) {
  const showPlaceholder = !logoUrl || isMissingLogo(logoUrl)
  const sizeCn = sizeClass[size]

  if (showPlaceholder) {
    return (
      <div
        className={`rounded-lg bg-muted flex-shrink-0 flex items-center justify-center text-black font-semibold ${sizeCn} ${className}`}
      >
        {initials(name)}
      </div>
    )
  }

  return (
    <img
      src={logoUrl}
      alt=""
      className={`rounded-lg object-contain flex-shrink-0 bg-muted ${sizeCn} ${className}`}
    />
  )
}

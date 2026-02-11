import type { YCFounder } from "@/domain/yc/types/yc"
import { LINKEDIN_ICON_URL, X_ICON_URL } from "@/pkg/ycExport"

const btnClass = "inline-flex opacity-80 hover:opacity-100"
const iconClass = "w-4 h-4 object-contain"

export function FounderLinks({
  founders,
  prefix,
  rowHeight,
  nameWidth,
}: {
  founders: YCFounder[]
  prefix: string
  rowHeight?: string
  nameWidth?: string
}) {
  return (
    <>
      {founders.map((f, i) => (
        <div key={`${prefix}-${i}`} className={`flex items-center gap-3 text-sm ${rowHeight ?? ""}`}>
          <span className={`text-muted-foreground truncate ${nameWidth ?? "w-32"}`}>{f.name}</span>
          <span className="w-5 flex justify-center" onClick={(e) => e.stopPropagation()}>
            {f.linkedin_url ? (
              <a href={f.linkedin_url} target="_blank" rel="noopener noreferrer" className={btnClass} aria-label="LinkedIn">
                <img src={LINKEDIN_ICON_URL} alt="" className={iconClass} />
              </a>
            ) : (
              <span className="w-4" />
            )}
          </span>
          <span className="w-5 flex justify-center" onClick={(e) => e.stopPropagation()}>
            {f.twitter_url ? (
              <a href={f.twitter_url} target="_blank" rel="noopener noreferrer" className={btnClass} aria-label="Twitter">
                <img src={X_ICON_URL} alt="" className={iconClass} />
              </a>
            ) : (
              <span className="w-4" />
            )}
          </span>
        </div>
      ))}
    </>
  )
}

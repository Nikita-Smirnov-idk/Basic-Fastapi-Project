export interface YCFounder {
  name: string
  twitter_url?: string | null
  linkedin_url?: string | null
}

export interface YCCompany {
  yc_id: number
  name: string
  slug: string
  batch: string
  batch_code: string
  year: number
  status: string
  industry?: string | null
  website?: string | null
  all_locations?: string | null
  one_liner?: string | null
  team_size?: number | null
  small_logo_thumb_url?: string | null
  url: string
  is_hiring: boolean
  nonprofit: boolean
  top_company: boolean
  tags: string[]
  industries?: string[]
  regions?: string[]
  founders: YCFounder[]
}

export interface YCCompanies {
  data: YCCompany[]
  count: number
}

export interface YCSearchMeta {
  statuses: string[]
  years: number[]
  batches: string[]
  industries: string[]
}

export interface YCSyncState {
  last_started_at: string | null
  last_finished_at: string | null
  last_success_at: string | null
  last_error: string | null
  last_item_count: number | null
}


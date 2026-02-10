export interface AuthMessage {
  message: string
}

export interface Session {
  id: string
  family_id: string
  user_agent: string | null
  created_at: string
  last_used_at: string | null
  is_current: boolean
}

export interface SessionsList {
  sessions: Session[]
  total: number
}


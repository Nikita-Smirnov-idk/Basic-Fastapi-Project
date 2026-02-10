export interface User {
  id: string
  email: string
  full_name: string | null
  is_active: boolean
  is_superuser: boolean
  plan?: string | null
  balance_cents?: number | null
}


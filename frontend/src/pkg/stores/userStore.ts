import { create } from "zustand"
import type { User } from "@/domain/user/types/user"
import { HttpError } from "@/pkg/httpClient"
import { getMe } from "@/use_cases/userService"

interface UserState {
  user: User | null
  loading: boolean
  error: string | null
  authChecked: boolean
  setUser: (user: User | null) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  fetchUser: (force?: boolean) => Promise<void>
  clear: () => void
}

const store = create<UserState>((set, get) => ({
  user: null,
  loading: false,
  error: null,
  authChecked: false,
  setUser: (user) => set({ user }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  fetchUser: async (force) => {
    if (get().loading) return
    if (get().user && !force) return
    set({ loading: true, error: null })
    try {
      const user = await getMe({ skipErrorToast: true, skipTokenRefresh: true })
      set({ user, loading: false, authChecked: true })
    } catch (e) {
      const isRateLimit = e instanceof HttpError && e.status === 429
      set({
        error: (e as Error).message,
        loading: false,
        user: isRateLimit ? get().user : null,
        authChecked: true,
      })
    }
  },
  clear: () => set({ user: null, loading: false, error: null, authChecked: false }),
}))

export const useUserStore = store

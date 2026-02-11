import { Link, useLocation, useNavigate } from "@tanstack/react-router"
import { useEffect, useState } from "react"
import * as DropdownMenu from "@radix-ui/react-dropdown-menu"
import { useLogout } from "@/delivery"
import { useUserStore } from "@/pkg/stores/userStore"
import { HeaderSkeleton } from "@/pkg/components"

const PROJECT_NAME = import.meta.env.VITE_PROJECT_NAME || "FeatureBoard"

export function Header() {
  const navigate = useNavigate()
  const location = useLocation()
  const { user, loading, authChecked, fetchUser } = useUserStore()
  const { logout } = useLogout()
  const [scrolled, setScrolled] = useState(false)
  const isHome = location.pathname === "/"

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20)
    }
    window.addEventListener("scroll", handleScroll, { passive: true })
    return () => window.removeEventListener("scroll", handleScroll)
  }, [])

  useEffect(() => {
    if (!authChecked && !loading) {
      void fetchUser()
    }
  }, [authChecked, loading, fetchUser])

  const handleLogout = async () => {
    try {
      await logout()
      useUserStore.getState().clear()
      navigate({ to: "/auth/login", search: { signedOut: "1" } })
    } catch (error) {
      console.error("Logout error:", error)
    }
  }

  const initials = user?.full_name
    ? user.full_name
        .split(" ")
        .map((n) => n[0])
        .join("")
        .toUpperCase()
        .slice(0, 2)
    : user?.email?.[0]?.toUpperCase() ?? "?"

  if (loading && !user) {
    return (
      <header className="fixed top-0 left-0 right-0 z-50 bg-transparent">
        <div className="max-w-7xl mx-auto px-4 md:px-8">
          <HeaderSkeleton />
        </div>
      </header>
    )
  }

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled
          ? "bg-background/80 backdrop-blur-md border-b border-border/50 shadow-sm"
          : "bg-transparent"
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 md:px-8">
        <div className="flex items-center justify-between h-16">
          <Link
            to="/"
            className="text-xl font-bold text-foreground hover:opacity-80 transition-opacity"
          >
            {PROJECT_NAME}
          </Link>

          {user ? (
            <DropdownMenu.Root>
              <DropdownMenu.Trigger asChild>
                <button
                  type="button"
                  className="flex items-center gap-2 rounded-lg px-3 py-2 hover:bg-accent transition-colors outline-none"
                  aria-label="Profile"
                >
                  <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center text-sm font-semibold text-primary">
                    {initials}
                  </div>
                  <span className="hidden sm:inline text-sm font-medium">{user.full_name || user.email}</span>
                </button>
              </DropdownMenu.Trigger>
              <DropdownMenu.Portal>
                <DropdownMenu.Content
                  className="min-w-[12rem] rounded-lg border bg-popover text-popover-foreground shadow-lg p-1 z-50"
                  align="end"
                  sideOffset={8}
                >
                  <DropdownMenu.Item asChild>
                    <Link
                      to="/users/me"
                      className="flex w-full rounded-md px-3 py-2 text-sm hover:bg-accent transition-colors outline-none cursor-pointer"
                    >
                      Profile
                    </Link>
                  </DropdownMenu.Item>
                  <DropdownMenu.Separator className="h-px bg-border my-1" />
                  <DropdownMenu.Item asChild>
                    <button
                      type="button"
                      onClick={handleLogout}
                      className="flex w-full rounded-md px-3 py-2 text-sm hover:bg-accent transition-colors outline-none cursor-pointer text-destructive"
                    >
                      Sign out
                    </button>
                  </DropdownMenu.Item>
                </DropdownMenu.Content>
              </DropdownMenu.Portal>
            </DropdownMenu.Root>
          ) : (
            <div className="flex items-center gap-2">
              {isHome ? (
                <>
                  <Link
                    to="/auth/login"
                    className="rounded-lg border bg-background px-4 py-2 text-sm hover:bg-accent transition-colors"
                  >
                    Sign in
                  </Link>
                  <Link
                    to="/auth/signup"
                    className="rounded-lg bg-primary px-4 py-2 text-sm text-primary-foreground hover:opacity-90 transition-opacity"
                  >
                    Sign up
                  </Link>
                </>
              ) : (
                <>
                  <button
                    type="button"
                    onClick={() => navigate({ to: "/auth/login" })}
                    className="rounded-lg border bg-background px-4 py-2 text-sm hover:bg-accent transition-colors"
                  >
                    Sign in
                  </button>
                  <button
                    type="button"
                    onClick={() => navigate({ to: "/auth/login" })}
                    className="rounded-lg bg-primary px-4 py-2 text-sm text-primary-foreground hover:opacity-90 transition-opacity"
                  >
                    Sign up
                  </button>
                </>
              )}
            </div>
          )}
        </div>
      </div>
    </header>
  )
}

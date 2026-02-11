import { useEffect } from "react"
import { Link } from "@tanstack/react-router"
import { toast } from "sonner"
import { blockAllUserSessions, blockUserSession, refreshSession } from "@/use_cases/authService"
import { useSessions } from "@/delivery"

const sessionsLoadedRef = { current: false }

export function SessionsPage() {
  const { data, loading, error, load } = useSessions()

  useEffect(() => {
    if (error) return
    if (sessionsLoadedRef.current) return
    sessionsLoadedRef.current = true
    void load()
    return () => {
      setTimeout(() => {
        sessionsLoadedRef.current = false
      }, 0)
    }
  }, [load, error])

  const handleBlock = async (familyId: string) => {
    try {
      await blockUserSession(familyId)
      toast.success("Session ended")
      await load()
    } catch (error) {
      console.error("Block session error:", error)
    }
  }

  const handleBlockAll = async () => {
    if (!confirm("End all sessions? You will be signed out on all devices.")) return

    try {
      await blockAllUserSessions()
      toast.success("All sessions ended")
      await load()
    } catch (error) {
      console.error("Block all sessions error:", error)
    }
  }

  const handleRefresh = async () => {
    try {
      await refreshSession()
      toast.success("Token refreshed")
      await load()
    } catch (error) {
      console.error("Refresh session error:", error)
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20 p-4 md:p-8">
      <div className="max-w-4xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl md:text-4xl font-bold">My sessions</h1>
            <p className="text-muted-foreground mt-1">Manage active sessions</p>
          </div>
          <Link
            to="/"
            className="inline-flex items-center justify-center rounded-lg border bg-background px-4 py-2 text-sm hover:bg-accent transition-colors"
          >
            ← Back to home
          </Link>
        </div>

        <section className="rounded-2xl border bg-card text-card-foreground shadow-lg p-6 space-y-4">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <span>⚙️</span> Actions
          </h2>
          <div className="flex flex-wrap gap-3">
            <button
              className="inline-flex items-center justify-center rounded-lg border bg-background px-4 py-2 text-sm font-medium hover:bg-accent transition-colors disabled:opacity-50"
              onClick={handleRefresh}
              disabled={loading}
            >
              🔄 Refresh token
            </button>
            <button
              className="inline-flex items-center justify-center rounded-lg border border-destructive bg-destructive/10 px-4 py-2 text-sm font-medium text-destructive hover:bg-destructive/20 transition-colors disabled:opacity-50"
              onClick={handleBlockAll}
              disabled={loading}
            >
              🚫 End all sessions
            </button>
          </div>
        </section>

        <section className="rounded-2xl border bg-card text-card-foreground shadow-lg p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold flex items-center gap-2">
              <span>🔐</span> Active sessions
            </h2>
            {data && (
              <span className="text-sm text-muted-foreground">
                Total: <span className="font-semibold">{data.total}</span>
              </span>
            )}
          </div>

          {loading && !data && (
            <div className="flex items-center justify-center py-12">
              <div className="text-center space-y-4">
                <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto" />
                <p className="text-muted-foreground">Loading sessions...</p>
              </div>
            </div>
          )}

          {error && (
            <div className="rounded-xl border bg-destructive/10 border-destructive/20 p-4 text-center">
              <p className="text-sm text-destructive">{error}</p>
            </div>
          )}

          {data && data.sessions.length === 0 && (
            <div className="text-center py-12">
              <p className="text-muted-foreground">No active sessions</p>
            </div>
          )}

          {data && data.sessions.length > 0 && (
            <div className="space-y-3">
              {data.sessions.map((session) => (
                <article
                  key={session.id}
                  className={`rounded-xl border p-5 space-y-3 transition-colors ${
                    session.is_current
                      ? "bg-primary/5 border-primary/20"
                      : "bg-background/50"
                  }`}
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 space-y-2">
                      <div className="flex items-center gap-2">
                        <p className="font-medium text-sm">
                          {session.user_agent || "Unknown device"}
                        </p>
                        {session.is_current && (
                          <span className="text-xs bg-green-500/20 text-green-700 dark:text-green-300 px-2 py-0.5 rounded-full">
                            ✓ Current
                          </span>
                        )}
                      </div>
                      <div className="flex flex-wrap gap-3 text-xs text-muted-foreground">
                        <span className="flex items-center gap-1">
                          <span>📅</span>
                          Created:{" "}
                          {new Date(session.created_at).toLocaleString()}
                        </span>
                        {session.last_used_at && (
                          <>
                            <span>•</span>
                            <span className="flex items-center gap-1">
                              <span>🕐</span>
                              Last used:{" "}
                              {new Date(session.last_used_at).toLocaleString()}
                            </span>
                          </>
                        )}
                      </div>
                    </div>
                    <button
                      className="inline-flex items-center justify-center rounded-lg border border-input bg-background px-3 py-2 text-xs font-medium hover:bg-accent transition-colors disabled:opacity-50"
                      onClick={() => handleBlock(session.family_id)}
                      disabled={loading}
                    >
                      🚪 End
                    </button>
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>
      </div>
    </main>
  )
}

export default SessionsPage


import { FormEvent, useEffect, useState } from "react"
import { Link } from "@tanstack/react-router"
import { toast } from "sonner"
import { useAdminUserActions, useAdminUsers } from "@/delivery"

const adminUsersLoadedRef = { current: false }

export function AdminUsersPage() {
  const { data, loading, error, load } = useAdminUsers()
  const { createUser, deleteUser, changeBalance } = useAdminUserActions()

  const [email, setEmail] = useState("")
  const [fullName, setFullName] = useState("")
  const [password, setPassword] = useState("")
  const [balanceInputs, setBalanceInputs] = useState<Record<string, string>>({})

  useEffect(() => {
    if (adminUsersLoadedRef.current) return
    adminUsersLoadedRef.current = true
    void load()
    return () => {
      setTimeout(() => {
        adminUsersLoadedRef.current = false
      }, 0)
    }
  }, [load])

  const handleCreate = async (e: FormEvent) => {
    e.preventDefault()
    try {
      await createUser({ email, full_name: fullName, password })
      toast.success("User created successfully")
      setEmail("")
      setFullName("")
      setPassword("")
      await load()
    } catch (error) {
      console.error("Create user error:", error)
    }
  }

  const handleDelete = async (id: string, userEmail: string) => {
    if (!confirm(`Delete user ${userEmail}?`)) return

    try {
      await deleteUser(id)
      toast.success("User deleted")
      await load()
    } catch (error) {
      console.error("Delete user error:", error)
    }
  }

  const handleAddBalance = async (id: string) => {
    const raw = balanceInputs[id]?.trim() ?? ""
    const amount = raw === "" ? NaN : Number(raw)
    if (Number.isNaN(amount) || amount <= 0) {
      toast.error("Enter a positive number (greater than zero)")
      return
    }
    try {
      await changeBalance(id, Math.floor(amount))
      toast.success("Balance updated")
      setBalanceInputs((prev) => ({ ...prev, [id]: "" }))
      await load()
    } catch (error) {
      console.error("Add balance error:", error)
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20 p-4 md:p-8">
      <div className="max-w-6xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl md:text-4xl font-bold">User management</h1>
            <p className="text-muted-foreground mt-1">Create and manage users</p>
          </div>
          <div className="flex gap-2">
            <button
              className="inline-flex items-center justify-center rounded-lg border bg-background px-4 py-2 text-sm hover:bg-accent transition-colors disabled:opacity-50"
              onClick={() => load()}
              disabled={loading}
            >
              🔄 Refresh
            </button>
            <Link
              to="/"
              className="inline-flex items-center justify-center rounded-lg border bg-background px-4 py-2 text-sm hover:bg-accent transition-colors"
            >
              ← Back to home
            </Link>
          </div>
        </div>

        <div className="flex gap-2 border-b pb-4">
          <Link
            to="/admin"
            className="px-4 py-2 rounded-lg hover:bg-accent text-sm font-medium transition-colors"
          >
            Dashboard
          </Link>
          <Link
            to="/admin/users"
            className="px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm font-medium"
          >
            Users
          </Link>
          <Link
            to="/admin/yc-sync"
            className="px-4 py-2 rounded-lg hover:bg-accent text-sm font-medium transition-colors"
          >
            YC Sync
          </Link>
        </div>

        <section className="rounded-2xl border bg-card text-card-foreground shadow-lg p-6 space-y-4">
          <h2 className="text-xl font-semibold flex items-center gap-2">
            <span>➕</span> Create user
          </h2>
          <form className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end" onSubmit={handleCreate}>
            <div className="space-y-2">
              <label className="block text-sm font-medium" htmlFor="create-email">
                Email
              </label>
              <input
                id="create-email"
                type="email"
                className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="user@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                disabled={loading}
              />
            </div>
            <div className="space-y-2">
              <label className="block text-sm font-medium" htmlFor="create-name">
                Full name
              </label>
              <input
                id="create-name"
                type="text"
                className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="John Doe"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                required
                disabled={loading}
              />
            </div>
            <div className="space-y-2">
              <label className="block text-sm font-medium" htmlFor="create-password">
                Password
              </label>
              <input
                id="create-password"
                type="password"
                className="w-full rounded-lg border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={loading}
              />
            </div>
            <button
              type="submit"
              className="inline-flex items-center justify-center rounded-lg bg-primary px-4 py-2.5 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-md"
              disabled={loading}
            >
              {loading ? "Creating..." : "Create"}
            </button>
          </form>
        </section>

        <section className="rounded-2xl border bg-card text-card-foreground shadow-lg p-6 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold flex items-center gap-2">
              <span>👥</span> User list
            </h2>
            {data && (
              <span className="text-sm text-muted-foreground">
                Total: <span className="font-semibold">{data.count}</span>
              </span>
            )}
          </div>

          {loading && !data && (
            <div className="flex items-center justify-center py-12">
              <div className="text-center space-y-4">
                <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto" />
                <p className="text-muted-foreground">Loading users...</p>
              </div>
            </div>
          )}

          {error && (
            <div className="rounded-xl border bg-destructive/10 border-destructive/20 p-4 text-center">
              <p className="text-sm text-destructive">{error}</p>
            </div>
          )}

          {data && data.data.length === 0 && (
            <div className="text-center py-12">
              <p className="text-muted-foreground">No users found</p>
            </div>
          )}

          {data && data.data.length > 0 && (
            <div className="space-y-3">
              {data.data.map((user) => (
                <article
                  key={user.id}
                  className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 rounded-xl border bg-background/50 p-4 hover:bg-background transition-colors"
                >
                  <div className="flex-1 space-y-1">
                    <div className="flex items-center gap-2">
                      <p className="font-semibold text-sm">{user.email}</p>
                      {user.plan === "premium" && (
                        <span className="text-xs bg-yellow-500/20 text-yellow-700 dark:text-yellow-300 px-2 py-0.5 rounded-full">
                          Premium
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-muted-foreground">
                      {user.full_name || "No name"}
                    </p>
                    <div className="flex items-center gap-3 text-xs text-muted-foreground">
                      <span>Plan: {user.plan}</span>
                      <span>•</span>
                      <span>Balance: {user.balance_cents}¢</span>
                    </div>
                  </div>

                  <div className="flex flex-wrap items-center gap-2">
                    <input
                      type="number"
                      min={1}
                      inputMode="numeric"
                      className="w-32 rounded-lg border border-input bg-background px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                      placeholder="Amount"
                      value={balanceInputs[user.id] ?? ""}
                      onChange={(e) =>
                        setBalanceInputs({
                          ...balanceInputs,
                          [user.id]: e.target.value,
                        })
                      }
                    />
                    <button
                      className="inline-flex items-center justify-center rounded-lg border bg-background px-3 py-1.5 text-xs font-medium hover:bg-accent transition-colors disabled:opacity-50"
                      onClick={() => handleAddBalance(user.id)}
                      disabled={loading}
                    >
                      Add
                    </button>
                    <button
                      className="inline-flex items-center justify-center rounded-lg bg-destructive px-3 py-1.5 text-xs font-medium text-destructive-foreground hover:bg-destructive/90 transition-colors disabled:opacity-50"
                      onClick={() => handleDelete(user.id, user.email)}
                      disabled={loading}
                    >
                      🗑️ Delete
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

export default AdminUsersPage


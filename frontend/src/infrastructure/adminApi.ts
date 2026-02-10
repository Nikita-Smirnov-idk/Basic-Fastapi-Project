import type { User } from "@/domain/user/types/user"
import { httpRequest } from "@/pkg/httpClient"

interface PrivateUserCreate {
  email: string
  password: string
  full_name: string
  is_verified?: boolean
  plan?: string
  balance_cents?: number
}

interface BalanceUpdate {
  amount_cents: number
}

export interface AdminDashboardStats {
  total_users: number
  paying_users: number
  total_balance_cents: number
  yc_companies_count: number
  yc_founders_count: number
}

export interface UsersPublic {
  data: User[]
  count: number
}

export interface Message {
  message: string
}

export async function createUser(body: PrivateUserCreate): Promise<User> {
  return httpRequest<User>({
    path: "/admin/",
    method: "POST",
    body,
  })
}

export async function readUsers(skip = 0, limit = 100): Promise<UsersPublic> {
  return httpRequest<UsersPublic>({
    path: "/admin/",
    method: "GET",
    query: { skip, limit },
  })
}

export async function readUserById(userId: string): Promise<User> {
  return httpRequest<User>({
    path: `/admin/${userId}`,
    method: "GET",
  })
}

export async function deleteUser(userId: string): Promise<Message> {
  return httpRequest<Message>({
    path: `/admin/${userId}`,
    method: "DELETE",
  })
}

export async function updateUserBalance(
  userId: string,
  amountCents: number,
): Promise<User> {
  return httpRequest<User>({
    path: `/admin/${userId}/balance`,
    method: "POST",
    body: { amount_cents: amountCents } satisfies BalanceUpdate,
  })
}

export async function getAdminDashboard(): Promise<AdminDashboardStats> {
  return httpRequest<AdminDashboardStats>({
    path: "/admin/dashboard",
    method: "GET",
  })
}


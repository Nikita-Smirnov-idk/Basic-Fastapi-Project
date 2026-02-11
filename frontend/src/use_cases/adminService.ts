import type { User } from "@/domain/user/types/user"
import {
  createUser as createAdminUserApi,
  deleteUser as deleteAdminUserApi,
  getAdminDashboard,
  readUserById,
  readUsers,
  updateUserBalance as updateUserBalanceApi,
  type AdminDashboardStats,
  type Message,
  type UsersPublic,
} from "@/infrastructure/adminApi"

interface CreateUserInput {
  email: string
  password: string
  full_name: string
  is_verified?: boolean
  plan?: string
  balance_cents?: number
}

export async function createAdminUser(body: CreateUserInput): Promise<User> {
  return createAdminUserApi(body)
}

export async function listAdminUsers(
  skip?: number,
  limit?: number,
): Promise<UsersPublic> {
  return readUsers(skip, limit)
}

export async function getAdminUserById(userId: string): Promise<User> {
  return readUserById(userId)
}

export async function deleteAdminUser(userId: string): Promise<Message> {
  return deleteAdminUserApi(userId)
}

export async function updateUserBalance(
  userId: string,
  amountCents: number,
): Promise<User> {
  return updateUserBalanceApi(userId, amountCents)
}

export async function getDashboardStats(): Promise<AdminDashboardStats> {
  return getAdminDashboard()
}


import { useCallback, useState } from "react"

import type { User } from "@/domain/user/types/user"
import {
  createAdminUser,
  deleteAdminUser,
  getAdminUserById,
  getDashboardStats,
  listAdminUsers,
  updateUserBalance,
} from "@/use_cases/adminService"
import type { AdminDashboardStats, Message, UsersPublic } from "@/infrastructure/adminApi"

export function useAdminUsers() {
  const [data, setData] = useState<UsersPublic | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async (skip?: number, limit?: number) => {
    setLoading(true)
    setError(null)
    try {
      const res = await listAdminUsers(skip, limit)
      setData(res)
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setLoading(false)
    }
  }, [])

  return { data, loading, error, load }
}

export function useAdminUserActions() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const createUser = async (input: {
    email: string
    password: string
    full_name: string
    is_verified?: boolean
    plan?: string
    balance_cents?: number
  }): Promise<User> => {
    setLoading(true)
    setError(null)
    try {
      return await createAdminUser(input)
    } catch (e) {
      setError((e as Error).message)
      throw e
    } finally {
      setLoading(false)
    }
  }

  const deleteUser = async (userId: string): Promise<Message> => {
    setLoading(true)
    setError(null)
    try {
      return await deleteAdminUser(userId)
    } catch (e) {
      setError((e as Error).message)
      throw e
    } finally {
      setLoading(false)
    }
  }

  const changeBalance = async (userId: string, amountCents: number): Promise<User> => {
    setLoading(true)
    setError(null)
    try {
      return await updateUserBalance(userId, amountCents)
    } catch (e) {
      setError((e as Error).message)
      throw e
    } finally {
      setLoading(false)
    }
  }

  const getUser = async (userId: string): Promise<User> => {
    setLoading(true)
    setError(null)
    try {
      return await getAdminUserById(userId)
    } catch (e) {
      setError((e as Error).message)
      throw e
    } finally {
      setLoading(false)
    }
  }

  return { loading, error, createUser, deleteUser, changeBalance, getUser }
}

export function useAdminDashboard() {
  const [data, setData] = useState<AdminDashboardStats | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const stats = await getDashboardStats()
      setData(stats)
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setLoading(false)
    }
  }, [])

  return { data, loading, error, load }
}


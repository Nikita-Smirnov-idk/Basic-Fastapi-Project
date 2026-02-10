import type { AuthMessage, SessionsList } from "@/domain/auth/types/auth"
import { httpRequest } from "@/pkg/httpClient"

export async function login(email: string, password: string): Promise<AuthMessage> {
  const base =
    import.meta.env.VITE_API_URL ??
    (typeof window !== "undefined" ? window.location.origin : "http://localhost:8000")

  const url = new URL("/api/v1/users/auth/login", base)
  const formData = new URLSearchParams()
  formData.set("username", email)
  formData.set("password", password)

  const response = await fetch(url.toString(), {
    method: "POST",
    body: formData,
    headers: {
      "Content-Type": "application/x-www-form-urlencoded",
    },
    credentials: "include",
  })

  if (!response.ok) {
    throw new Error(`HTTP error ${response.status}`)
  }

  return (await response.json()) as AuthMessage
}

export async function logout(): Promise<AuthMessage> {
  return httpRequest<AuthMessage>({
    path: "/users/auth/logout",
    method: "POST",
  })
}

export async function getMySessions(): Promise<SessionsList> {
  return httpRequest<SessionsList>({
    path: "/users/auth/my-sessions",
    method: "GET",
  })
}

export async function startSignup(email: string, fullName: string): Promise<AuthMessage> {
  return httpRequest<AuthMessage>({
    path: "/users/auth/start-signup",
    method: "POST",
    body: { email, full_name: fullName },
  })
}

export async function completeSignup(token: string, password: string) {
  return httpRequest<unknown>({
    path: "/users/auth/complete-signup",
    method: "POST",
    body: { token, password },
  })
}

export async function refreshToken(): Promise<AuthMessage> {
  return httpRequest<AuthMessage>({
    path: "/users/auth/refresh",
    method: "POST",
  })
}

export async function blockSession(familyId: string): Promise<AuthMessage> {
  return httpRequest<AuthMessage>({
    path: "/users/auth/block",
    method: "POST",
    body: { family_id: familyId },
  })
}

export async function blockAllSessions(): Promise<AuthMessage> {
  return httpRequest<AuthMessage>({
    path: "/users/auth/block/all",
    method: "POST",
  })
}

export function getGoogleLoginUrl(): string {
  const base =
    import.meta.env.VITE_API_URL ??
    (typeof window !== "undefined" ? window.location.origin : "http://localhost:8000")
  const url = new URL("/api/v1/users/google-oauth/login", base)
  return url.toString()
}
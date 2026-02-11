import type { AuthMessage, SessionsList } from "@/domain/auth/types/auth"
import {
  blockAllSessions,
  blockSession,
  completeSignup,
  getGoogleLoginUrl,
  getMySessions,
  login,
  logout,
  refreshToken,
  startSignup,
} from "@/infrastructure/authApi"

export async function loginUser(email: string, password: string): Promise<AuthMessage> {
  return login(email, password)
}

export async function logoutUser(): Promise<AuthMessage> {
  return logout()
}

export async function getSessions(): Promise<SessionsList> {
  return getMySessions()
}

export async function startSignupFlow(
  email: string,
  fullName: string,
): Promise<AuthMessage> {
  return startSignup(email, fullName)
}

export async function completeSignupFlow(token: string, password: string) {
  return completeSignup(token, password)
}

export async function refreshSession(): Promise<AuthMessage> {
  return refreshToken()
}

export async function blockUserSession(familyId: string): Promise<AuthMessage> {
  return blockSession(familyId)
}

export async function blockAllUserSessions(): Promise<AuthMessage> {
  return blockAllSessions()
}

export function buildGoogleLoginUrl(): string {
  return getGoogleLoginUrl()
}
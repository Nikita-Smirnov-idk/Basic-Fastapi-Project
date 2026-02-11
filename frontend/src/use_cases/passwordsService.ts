import type { AuthMessage } from "@/domain/auth/types/auth"
import { recoverPassword, resetPassword } from "@/infrastructure/passwordsApi"

export async function requestPasswordRecovery(email: string): Promise<AuthMessage> {
  return recoverPassword(email)
}

export async function submitPasswordReset(
  token: string,
  newPassword: string,
): Promise<AuthMessage> {
  return resetPassword(token, newPassword)
}


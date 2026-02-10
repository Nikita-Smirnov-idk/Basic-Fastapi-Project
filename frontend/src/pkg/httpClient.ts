import { toast } from "sonner"

export type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE"

export interface HttpRequestOptions<TBody = unknown> {
  path: string
  method?: HttpMethod
  body?: TBody
  query?: Record<string, string | number | boolean | undefined>
  headers?: Record<string, string>
  skipErrorToast?: boolean
  skipTokenRefresh?: boolean
}

export class HttpError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    public data?: unknown,
  ) {
    super(`HTTP ${status}: ${statusText}`)
    this.name = "HttpError"
  }
}

const API_PREFIX = "/api/v1"
let isRefreshing = false
let refreshPromise: Promise<void> | null = null
let refreshFailed = false

function buildUrl(path: string, query?: HttpRequestOptions["query"]): string {
  const base =
    import.meta.env.VITE_API_URL ??
    (typeof window !== "undefined" ? window.location.origin : "http://localhost:8000")

  const url = new URL(API_PREFIX + path, base)

  if (query) {
    Object.entries(query).forEach(([key, value]) => {
      if (value === undefined) return
      url.searchParams.set(key, String(value))
    })
  }

  return url.toString()
}

async function refreshToken(): Promise<void> {
  const response = await fetch(buildUrl("/users/auth/refresh"), {
    method: "POST",
    credentials: "include",
  })

  if (!response.ok) {
    throw new HttpError(response.status, response.statusText)
  }
}

async function performRequest<TResponse>(
  url: string,
  init: RequestInit,
  skipErrorToast: boolean,
): Promise<TResponse> {
  const response = await fetch(url, init)

  if (!response.ok) {
    let errorData: unknown
    try {
      errorData = await response.json()
    } catch {
      errorData = await response.text()
    }

    const error = new HttpError(response.status, response.statusText, errorData)

    if (!skipErrorToast) {
      const errorMessage = getErrorMessage(error)
      toast.error(errorMessage)
    }

    throw error
  }

  const contentType = response.headers.get("content-type")
  if (contentType?.includes("application/json")) {
    return (await response.json()) as TResponse
  }

  return (await response.text()) as TResponse
}

/** Format FastAPI-style validation errors (detail is array of { loc, msg }) */
function formatValidationDetail(detail: unknown): string {
  if (Array.isArray(detail)) {
    const parts = detail.map((item: unknown) => {
      if (typeof item === "object" && item !== null && "loc" in item && "msg" in item) {
        const loc = (item as { loc?: unknown[] }).loc
        const msg = String((item as { msg?: unknown }).msg)
        const field = Array.isArray(loc) ? loc.filter((x) => x !== "body" && x !== "query").join(".") : ""
        return field ? `${field}: ${msg}` : msg
      }
      return String(item)
    })
    return parts.length > 0 ? parts.join("; ") : "Ошибка валидации данных"
  }
  if (typeof detail === "string") return detail
  return "Ошибка валидации данных"
}

function getErrorMessage(error: HttpError): string {
  const { status, data } = error

  if (typeof data === "object" && data !== null && "detail" in data) {
    const detail = (data as { detail?: unknown }).detail
    if (status === 422) return formatValidationDetail(detail)
    return String(detail)
  }

  if (typeof data === "string") {
    return data
  }

  switch (status) {
    case 400:
      return "Неверный запрос"
    case 401:
      return "Требуется авторизация"
    case 403:
      return "Доступ запрещен"
    case 404:
      return "Не найдено"
    case 409:
      return "Конфликт данных"
    case 422:
      return "Ошибка валидации данных"
    case 500:
      return "Внутренняя ошибка сервера"
    case 502:
      return "Сервер недоступен"
    case 503:
      return "Сервис временно недоступен"
    default:
      return `Ошибка ${status}`
  }
}

export async function httpRequest<TResponse, TBody = unknown>(
  options: HttpRequestOptions<TBody>,
): Promise<TResponse> {
  const {
    path,
    method = "GET",
    body,
    query,
    headers = {},
    skipErrorToast = false,
    skipTokenRefresh = false,
  } = options

  const url = buildUrl(path, query)
  const init: RequestInit = {
    method,
    headers: {
      "Content-Type": "application/json",
      ...headers,
    },
    body: body ? JSON.stringify(body) : undefined,
    credentials: "include",
  }

  try {
    const result = await performRequest<TResponse>(url, init, skipErrorToast)
    refreshFailed = false
    return result
  } catch (error) {
    const shouldTryRefresh =
      !skipTokenRefresh &&
      !refreshFailed &&
      error instanceof HttpError &&
      (error.status === 401 || error.status === 403)

    if (!shouldTryRefresh) {
      if (
        error instanceof HttpError &&
        (error.status === 401 || error.status === 403) &&
        !skipErrorToast
      ) {
        toast.error(getErrorMessage(error))
      }
      throw error
    }

    if (isRefreshing) {
      await refreshPromise
    } else {
      isRefreshing = true
      refreshPromise = refreshToken()
        .then(() => {
          refreshFailed = false
        })
        .catch((refreshErr) => {
          refreshFailed = true
          if (!skipErrorToast) {
            toast.error(
              refreshErr instanceof HttpError
                ? getErrorMessage(refreshErr)
                : "Не удалось обновить сессию",
            )
          }
          if (
            typeof window !== "undefined" &&
            !window.location.pathname.startsWith("/auth")
          ) {
            window.location.href = "/auth/login"
          }
          throw refreshErr
        })
        .finally(() => {
          isRefreshing = false
          refreshPromise = null
        })

        await refreshPromise
    }

    try {
      return await httpRequest<TResponse, TBody>(
        { ...options, skipTokenRefresh: true },
      )
    } catch (retryError) {
      if (!skipErrorToast) {
        const msg =
          retryError instanceof HttpError
            ? getErrorMessage(retryError)
            : String(retryError)
        toast.error(msg)
      }
      throw retryError
    }
  }
}



export type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE"

export interface HttpRequestOptions<TBody = unknown> {
  path: string
  method?: HttpMethod
  body?: TBody
  query?: Record<string, string | number | boolean | undefined>
  headers?: Record<string, string>
}

export async function httpRequest<TResponse, TBody = unknown>(
  options: HttpRequestOptions<TBody>,
): Promise<TResponse> {
  const { path, method = "GET", body, query, headers = {} } = options

  const url = new URL(path, import.meta.env.VITE_API_URL)

  if (query) {
    Object.entries(query).forEach(([key, value]) => {
      if (value === undefined) return
      url.searchParams.set(key, String(value))
    })
  }

  const response = await fetch(url.toString(), {
    method,
    headers: {
      "Content-Type": "application/json",
      ...headers,
    },
    body: body ? JSON.stringify(body) : undefined,
  })

  if (!response.ok) {
    // Здесь можно навесить общую обработку ошибок, логирование и т.п.
    throw new Error(`HTTP error ${response.status}`)
  }

  // Для главной страницы сейчас ожидаем JSON, при необходимости можно
  // расширить опциями (blob/text и т.д.)
  return (await response.json()) as TResponse
}


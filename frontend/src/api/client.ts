import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

// JWT interceptor
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// SSE client for streaming interview responses
export function createSSEConnection(url: string, body: object): EventSource | null {
  // We use fetch + ReadableStream for POST SSE since EventSource only supports GET
  return null // See streamChat below
}

export async function* streamChat(sessionId: string, message: string): AsyncGenerator<{ event: string; data: any }> {
  const token = localStorage.getItem('token')
  const response = await fetch(`/api/interviews/${sessionId}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify({ message }),
  })

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`)
  }

  const reader = response.body?.getReader()
  if (!reader) return

  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() || ''

    let currentEvent = 'message'
    for (const line of lines) {
      if (line.startsWith('event:')) {
        currentEvent = line.slice(6).trim()
      } else if (line.startsWith('data:')) {
        const data = line.slice(5).trim()
        try {
          yield { event: currentEvent, data: JSON.parse(data) }
        } catch {
          yield { event: currentEvent, data }
        }
      }
    }
  }
}

export default api

const TOKEN_KEY = 'drink_token'
const USER_KEY = 'drink_user'

export const auth = {
  get token() { return localStorage.getItem(TOKEN_KEY) },
  get user() {
    try { return JSON.parse(localStorage.getItem(USER_KEY)) } catch { return null }
  },
  save({ access_token, user }) {
    localStorage.setItem(TOKEN_KEY, access_token)
    localStorage.setItem(USER_KEY, JSON.stringify(user))
  },
  clear() {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  },
}

export async function api(path, { method = 'GET', body } = {}) {
  const headers = { 'Content-Type': 'application/json' }
  if (auth.token) headers.Authorization = `Bearer ${auth.token}`
  const res = await fetch(`/api${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  })
  const data = await res.json().catch(() => ({}))
  if (!res.ok) {
    if (res.status === 401) auth.clear()
    const msg = Array.isArray(data.detail)
      ? data.detail.map((d) => d.msg).join(', ')
      : data.detail || `錯誤 (${res.status})`
    throw new Error(msg)
  }
  return data
}

export const fmtMoney = (n) => `NT$ ${Number(n).toLocaleString()}`
export const fmtDateTime = (s) => (s ? s.replace('T', ' ').slice(0, 16) : '—')

import { createContext, useContext, useState } from 'react'
import { api, auth } from './api'

const Ctx = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(auth.user)

  const login = async (username, password) => {
    const data = await api('/auth/login', { method: 'POST', body: { username, password } })
    auth.save(data)
    setUser(data.user)
    return data.user
  }
  const register = async (form) => {
    const data = await api('/auth/register', { method: 'POST', body: form })
    auth.save(data)
    setUser(data.user)
    return data.user
  }
  const logout = () => {
    auth.clear()
    setUser(null)
  }
  return <Ctx.Provider value={{ user, login, register, logout }}>{children}</Ctx.Provider>
}

export const useAuth = () => useContext(Ctx)

export const homeFor = (role) =>
  ({ customer: '/menu', staff: '/staff', manager: '/manager' }[role] || '/')

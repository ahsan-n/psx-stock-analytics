import React, { createContext, useContext, useState, useEffect } from 'react'
import { api } from '../services/api'

interface User {
  id: number
  email: string
  full_name: string | null
}

interface AuthContextType {
  user: User | null
  token: string | null
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, fullName?: string) => Promise<void>
  logout: () => void
  isLoading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'))
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    if (token) {
      loadUser()
    } else {
      setIsLoading(false)
    }
  }, [token])

  const loadUser = async () => {
    try {
      const userData = await api.getCurrentUser()
      setUser(userData)
    } catch (error) {
      console.error('Failed to load user:', error)
      logout()
    } finally {
      setIsLoading(false)
    }
  }

  const login = async (email: string, password: string) => {
    const response = await api.login(email, password)
    const { access_token } = response
    localStorage.setItem('token', access_token)
    setToken(access_token)
  }

  const register = async (email: string, password: string, fullName?: string) => {
    await api.register(email, password, fullName)
    await login(email, password)
  }

  const logout = () => {
    localStorage.removeItem('token')
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

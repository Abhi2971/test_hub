import { createContext, useContext, useState, useEffect } from 'react'
import api from '../services/api'
import { clearAuthTokens } from '../services/api'

const AuthContext = createContext(null)

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

const TOKEN_KEYS = {
  access: 'auth_access_token',
  refresh: 'auth_refresh_token',
  user: 'auth_user',
}

function decodeJWT(token) {
  try {
    const parts = token.split('.')
    if (parts.length !== 3) return null
    const payload = JSON.parse(atob(parts[1]))
    return payload
  } catch {
    return null
  }
}

function isTokenExpired(token) {
  const payload = decodeJWT(token)
  if (!payload || !payload.exp) return true
  return Date.now() >= payload.exp * 1000
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [accessToken, setAccessToken] = useState(null)
  const [refreshToken, setRefreshToken] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  const refreshTokens = async () => {
    try {
      const storedRefresh = localStorage.getItem(TOKEN_KEYS.refresh)
      if (!storedRefresh) throw new Error('No refresh token')

      const response = await api.post(
        '/auth/refresh',
        {},
        { headers: { Authorization: `Bearer ${storedRefresh}` } }
      )
      const { access_token, refresh_token } = response.data.data
      localStorage.setItem(TOKEN_KEYS.access, access_token)
      localStorage.setItem(TOKEN_KEYS.refresh, refresh_token)
      setAccessToken(access_token)
      setRefreshToken(refresh_token)
      return { access_token, refresh_token }
    } catch (error) {
      clearAuthTokens()
      setUser(null)
      setAccessToken(null)
      setRefreshToken(null)
      setIsAuthenticated(false)
      throw error
    }
  }

  useEffect(() => {
    const initAuth = async () => {
      const storedAccess = localStorage.getItem(TOKEN_KEYS.access)
      const storedRefresh = localStorage.getItem(TOKEN_KEYS.refresh)
      const storedUser = localStorage.getItem(TOKEN_KEYS.user)

      if (storedAccess && !isTokenExpired(storedAccess)) {
        setAccessToken(storedAccess)
        setRefreshToken(storedRefresh)
        setUser(storedUser ? JSON.parse(storedUser) : null)
        setIsAuthenticated(true)
        setIsLoading(false)
      } else if (storedRefresh) {
        try {
          const tokens = await refreshTokens()
          const userData = storedUser ? JSON.parse(storedUser) : null
          setUser(userData)
          setIsAuthenticated(true)
        } catch {
          setIsAuthenticated(false)
        } finally {
          setIsLoading(false)
        }
      } else {
        setIsLoading(false)
      }
    }

    initAuth()
  }, [])

  const login = async (email, password) => {
    const response = await api.post('/auth/login', { email, password })
    const { access_token, refresh_token, user: userData } = response.data.data
    localStorage.setItem(TOKEN_KEYS.access, access_token)
    localStorage.setItem(TOKEN_KEYS.refresh, refresh_token)
    localStorage.setItem(TOKEN_KEYS.user, JSON.stringify(userData))
    setAccessToken(access_token)
    setRefreshToken(refresh_token)
    setUser(userData)
    setIsAuthenticated(true)
    return response.data
  }

  const loginWithGoogle = async (idToken) => {
    const response = await api.post('/auth/google', { id_token: idToken })
    const { access_token, refresh_token, user: userData } = response.data.data
    localStorage.setItem(TOKEN_KEYS.access, access_token)
    localStorage.setItem(TOKEN_KEYS.refresh, refresh_token)
    localStorage.setItem(TOKEN_KEYS.user, JSON.stringify(userData))
    setAccessToken(access_token)
    setRefreshToken(refresh_token)
    setUser(userData)
    setIsAuthenticated(true)
    return response.data
  }

  const logout = async () => {
    try {
      await api.post('/auth/logout')
    } catch {
    } finally {
      localStorage.removeItem(TOKEN_KEYS.access)
      localStorage.removeItem(TOKEN_KEYS.refresh)
      localStorage.removeItem(TOKEN_KEYS.user)
      setAccessToken(null)
      setRefreshToken(null)
      setUser(null)
      setIsAuthenticated(false)
    }
  }

  const updateUser = (userData) => {
    setUser(userData)
    localStorage.setItem(TOKEN_KEYS.user, JSON.stringify(userData))
  }

  const value = {
    user,
    accessToken,
    refreshToken,
    isAuthenticated,
    isLoading,
    login,
    loginWithGoogle,
    logout,
    refreshTokens,
    updateUser,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export default AuthContext

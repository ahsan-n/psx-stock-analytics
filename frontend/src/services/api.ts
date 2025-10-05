import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const axiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token to requests
axiosInstance.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle unauthorized responses
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const api = {
  // Auth
  login: async (email: string, password: string) => {
    const response = await axiosInstance.post('/api/v1/auth/login', { email, password })
    return response.data
  },

  register: async (email: string, password: string, full_name?: string) => {
    const response = await axiosInstance.post('/api/v1/auth/register', { 
      email, 
      password, 
      full_name 
    })
    return response.data
  },

  getCurrentUser: async () => {
    const response = await axiosInstance.get('/api/v1/auth/me')
    return response.data
  },

  // Companies
  getCompanies: async () => {
    const response = await axiosInstance.get('/api/v1/financial/companies')
    return response.data
  },

  getCompany: async (symbol: string) => {
    const response = await axiosInstance.get(`/api/v1/financial/companies/${symbol}`)
    return response.data
  },

  // Financial Statements
  getFinancialStatements: async (
    symbol: string,
    params?: {
      statement_type?: 'income_statement' | 'balance_sheet' | 'cash_flow'
      period_type?: 'quarterly' | 'annual'
      fiscal_year?: number
    }
  ) => {
    const response = await axiosInstance.get(`/api/v1/financial/statements/${symbol}`, { params })
    return response.data
  },

  // Financial Ratios
  getFinancialRatios: async (
    symbol: string,
    params?: {
      period_type?: 'quarterly' | 'annual'
      fiscal_year?: number
    }
  ) => {
    const response = await axiosInstance.get(`/api/v1/financial/ratios/${symbol}`, { params })
    return response.data
  },
}

export default axiosInstance

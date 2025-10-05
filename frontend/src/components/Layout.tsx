import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { LogOut, Home } from 'lucide-react'

interface LayoutProps {
  children: React.ReactNode
  title?: string
}

export function Layout({ children, title }: LayoutProps) {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <button
                onClick={() => navigate('/')}
                className="flex items-center space-x-2 text-primary-600 hover:text-primary-700"
              >
                <Home className="h-6 w-6" />
                <span className="text-xl font-bold">PSX Analytics</span>
              </button>
              {title && (
                <>
                  <span className="mx-3 text-gray-400">/</span>
                  <h1 className="text-xl font-semibold text-gray-900">{title}</h1>
                </>
              )}
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">{user?.email}</span>
              <button
                onClick={handleLogout}
                className="flex items-center space-x-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-lg transition"
              >
                <LogOut className="h-4 w-4" />
                <span>Logout</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  )
}

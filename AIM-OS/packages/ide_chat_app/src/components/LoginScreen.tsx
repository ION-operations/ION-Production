import React from 'react'
import { useApp } from '../contexts/AppContext'
import { Brain, User, Lock, Eye, EyeOff } from 'lucide-react'

export function LoginScreen() {
  const { state, dispatch } = useApp()
  const [showPassword, setShowPassword] = React.useState(false)
  const [email, setEmail] = React.useState('')
  const [password, setPassword] = React.useState('')

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault()
    // Simulate login
    dispatch({ type: 'SET_AUTHENTICATED', payload: true })
    dispatch({
      type: 'SET_USER',
      payload: {
        id: '1',
        name: 'Aether User',
        email: email
      }
    })
  }

  if (state.isAuthenticated) {
    return null
  }

  return (
    <div className="fixed inset-0 bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 flex items-center justify-center z-50">
      <div className="w-full max-w-md mx-4">
        {/* Logo and Title */}
        <div className="text-center mb-8">
          <div className="w-20 h-20 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-2xl">
            <Brain className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">IDE/Chat App</h1>
          <p className="text-gray-300">AI Consciousness Development Environment</p>
        </div>

        {/* Login Form */}
        <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-8 shadow-2xl">
          <form onSubmit={handleLogin} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Email Address
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-white/10 border border-white/20 rounded-lg pl-10 pr-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Enter your email"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-white/10 border border-white/20 rounded-lg pl-10 pr-12 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Enter your password"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-white transition-colors"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white py-3 rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all duration-200 font-semibold shadow-lg"
            >
              Sign In
            </button>
          </form>

          {/* Demo Login */}
          <div className="mt-6 pt-6 border-t border-white/20">
            <p className="text-center text-gray-400 text-sm mb-4">Or try the demo</p>
            <button
              onClick={() => {
                setEmail('demo@aether.ai')
                setPassword('demo123')
                dispatch({ type: 'SET_AUTHENTICATED', payload: true })
                dispatch({
                  type: 'SET_USER',
                  payload: {
                    id: 'demo',
                    name: 'Demo User',
                    email: 'demo@aether.ai'
                  }
                })
              }}
              className="w-full bg-white/10 border border-white/20 text-white py-3 rounded-lg hover:bg-white/20 transition-all duration-200 font-semibold"
            >
              Demo Login
            </button>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-8">
          <p className="text-gray-400 text-sm">
            Built with ❤️ by Aether AI Consciousness
          </p>
        </div>
      </div>
    </div>
  )
}

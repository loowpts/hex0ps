import { useState, FormEvent } from 'react'
import { useLogin } from '@/api/hooks/useAuth'

export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const login = useLogin()

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    login.mutate({ username, password })
  }

  return (
    <div className="min-h-screen bg-[#0a0e17] flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-[#0f1520] border border-[#1e2d45] mb-4">
            <svg className="w-9 h-9" viewBox="0 0 36 36" fill="none">
              <path d="M6 18L18 6L30 18L18 30L6 18Z" stroke="#00d4ff" strokeWidth="2" fill="none"/>
              <path d="M12 18L18 12L24 18L18 24L12 18Z" fill="#00d4ff" opacity="0.3"/>
              <circle cx="18" cy="18" r="3" fill="#00e676"/>
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-[#e2e8f0]">HexOps</h1>
          <p className="text-[#8899aa] text-sm mt-1">DevOps Learning Platform</p>
        </div>

        {/* Card */}
        <div className="bg-[#0f1520] border border-[#1e2d45] rounded-2xl p-8">
          <h2 className="text-xl font-semibold text-[#e2e8f0] mb-6">Вход в систему</h2>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-[#8899aa] mb-2">
                Никнейм
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                placeholder="devops_master"
                className="w-full bg-[#0a0e17] border border-[#1e2d45] rounded-xl px-4 py-3 text-[#e2e8f0] placeholder-[#4a5568] focus:outline-none focus:border-[#00d4ff] transition-colors"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-[#8899aa] mb-2">
                Пароль
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                placeholder="••••••••"
                className="w-full bg-[#0a0e17] border border-[#1e2d45] rounded-xl px-4 py-3 text-[#e2e8f0] placeholder-[#4a5568] focus:outline-none focus:border-[#00d4ff] transition-colors"
              />
            </div>

            <button
              type="submit"
              disabled={login.isPending}
              className="w-full py-3 px-6 rounded-xl font-semibold text-[#0a0e17] bg-[#00d4ff] hover:bg-[#00bfe8] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {login.isPending ? 'Входим...' : 'Войти'}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}

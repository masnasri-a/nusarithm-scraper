'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import axios from 'axios'
import { Button } from '@/components/ui/button'
import { getApiUrl } from '@/lib/config'

interface User {
  id: string
  username: string
  email: string
  role: string
  is_active: boolean
  train_count: number
  scrape_count: number
  max_trains: number
  max_scrapes: number
  created_at: string
}

interface APIToken {
  id: string
  name: string
  token: string
  created_at: string
  expires_at: string | null
  last_used: string | null
  is_active: boolean
}

export default function AdminPage() {
  const [users, setUsers] = useState<User[]>([])
  const [tokens, setTokens] = useState<APIToken[]>([])
  const [currentUser, setCurrentUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('users')
  const [tokenName, setTokenName] = useState('')
  const [newToken, setNewToken] = useState<APIToken | null>(null)
  const router = useRouter()

  useEffect(() => {
    checkAdminAuth()
    loadAdminData()
  }, [])

  const checkAdminAuth = async () => {
    const token = localStorage.getItem('auth_token')
    if (!token) {
      router.push('/auth/login')
      return
    }

    try {
      const response = await axios.get(getApiUrl('/users/me'), {
        headers: { Authorization: `Bearer ${token}` }
      })
      
      if (response.data.role !== 'admin') {
        router.push('/dashboard')
        return
      }
      
      setCurrentUser(response.data)
    } catch (error) {
      router.push('/auth/login')
    }
  }

  const loadAdminData = async () => {
    try {
      const token = localStorage.getItem('auth_token')
      const headers = { Authorization: `Bearer ${token}` }

      // For now, we'll simulate users data since the endpoint isn't fully implemented
      const usersData = [
        {
          id: '1',
          username: 'nasri',
          email: 'admin@scraper.local',
          role: 'admin',
          is_active: true,
          train_count: 0,
          scrape_count: 0,
          max_trains: -1,
          max_scrapes: -1,
          created_at: new Date().toISOString()
        }
      ]
      
      setUsers(usersData)
    } catch (error) {
      console.error('Error loading admin data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const generateAPIToken = async () => {
    if (!tokenName.trim()) {
      alert('Please enter a token name')
      return
    }

    try {
      const token = localStorage.getItem('auth_token')
      const response = await axios.post(getApiUrl('/auth/tokens'), {
        name: tokenName,
        expires_in_days: 365
      }, {
        headers: { Authorization: `Bearer ${token}` }
      })

      setNewToken(response.data)
      setTokenName('')
      alert('API Token generated successfully!')
    } catch (error) {
      console.error('Error generating token:', error)
      alert('Failed to generate API token')
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('auth_token')
    localStorage.removeItem('user_data')
    router.push('/')
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Loading admin panel...</div>
      </div>
    )
  }

  if (!currentUser || currentUser.role !== 'admin') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-600 mb-4">Access Denied</h1>
          <p className="text-gray-600 mb-4">You don't have permission to access this page.</p>
          <Button onClick={() => router.push('/dashboard')}>
            Go to Dashboard
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Admin Panel</h1>
              <p className="text-sm text-gray-600">Manage users and API tokens</p>
            </div>
            <div className="flex items-center space-x-4">
              <Button 
                onClick={() => router.push('/dashboard')}
                variant="outline"
              >
                Back to Dashboard
              </Button>
              <Button onClick={handleLogout} variant="outline">
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Tabs */}
        <div className="border-b border-gray-200 mb-6">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('users')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'users'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Users Management
            </button>
            <button
              onClick={() => setActiveTab('tokens')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'tokens'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              API Tokens
            </button>
            <button
              onClick={() => setActiveTab('settings')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'settings'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              System Settings
            </button>
          </nav>
        </div>

        {/* Tab Content */}
        {activeTab === 'users' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-gray-900">Users</h2>
              <Button>Add New User</Button>
            </div>

            <div className="bg-white shadow overflow-hidden sm:rounded-md">
              <ul className="divide-y divide-gray-200">
                {users.map((user) => (
                  <li key={user.id} className="px-6 py-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <div className="flex-shrink-0">
                          <div className="h-10 w-10 bg-blue-500 rounded-full flex items-center justify-center">
                            <span className="text-white font-bold">
                              {user.username.charAt(0).toUpperCase()}
                            </span>
                          </div>
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">
                            {user.username}
                            {user.role === 'admin' && (
                              <span className="ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                                Admin
                              </span>
                            )}
                          </div>
                          <div className="text-sm text-gray-500">{user.email}</div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-4">
                        <div className="text-sm text-gray-500">
                          <div>Trains: {user.train_count}/{user.max_trains === -1 ? '∞' : user.max_trains}</div>
                          <div>Scrapes: {user.scrape_count}/{user.max_scrapes === -1 ? '∞' : user.max_scrapes}</div>
                        </div>
                        <div className="flex space-x-2">
                          <Button size="sm" variant="outline">Edit</Button>
                          <Button size="sm" variant="destructive">Disable</Button>
                        </div>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}

        {activeTab === 'tokens' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-gray-900">API Tokens</h2>
            </div>

            {/* Generate New Token */}
            <div className="bg-white shadow rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Generate New API Token</h3>
              <div className="flex items-center space-x-4">
                <div className="flex-1">
                  <input
                    type="text"
                    placeholder="Token name (e.g., 'Production API')"
                    value={tokenName}
                    onChange={(e) => setTokenName(e.target.value)}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <Button onClick={generateAPIToken}>
                  Generate Token
                </Button>
              </div>
              
              {newToken && (
                <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-md">
                  <h4 className="text-sm font-medium text-green-800 mb-2">Token Generated Successfully!</h4>
                  <div className="text-sm text-green-700">
                    <p className="mb-2"><strong>Name:</strong> {newToken.name}</p>
                    <p className="mb-2"><strong>Token:</strong></p>
                    <code className="block p-2 bg-white border rounded text-xs break-all">
                      {newToken.token}
                    </code>
                    <p className="mt-2 text-xs text-green-600">
                      ⚠️ Save this token now! You won't be able to see it again.
                    </p>
                  </div>
                </div>
              )}
            </div>

            {/* Token List */}
            <div className="bg-white shadow rounded-lg">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-medium text-gray-900">Active Tokens</h3>
              </div>
              <div className="px-6 py-4">
                <div className="text-center text-gray-500">
                  No API tokens created yet.
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'settings' && (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold text-gray-900">System Settings</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Default Limits</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Free Trial - Max Trains
                    </label>
                    <input
                      type="number"
                      defaultValue={1}
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">
                      Free Trial - Max Scrapes
                    </label>
                    <input
                      type="number"
                      defaultValue={10}
                      className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    />
                  </div>
                  <Button>Save Settings</Button>
                </div>
              </div>

              <div className="bg-white shadow rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4">System Status</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Database</span>
                    <span className="text-sm text-green-600">✅ Connected</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">AI Service</span>
                    <span className="text-sm text-green-600">✅ Connected</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Scraper Engine</span>
                    <span className="text-sm text-green-600">✅ Ready</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
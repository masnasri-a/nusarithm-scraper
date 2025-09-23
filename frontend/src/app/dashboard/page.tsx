'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import axios from 'axios'
import { Button } from '@/components/ui/button'
import CreateTemplate from '@/components/CreateTemplate'
import ScrapeContent from '@/components/ScrapeContent'
import UsageStats from '@/components/UsageStats'
import { getApiUrl } from '@/lib/config'

interface Template {
  id: string
  domain: string
  template: {
    selectors: {
      title: string
      content: string
      author: string
      date: string
    }
    confidence_score: number
  }
  usage_count: number
  success_rate: number
  last_used: string | null
}

interface UserData {
  id: string
  username: string
  email: string
  role: string
  is_active: boolean
  train_count: number
  scrape_count: number
  max_trains: number
  max_scrapes: number
}

export default function DashboardPage() {
  const [templates, setTemplates] = useState<Template[]>([])
  const [userData, setUserData] = useState<UserData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [activeTab, setActiveTab] = useState('templates')
  const router = useRouter()

  useEffect(() => {
    checkAuth()
    loadDashboardData()
  }, [])

  const checkAuth = () => {
    const token = localStorage.getItem('auth_token')
    if (!token) {
      router.push('/auth/login')
      return
    }

    const user = localStorage.getItem('user_data')
    if (user) {
      setUserData(JSON.parse(user))
    }
  }

  const loadDashboardData = async () => {
    try {
      const token = localStorage.getItem('auth_token')
      const headers = { Authorization: `Bearer ${token}` }

      console.log('🔄 Loading dashboard data...')
      const [templatesResponse, userResponse] = await Promise.all([
        axios.get(getApiUrl('/train/templates'), { headers }),
        axios.get(getApiUrl('/users/me'), { headers })
      ])

      console.log('📊 Templates response:', templatesResponse.data)
      console.log('👤 User response:', userResponse.data)

      setTemplates(templatesResponse.data.templates || [])
      setUserData(userResponse.data)
      
      // Update localStorage dengan user data terbaru
      localStorage.setItem('user_data', JSON.stringify(userResponse.data))
      console.log('✅ Dashboard data updated')
    } catch (error) {
      console.error('❌ Error loading dashboard:', error)
    } finally {
      setIsLoading(false)
      setIsRefreshing(false)
    }
  }

  // Fungsi refresh yang dipanggil setelah operasi berhasil
  const refreshData = async () => {
    console.log('🔄 Refreshing data...')
    setIsRefreshing(true)
    await loadDashboardData()
  }

  const handleLogout = () => {
    localStorage.removeItem('auth_token')
    localStorage.removeItem('user_data')
    router.push('/')
  }

  const deleteTemplate = async (templateId: string) => {
    try {
      const token = localStorage.getItem('auth_token')
      await axios.delete(getApiUrl(`/train/template/${templateId}`), {
        headers: { Authorization: `Bearer ${token}` }
      })
      
      // Reload templates
      await refreshData()
    } catch (error) {
      console.error('Error deleting template:', error)
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Loading dashboard...</div>
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
              <div className="flex items-center space-x-2">
                <h1 className="text-3xl font-bold text-gray-900">AI Scraper Dashboard</h1>
                {isRefreshing && (
                  <div className="flex items-center text-blue-600">
                    <svg className="animate-spin h-4 w-4 mr-1" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span className="text-sm">Updating...</span>
                  </div>
                )}
              </div>
              <p className="text-sm text-gray-600">Welcome back, {userData?.username}</p>
            </div>
            <div className="flex items-center space-x-4">
              <Button 
                onClick={refreshData}
                variant="outline"
                size="sm"
                disabled={isRefreshing}
              >
                {isRefreshing ? 'Refreshing...' : 'Refresh'}
              </Button>
              {userData?.role === 'admin' && (
                <Button 
                  onClick={() => router.push('/admin')}
                  variant="outline"
                >
                  Admin Panel
                </Button>
              )}
              <Button onClick={handleLogout} variant="outline">
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Usage Stats */}
      {userData && (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <UsageStats 
            userData={{
              train_count: userData.train_count,
              scrape_count: userData.scrape_count,
              max_trains: userData.max_trains,
              max_scrapes: userData.max_scrapes,
              role: userData.role
            }}
            templatesCount={templates.length}
          />
        </div>
      )}

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Tabs */}
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('templates')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'templates'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Templates
            </button>
            <button
              onClick={() => setActiveTab('new-template')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'new-template'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Create Template
            </button>
            <button
              onClick={() => setActiveTab('scrape')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'scrape'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              Scrape Content
            </button>
          </nav>
        </div>

        {/* Tab Content */}
        <div className="py-6">
          {activeTab === 'templates' && (
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold text-gray-900">Your Templates</h2>
                <Button onClick={() => setActiveTab('new-template')}>
                  Create New Template
                </Button>
              </div>

              {templates.length === 0 ? (
                <div className="text-center py-12">
                  <div className="text-gray-500 text-lg">No templates yet</div>
                  <p className="text-gray-400 mt-2">Create your first template to get started</p>
                </div>
              ) : (
                <div className="grid gap-6">
                  {templates.map((template) => (
                    <div key={template.id} className="bg-white shadow rounded-lg p-6">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <h3 className="text-lg font-medium text-gray-900 mb-2">
                            {template.domain}
                          </h3>
                          <div className="grid grid-cols-2 gap-4 text-sm text-gray-600">
                            <div>
                              <span className="font-medium">Usage:</span> {template.usage_count} times
                            </div>
                            <div>
                              <span className="font-medium">Success Rate:</span> {(template.success_rate * 100).toFixed(1)}%
                            </div>
                            <div>
                              <span className="font-medium">Confidence:</span> {(template.template.confidence_score * 100).toFixed(1)}%
                            </div>
                            <div>
                              <span className="font-medium">Last Used:</span> {
                                template.last_used 
                                  ? new Date(template.last_used).toLocaleDateString() 
                                  : 'Never'
                              }
                            </div>
                          </div>
                          
                          <div className="mt-4">
                            <h4 className="font-medium text-gray-900 mb-2">Selectors:</h4>
                            <div className="grid grid-cols-2 gap-2 text-xs">
                              <div>
                                <span className="font-medium">Title:</span> 
                                <code className="bg-gray-100 px-1 rounded ml-1">
                                  {template.template.selectors.title}
                                </code>
                              </div>
                              <div>
                                <span className="font-medium">Content:</span> 
                                <code className="bg-gray-100 px-1 rounded ml-1">
                                  {template.template.selectors.content}
                                </code>
                              </div>
                              <div>
                                <span className="font-medium">Author:</span> 
                                <code className="bg-gray-100 px-1 rounded ml-1">
                                  {template.template.selectors.author}
                                </code>
                              </div>
                              <div>
                                <span className="font-medium">Date:</span> 
                                <code className="bg-gray-100 px-1 rounded ml-1">
                                  {template.template.selectors.date}
                                </code>
                              </div>
                            </div>
                          </div>
                        </div>
                        <div className="ml-4">
                          <Button
                            onClick={() => deleteTemplate(template.id)}
                            variant="destructive"
                            size="sm"
                          >
                            Delete
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {activeTab === 'new-template' && userData && (
            <div>
              <div className="mb-6">
                <h2 className="text-2xl font-bold text-gray-900">Create New Template</h2>
                <p className="text-gray-600 mt-2">
                  Train AI to extract data from websites using example pages
                </p>
              </div>
              <CreateTemplate 
                onTemplateCreated={refreshData}
                userLimits={{
                  train_count: userData.train_count,
                  max_trains: userData.max_trains
                }}
              />
            </div>
          )}

          {activeTab === 'scrape' && userData && (
            <div>
              <div className="mb-6">
                <h2 className="text-2xl font-bold text-gray-900">Scrape Content</h2>
                <p className="text-gray-600 mt-2">
                  Extract data from websites using your trained templates
                </p>
              </div>
              <ScrapeContent 
                userLimits={{
                  scrape_count: userData.scrape_count,
                  max_scrapes: userData.max_scrapes
                }}
                onScrapeCompleted={refreshData}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
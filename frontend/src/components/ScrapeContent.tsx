'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import LoadingSpinner from '@/components/LoadingSpinner'
import axios from 'axios'

interface Template {
  id: string
  domain: string
  template: {
    selectors: Record<string, string>
    confidence_score: number
  }
  usage_count: number
  success_rate: number
}

interface ScrapeContentProps {
  userLimits: {
    scrape_count: number
    max_scrapes: number
  }
  onScrapeCompleted: () => void
}

interface ScrapeResult {
  url: string
  domain: string
  template_used: string
  scraped_at: string
  data: Record<string, any>
  success: boolean
}

export default function ScrapeContent({ userLimits, onScrapeCompleted }: ScrapeContentProps) {
  const [templates, setTemplates] = useState<Template[]>([])
  const [selectedTemplate, setSelectedTemplate] = useState<string>('')
  const [urls, setUrls] = useState<string>('')
  const [outputFormat, setOutputFormat] = useState<'html' | 'markdown' | 'plaintext'>('html')
  const [isLoading, setIsLoading] = useState(false)
  const [results, setResults] = useState<ScrapeResult[]>([])
  const [error, setError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)

  const canScrape = userLimits.max_scrapes === -1 || userLimits.scrape_count < userLimits.max_scrapes

  useEffect(() => {
    loadTemplates()
  }, [])

  const loadTemplates = async () => {
    try {
      const token = localStorage.getItem('auth_token')
      const response = await axios.get('/api/backend/train/templates', {
        headers: { Authorization: `Bearer ${token}` }
      })
      setTemplates(response.data.templates || [])
    } catch (error) {
      console.error('Error loading templates:', error)
    }
  }

  const handleScrape = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!canScrape) {
      setError('You have reached your scraping limit')
      return
    }

    const urlList = urls.split('\n').filter(url => url.trim())
    if (urlList.length === 0) {
      setError('Please enter at least one URL')
      return
    }

    setIsLoading(true)
    setError(null)
    setSuccessMessage(null)
    setResults([])

    try {
      const token = localStorage.getItem('auth_token')
      
      if (urlList.length === 1) {
        // Single URL scraping
        const response = await axios.post('/api/backend/scrape', {
          url: urlList[0],
          output_format: outputFormat,
          template_id: selectedTemplate || undefined
        }, {
          headers: { 
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        })
        
        setResults([response.data])
      } else {
        // Batch scraping
        const response = await axios.post('/api/backend/scrape/batch', {
          urls: urlList,
          output_format: outputFormat,
          template_id: selectedTemplate || undefined,
          max_concurrent: 3
        }, {
          headers: { 
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        })
        
        setResults(response.data.results || [])
      }

      console.log('✅ Scraping completed successfully, calling refresh callback')
      setSuccessMessage(`Successfully scraped ${urlList.length} URL(s). Your usage stats are being updated...`)
      onScrapeCompleted()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to scrape content')
    } finally {
      setIsLoading(false)
    }
  }

  const downloadResults = () => {
    const dataStr = JSON.stringify(results, null, 2)
    const dataBlob = new Blob([dataStr], { type: 'application/json' })
    const url = URL.createObjectURL(dataBlob)
    const link = document.createElement('a')
    link.href = url
    link.download = `scrape-results-${new Date().toISOString().split('T')[0]}.json`
    link.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Scraping Form */}
        <div className="bg-white shadow rounded-lg p-6">
          <div className="mb-6">
            <h3 className="text-lg font-medium text-gray-900 mb-2">Scrape Content</h3>
            <p className="text-sm text-gray-600">
              Extract data from websites using your trained templates or automatic detection.
            </p>
            
            {!canScrape && (
              <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
                <p className="text-red-800">
                  ⚠️ You have reached your scraping limit ({userLimits.scrape_count}/{userLimits.max_scrapes})
                </p>
              </div>
            )}

            {successMessage && (
              <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-md">
                <p className="text-green-800">
                  ✅ {successMessage}
                </p>
              </div>
            )}
          </div>

          <form onSubmit={handleScrape} className="space-y-6">
            {/* Template Selection */}
            <div>
              <label htmlFor="template" className="block text-sm font-medium text-gray-700 mb-2">
                Template (Optional)
              </label>
              <select
                id="template"
                value={selectedTemplate}
                onChange={(e) => setSelectedTemplate(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                disabled={!canScrape}
              >
                <option value="">Auto-detect (use AI to find best template)</option>
                {templates.map((template) => (
                  <option key={template.id} value={template.id}>
                    {template.domain} (Confidence: {(template.template.confidence_score * 100).toFixed(1)}%)
                  </option>
                ))}
              </select>
              <p className="mt-1 text-xs text-gray-500">
                Choose a template or let AI automatically detect the best one
              </p>
            </div>

            {/* URLs Input */}
            <div>
              <label htmlFor="urls" className="block text-sm font-medium text-gray-700 mb-2">
                URLs to Scrape
              </label>
              <textarea
                id="urls"
                value={urls}
                onChange={(e) => setUrls(e.target.value)}
                placeholder="https://example.com/article/1&#10;https://example.com/article/2&#10;https://example.com/article/3"
                rows={6}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                required
                disabled={!canScrape}
              />
              <p className="mt-1 text-xs text-gray-500">
                Enter one URL per line for batch scraping
              </p>
            </div>

            {/* Output Format */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Output Format
              </label>
              <div className="flex space-x-4">
                {[
                  { value: 'html', label: 'HTML' },
                  { value: 'markdown', label: 'Markdown' },
                  { value: 'plaintext', label: 'Plain Text' }
                ].map((format) => (
                  <label key={format.value} className="flex items-center">
                    <input
                      type="radio"
                      value={format.value}
                      checked={outputFormat === format.value}
                      onChange={(e) => setOutputFormat(e.target.value as any)}
                      className="mr-2"
                      disabled={!canScrape}
                    />
                    {format.label}
                  </label>
                ))}
              </div>
            </div>

            {/* Submit Button */}
            <div className="flex justify-end">
              <Button 
                type="submit" 
                disabled={isLoading || !canScrape}
                className="px-6"
              >
                {isLoading ? (
                  <LoadingSpinner text="Scraping..." />
                ) : (
                  'Start Scraping'
                )}
              </Button>
            </div>
          </form>

          {/* Error Display */}
          {error && (
            <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-md">
              <h4 className="text-red-800 font-medium">Error</h4>
              <p className="text-red-700 mt-1">{error}</p>
            </div>
          )}
        </div>

        {/* Results Panel */}
        <div className="bg-white shadow rounded-lg p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-medium text-gray-900">Results</h3>
            {results.length > 0 && (
              <Button onClick={downloadResults} variant="outline" size="sm">
                Download JSON
              </Button>
            )}
          </div>

          {results.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No results yet. Start scraping to see extracted data here.
            </div>
          ) : (
            <div className="space-y-4 max-h-96 overflow-y-auto">
              {results.map((result, index) => (
                <div 
                  key={index} 
                  className={`p-4 rounded-lg border ${
                    result.success ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-sm truncate">
                      {new URL(result.url).hostname}
                    </h4>
                    <span className={`text-xs px-2 py-1 rounded ${
                      result.success ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {result.success ? 'Success' : 'Failed'}
                    </span>
                  </div>
                  
                  <div className="text-xs text-gray-600 mb-2">
                    <a href={result.url} target="_blank" rel="noopener noreferrer" 
                       className="text-blue-600 hover:underline truncate block">
                      {result.url}
                    </a>
                  </div>

                  {result.success && result.data && (
                    <div className="space-y-2">
                      {Object.entries(result.data).map(([field, value]) => (
                        <div key={field} className="text-xs">
                          <strong className="text-gray-700">{field}:</strong>
                          <div className="mt-1 p-2 bg-white rounded border max-h-20 overflow-y-auto">
                            {typeof value === 'string' ? (
                              <div dangerouslySetInnerHTML={{ 
                                __html: value
                              }} />
                            ) : (
                              <pre className="text-xs">{JSON.stringify(value, null, 2)}</pre>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Help Section */}
      <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="text-blue-800 font-medium mb-2">💡 Scraping Tips</h4>
        <ul className="text-blue-700 text-sm space-y-1">
          <li>• For best results, use URLs from the same domain as your trained templates</li>
          <li>• Auto-detect mode will try to find the best template automatically</li>
          <li>• Batch scraping supports multiple URLs (one per line)</li>
          <li>• HTML format preserves original formatting and images</li>
          <li>• Markdown format is great for documentation and readability</li>
          <li>• Plain text format extracts only the text content</li>
        </ul>
      </div>
    </div>
  )
}
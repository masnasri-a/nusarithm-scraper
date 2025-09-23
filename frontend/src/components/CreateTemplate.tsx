'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import LoadingSpinner from '@/components/LoadingSpinner'
import axios from 'axios'

interface CreateTemplateProps {
  onTemplateCreated: () => void
  userLimits: {
    train_count: number
    max_trains: number
  }
}

export default function CreateTemplate({ onTemplateCreated, userLimits }: CreateTemplateProps) {
  const [formData, setFormData] = useState({
    url: '',
    expected_schema: {
      title: 'string',
      content: 'string',
      author: 'string',
      date: 'string'
    } as Record<string, string>
  })
  
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  const canCreateTemplate = userLimits.max_trains === -1 || userLimits.train_count < userLimits.max_trains

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!canCreateTemplate) {
      setError('You have reached your template creation limit')
      return
    }

    setIsLoading(true)
    setError(null)
    setResult(null)

    try {
      const token = localStorage.getItem('auth_token')
      const response = await axios.post('/api/backend/train/', formData, {
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      setResult(response.data)
      console.log('✅ Template created successfully, calling refresh callback')
      onTemplateCreated()
      
      // Reset form
      setFormData({
        url: '',
        expected_schema: {
          title: 'string',
          content: 'string', 
          author: 'string',
          date: 'string'
        } as Record<string, string>
      })
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create template')
    } finally {
      setIsLoading(false)
    }
  }

  const handleSchemaChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      expected_schema: {
        ...prev.expected_schema,
        [field]: value
      }
    }))
  }

  const addSchemaField = () => {
    const fieldName = prompt('Enter field name:')
    if (fieldName) {
      setFormData(prev => ({
        ...prev,
        expected_schema: {
          ...prev.expected_schema,
          [fieldName]: 'string'
        }
      }))
    }
  }

  const removeSchemaField = (field: string) => {
    setFormData(prev => {
      const newSchema = { ...prev.expected_schema }
      delete newSchema[field]
      return {
        ...prev,
        expected_schema: newSchema
      }
    })
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="bg-white shadow rounded-lg p-6">
        <div className="mb-6">
          <h3 className="text-lg font-medium text-gray-900 mb-2">Create AI Template</h3>
          <p className="text-sm text-gray-600">
            Provide a sample URL and define the fields you want to extract. Our AI will automatically generate CSS selectors.
          </p>
          
          {!canCreateTemplate && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
              <p className="text-red-800">
                ⚠️ You have reached your template creation limit ({userLimits.train_count}/{userLimits.max_trains})
              </p>
            </div>
          )}
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* URL Input */}
          <div>
            <label htmlFor="url" className="block text-sm font-medium text-gray-700 mb-2">
              Sample URL
            </label>
            <input
              type="url"
              id="url"
              value={formData.url}
              onChange={(e) => setFormData(prev => ({ ...prev, url: e.target.value }))}
              placeholder="https://example.com/article/sample"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              required
              disabled={!canCreateTemplate}
            />
            <p className="mt-1 text-xs text-gray-500">
              Enter a URL of a representative page you want to scrape
            </p>
          </div>

          {/* Schema Definition */}
          <div>
            <div className="flex justify-between items-center mb-3">
              <label className="block text-sm font-medium text-gray-700">
                Fields to Extract
              </label>
              <Button 
                type="button" 
                onClick={addSchemaField} 
                variant="outline" 
                size="sm"
                disabled={!canCreateTemplate}
              >
                Add Field
              </Button>
            </div>

            <div className="space-y-3">
              {Object.entries(formData.expected_schema).map(([field, type]) => (
                <div key={field} className="flex items-center space-x-3">
                  <input
                    type="text"
                    value={field}
                    readOnly
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-md bg-gray-50"
                  />
                  <select
                    value={type}
                    onChange={(e) => handleSchemaChange(field, e.target.value)}
                    className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    disabled={!canCreateTemplate}
                  >
                    <option value="string">Text</option>
                    <option value="number">Number</option>
                    <option value="date">Date</option>
                    <option value="url">URL</option>
                    <option value="html">HTML Content</option>
                  </select>
                  {['title', 'content', 'author', 'date'].indexOf(field) === -1 && (
                    <Button
                      type="button"
                      onClick={() => removeSchemaField(field)}
                      variant="destructive"
                      size="sm"
                      disabled={!canCreateTemplate}
                    >
                      Remove
                    </Button>
                  )}
                </div>
              ))}
            </div>
            <p className="mt-2 text-xs text-gray-500">
              Define the fields you want to extract from the webpage
            </p>
          </div>

          {/* Submit Button */}
          <div className="flex justify-end">
            <Button 
              type="submit" 
              disabled={isLoading || !canCreateTemplate}
              className="px-6"
            >
              {isLoading ? (
                <LoadingSpinner text="Creating Template..." />
              ) : (
                'Create Template'
              )}
            </Button>
          </div>
        </form>

        {/* Results */}
        {error && (
          <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-md">
            <h4 className="text-red-800 font-medium">Error</h4>
            <p className="text-red-700 mt-1">{error}</p>
          </div>
        )}

        {result && (
          <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-md">
            <h4 className="text-green-800 font-medium mb-3">✅ Template Created Successfully!</h4>
            <p className="text-green-700 text-sm mb-3">Your usage stats are being updated...</p>
            <div className="space-y-2">
              <div>
                <strong>Domain:</strong> <code className="bg-green-100 px-1 rounded">{result.domain}</code>
              </div>
              <div>
                <strong>Confidence Score:</strong> <span className="text-green-700">{(result.template?.confidence_score * 100).toFixed(1)}%</span>
              </div>
              <div>
                <strong>Generated Selectors:</strong>
                <div className="mt-2 grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                  {result.template?.selectors && Object.entries(result.template.selectors).map(([field, selector]: [string, any]) => (
                    <div key={field} className="bg-green-100 p-2 rounded">
                      <strong>{field}:</strong>
                      <br />
                      <code className="text-xs">{selector}</code>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Help Section */}
      <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="text-blue-800 font-medium mb-2">💡 Tips for Better Templates</h4>
        <ul className="text-blue-700 text-sm space-y-1">
          <li>• Use a representative page that contains all the fields you want to extract</li>
          <li>• Make sure the sample URL is accessible and loads properly</li>
          <li>• Include common fields like title, content, author, and date</li>
          <li>• The AI will analyze the page structure and generate optimal CSS selectors</li>
          <li>• Higher confidence scores indicate better template quality</li>
        </ul>
      </div>
    </div>
  )
}
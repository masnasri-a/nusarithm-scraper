'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import axios from 'axios'
import { getApiUrl } from '@/lib/config'

interface URLPreviewProps {
  url: string
}

export default function URLPreview({ url }: URLPreviewProps) {
  const [preview, setPreview] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handlePreview = async () => {
    if (!url) return

    setIsLoading(true)
    setError(null)

    try {
      const token = localStorage.getItem('auth_token')
      const response = await axios.get(getApiUrl(`/scrape/preview?url=${encodeURIComponent(url)}&show_selectors=true`), {
        headers: { Authorization: `Bearer ${token}` }
      })

      setPreview(response.data)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to preview URL')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="mt-4 p-4 bg-gray-50 rounded-lg">
      <div className="flex justify-between items-center mb-3">
        <h4 className="font-medium text-gray-900">URL Preview</h4>
        <Button 
          onClick={handlePreview} 
          variant="outline" 
          size="sm"
          disabled={!url || isLoading}
        >
          {isLoading ? 'Loading...' : 'Preview'}
        </Button>
      </div>

      {error && (
        <div className="text-red-600 text-sm mb-3">{error}</div>
      )}

      {preview && (
        <div className="space-y-3">
          <div>
            <strong className="text-sm">Title:</strong>
            <div className="text-sm text-gray-600 mt-1">{preview.title || 'Not found'}</div>
          </div>
          
          <div>
            <strong className="text-sm">Meta Description:</strong>
            <div className="text-sm text-gray-600 mt-1">{preview.description || 'Not found'}</div>
          </div>

          <div>
            <strong className="text-sm">Detected Structure:</strong>
            <div className="text-xs text-gray-500 mt-1 max-h-32 overflow-y-auto">
              <pre>{JSON.stringify(preview.structure, null, 2)}</pre>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
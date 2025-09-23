// API Configuration
export const API_BASE_URL = 'https://scraper-api.nusarithm.id'

// Helper function to get API URL
export const getApiUrl = (endpoint: string): string => {
  // Remove leading slash if present to avoid double slashes
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint
  return `${API_BASE_URL}/${cleanEndpoint}`
}
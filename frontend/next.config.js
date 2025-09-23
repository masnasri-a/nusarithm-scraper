/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable standalone output for Docker production builds
  output: 'standalone',
  
  // Better error handling and development settings
  onDemandEntries: {
    // period (in ms) where the server will keep pages in the buffer
    maxInactiveAge: 25 * 1000,
    // number of pages that should be kept simultaneously without being disposed
    pagesBufferLength: 2,
  },

  async rewrites() {
    // Determine the backend URL based on environment
    const isDev = process.env.NODE_ENV === 'development';
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 
                      (isDev ? 'http://localhost:6777' : 'https://scraper.nusarithm.id/api');
    
    console.log(`Next.js Rewrite: /api/backend/* -> ${backendUrl}/*`);
    
    return [
      {
        source: '/api/backend/:path*',
        destination: `${backendUrl}/:path*`,
      },
    ]
  },

  // Webpack configuration to avoid potential issues
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        net: false,
        tls: false,
      }
    }
    return config
  },

  // Better development experience
  reactStrictMode: true,
  
  // Disable source maps in development to reduce memory usage
  productionBrowserSourceMaps: false,
}

module.exports = nextConfig
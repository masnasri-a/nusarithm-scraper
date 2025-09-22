/** @type {import('next').NextConfig} */
const nextConfig = {
  // Better error handling and development settings
  onDemandEntries: {
    // period (in ms) where the server will keep pages in the buffer
    maxInactiveAge: 25 * 1000,
    // number of pages that should be kept simultaneously without being disposed
    pagesBufferLength: 2,
  },

  async rewrites() {
    return [
      {
        source: '/api/backend/:path*',
        destination: 'http://localhost:8000/:path*',
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
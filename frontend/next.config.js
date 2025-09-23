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

  // No rewrites needed - frontend directly calls https://scraper-api.nusarithm.id/
  async rewrites() {
    console.log('No API rewrites - using direct backend URL');
    return []
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
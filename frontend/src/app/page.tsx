'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'

export default function HomePage() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const router = useRouter()

  useEffect(() => {
    try {
      // Check if user is authenticated
      const token = localStorage.getItem('auth_token')
      if (token) {
        // Validate token here
        setIsAuthenticated(true)
      }
    } catch (err) {
      console.error('Error checking authentication:', err)
      setError('Failed to check authentication status')
    } finally {
      setIsLoading(false)
    }
  }, [])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white">
        <div className="text-lg text-gray-600">Loading...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-white">
        <div className="text-center">
          <div className="text-red-600 text-lg mb-4">⚠️ {error}</div>
          <button 
            onClick={() => window.location.reload()} 
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            Reload Page
          </button>
        </div>
      </div>
    )
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-white">
        {/* Navigation */}
        <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16 items-center">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <h1 className="text-xl font-bold text-gray-900">
                    🌠 Nusarithm AI Scraper
                  </h1>
                </div>
              </div>
              <div className="hidden md:block">
                <div className="ml-10 flex items-baseline space-x-4">
                  <a href="#features" className="text-gray-600 hover:text-gray-900 px-3 py-2 text-sm font-medium">Features</a>
                  <a href="#templates" className="text-gray-600 hover:text-gray-900 px-3 py-2 text-sm font-medium">Templates</a>
                  <a href="#pricing" className="text-gray-600 hover:text-gray-900 px-3 py-2 text-sm font-medium">Pricing</a>
                  <Link href="/auth/login" className="text-blue-600 hover:text-blue-700 px-3 py-2 text-sm font-medium">
                    Login
                  </Link>
                  <Link href="/auth/register" className="bg-blue-600 text-white hover:bg-blue-700 px-4 py-2 rounded-md text-sm font-medium">
                    Start Free Trial
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </nav>

        {/* Hero Section */}
        <section className="relative bg-gradient-to-b from-blue-50 to-white py-20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center">
              <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
                Easy Web Scraping <br />
                <span className="text-blue-600">for Anyone</span>
              </h1>
              <p className="text-xl md:text-2xl text-gray-600 mb-8 max-w-3xl mx-auto">
                AI Scraper is your no-coding solution for web scraping to turn pages into structured data within clicks.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
                <Link href="/auth/register" className="bg-blue-600 text-white hover:bg-blue-700 px-8 py-4 rounded-lg text-lg font-semibold transition-colors">
                  Start a free trial
                </Link>
              </div>
              
              {/* Trust indicators */}
              <div className="flex justify-center items-center space-x-8 opacity-70">
                <div className="text-sm text-gray-500">Trusted by data-driven organizations</div>
              </div>
            </div>
          </div>
        </section>

        {/* Feature Cards */}
        <section id="features" className="py-20 bg-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
              
              <div className="text-center">
                <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">🧠</span>
                </div>
                <h3 className="text-xl font-semibold mb-3 text-gray-900">No code is the best code</h3>
                <p className="text-gray-600">
                  AI Scraper allows everyone to build reliable web scrapers they need - no coding needed. Design your own scraper with AI assistance.
                </p>
              </div>

              <div className="text-center">
                <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">🤖</span>
                </div>
                <h3 className="text-xl font-semibold mb-3 text-gray-900">The only AI assistant you need</h3>
                <p className="text-gray-600">
                  Access the limitless power of AI, right inside AI Scraper. Get started faster with auto-detect and receive timely tips every step.
                </p>
              </div>

              <div className="text-center">
                <div className="bg-purple-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">⚡</span>
                </div>
                <h3 className="text-xl font-semibold mb-3 text-gray-900">Automation that goes beyond</h3>
                <p className="text-gray-600">
                  Maximize scraping efficiency with our 24/7 cloud solution and schedule scrapers to get data just in time or in flexible intervals.
                </p>
              </div>

              <div className="text-center">
                <div className="bg-orange-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">🔧</span>
                </div>
                <h3 className="text-xl font-semibold mb-3 text-gray-900">Infinitely configurable</h3>
                <p className="text-gray-600">
                  Interact with web elements the way you want. Get ahead of web scraping challenges with IP rotation, CAPTCHA solving, and more.
                </p>
              </div>

            </div>
          </div>
        </section>

        {/* Templates Section */}
        <section id="templates" className="py-20 bg-gray-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold text-gray-900 mb-4">
                There's a template for that
              </h2>
              <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                Browse hundreds of preset templates for the most popular websites and get data instantly with zero setup.
              </p>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              {[
                {
                  title: 'News Scraper',
                  description: 'Extract news articles, titles, content, and metadata from news websites',
                  icon: '📰'
                },
                {
                  title: 'Job Listings Scraper',
                  description: 'Collect job postings, salaries, requirements, and company information',
                  icon: '💼'
                },
                {
                  title: 'Real Estate Scraper',
                  description: 'Gather property listings, prices, features, and location data',
                  icon: '🏠'
                },
                {
                  title: 'Directory Scraper',
                  description: 'Extract business listings, contact details, and review information',
                  icon: '📋'
                }
              ].map((template, index) => (
                <div key={index} className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow">
                  <div className="text-3xl mb-3">{template.icon}</div>
                  <h3 className="text-lg font-semibold mb-2 text-gray-900">{template.title}</h3>
                  <p className="text-gray-600 text-sm">{template.description}</p>
                </div>
              ))}
            </div>

            <div className="text-center mt-12">
              <button className="bg-blue-600 text-white hover:bg-blue-700 px-8 py-3 rounded-lg font-semibold transition-colors">
                Browse all templates
              </button>
            </div>
          </div>
        </section>

        {/* Use Cases */}
        <section className="py-20 bg-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold text-gray-900 mb-4">
                Use Cases for Nearly Every Industry
              </h2>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              {[
                'Lead Generation',
                'Market Research', 
                'Content Curation',
                'E-commerce Intelligence',
                'Social Media Monitoring',
                'Real Estate Analysis',
                'Financial Data',
                'Academic Research'
              ].map((useCase, index) => (
                <div key={index} className="bg-gradient-to-br from-blue-50 to-indigo-100 p-6 rounded-lg text-center hover:shadow-md transition-shadow">
                  <h3 className="text-lg font-semibold text-gray-900">{useCase}</h3>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Pricing Section */}
        <section id="pricing" className="py-20 bg-gray-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold text-gray-900 mb-4">
                Get started for free
              </h2>
              <p className="text-xl text-gray-600">
                Sign up free and start your 14-day premium trial
              </p>
            </div>

            <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
              {/* Free Plan */}
              <div className="bg-white p-8 rounded-lg shadow-md">
                <h3 className="text-2xl font-bold text-gray-900 mb-4">Free Trial</h3>
                <div className="text-4xl font-bold text-blue-600 mb-4">$0</div>
                <ul className="space-y-3 mb-8">
                  <li className="flex items-center text-gray-600">
                    <span className="text-green-500 mr-3">✓</span>
                    1 Template Creation
                  </li>
                  <li className="flex items-center text-gray-600">
                    <span className="text-green-500 mr-3">✓</span>
                    10 Scraping Requests
                  </li>
                  <li className="flex items-center text-gray-600">
                    <span className="text-green-500 mr-3">✓</span>
                    Basic AI Assistance
                  </li>
                </ul>
                <Link href="/auth/register" className="w-full bg-gray-200 text-gray-800 hover:bg-gray-300 py-3 rounded-lg font-semibold transition-colors block text-center">
                  Start Free Trial
                </Link>
              </div>

              {/* Pro Plan */}
              <div className="bg-white p-8 rounded-lg shadow-md border-2 border-blue-500 relative">
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 bg-blue-500 text-white px-4 py-1 rounded-full text-sm font-semibold">
                  Most Popular
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-4">Professional</h3>
                <div className="text-4xl font-bold text-blue-600 mb-4">$29</div>
                <ul className="space-y-3 mb-8">
                  <li className="flex items-center text-gray-600">
                    <span className="text-green-500 mr-3">✓</span>
                    Unlimited Templates
                  </li>
                  <li className="flex items-center text-gray-600">
                    <span className="text-green-500 mr-3">✓</span>
                    10,000 Scraping Requests
                  </li>
                  <li className="flex items-center text-gray-600">
                    <span className="text-green-500 mr-3">✓</span>
                    Advanced AI Features
                  </li>
                  <li className="flex items-center text-gray-600">
                    <span className="text-green-500 mr-3">✓</span>
                    Priority Support
                  </li>
                </ul>
                <Link href="/auth/register" className="w-full bg-blue-600 text-white hover:bg-blue-700 py-3 rounded-lg font-semibold transition-colors block text-center">
                  Start Pro Trial
                </Link>
              </div>

              {/* Enterprise Plan */}
              <div className="bg-white p-8 rounded-lg shadow-md">
                <h3 className="text-2xl font-bold text-gray-900 mb-4">Enterprise</h3>
                <div className="text-4xl font-bold text-blue-600 mb-4">Custom</div>
                <ul className="space-y-3 mb-8">
                  <li className="flex items-center text-gray-600">
                    <span className="text-green-500 mr-3">✓</span>
                    Unlimited Everything
                  </li>
                  <li className="flex items-center text-gray-600">
                    <span className="text-green-500 mr-3">✓</span>
                    Dedicated Support
                  </li>
                  <li className="flex items-center text-gray-600">
                    <span className="text-green-500 mr-3">✓</span>
                    Custom Integration
                  </li>
                  <li className="flex items-center text-gray-600">
                    <span className="text-green-500 mr-3">✓</span>
                    SLA & Security
                  </li>
                </ul>
                <button className="w-full bg-gray-200 text-gray-800 hover:bg-gray-300 py-3 rounded-lg font-semibold transition-colors">
                  Contact Sales
                </button>
              </div>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="bg-gray-900 text-white py-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid md:grid-cols-4 gap-8">
              <div>
                <h3 className="text-lg font-semibold mb-4">🌠 Nusarithm AI Scraper</h3>
                <p className="text-gray-400 text-sm">
                  The no-code solution for intelligent web scraping powered by AI.
                </p>
              </div>
              
              <div>
                <h4 className="font-semibold mb-4">Product</h4>
                <ul className="space-y-2 text-sm text-gray-400">
                  <li><a href="#" className="hover:text-white">Features</a></li>
                  <li><a href="#" className="hover:text-white">Templates</a></li>
                  <li><a href="#" className="hover:text-white">Pricing</a></li>
                  <li><a href="#" className="hover:text-white">API</a></li>
                </ul>
              </div>

              <div>
                <h4 className="font-semibold mb-4">Company</h4>
                <ul className="space-y-2 text-sm text-gray-400">
                  <li><a href="#" className="hover:text-white">About</a></li>
                  <li><a href="#" className="hover:text-white">Blog</a></li>
                  <li><a href="#" className="hover:text-white">Careers</a></li>
                  <li><a href="#" className="hover:text-white">Contact</a></li>
                </ul>
              </div>

              <div>
                <h4 className="font-semibold mb-4">Support</h4>
                <ul className="space-y-2 text-sm text-gray-400">
                  <li><a href="#" className="hover:text-white">Help Center</a></li>
                  <li><a href="#" className="hover:text-white">Documentation</a></li>
                  <li><a href="#" className="hover:text-white">Community</a></li>
                  <li><a href="#" className="hover:text-white">Status</a></li>
                </ul>
              </div>
            </div>

            <div className="border-t border-gray-800 mt-8 pt-8 text-center text-sm text-gray-400">
              <p>&copy; 2025 Nusarithm AI Scraper. All rights reserved. | Aliendev</p>
            </div>
          </div>
        </footer>
      </div>
    )
  }

  // Authenticated user - redirect to dashboard
  router.push('/dashboard')
  return null
}
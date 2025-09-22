'use client'

import { useState, useEffect } from 'react'

interface StatsCardProps {
  title: string
  value: string | number
  icon: string
  color: string
  description?: string
}

export function StatsCard({ title, value, icon, color, description }: StatsCardProps) {
  return (
    <div className="bg-white overflow-hidden shadow rounded-lg">
      <div className="p-5">
        <div className="flex items-center">
          <div className="flex-shrink-0">
            <div className={`w-8 h-8 ${color} rounded-full flex items-center justify-center`}>
              <span className="text-white text-sm font-bold">{icon}</span>
            </div>
          </div>
          <div className="ml-5 w-0 flex-1">
            <dl>
              <dt className="text-sm font-medium text-gray-500 truncate">
                {title}
              </dt>
              <dd className="text-lg font-medium text-gray-900">
                {value}
              </dd>
              {description && (
                <dd className="text-xs text-gray-500 mt-1">
                  {description}
                </dd>
              )}
            </dl>
          </div>
        </div>
      </div>
    </div>
  )
}

interface UsageStatsProps {
  userData: {
    train_count: number
    scrape_count: number
    max_trains: number
    max_scrapes: number
    role: string
  }
  templatesCount: number
}

export default function UsageStats({ userData, templatesCount }: UsageStatsProps) {
  const [timeOfDay, setTimeOfDay] = useState('')

  useEffect(() => {
    const hour = new Date().getHours()
    if (hour < 12) setTimeOfDay('Good morning')
    else if (hour < 17) setTimeOfDay('Good afternoon')
    else setTimeOfDay('Good evening')
  }, [])

  const getAccountType = () => {
    if (userData.role === 'admin') return 'Admin'
    if (userData.max_trains === 1) return 'Free Trial'
    return 'Premium'
  }

  const getUsagePercentage = (used: number, max: number) => {
    if (max === -1) return 0 // Unlimited
    return Math.round((used / max) * 100)
  }

  return (
    <div className="mb-8">
      <div className="mb-6">
        <h2 className="text-lg font-medium text-gray-900">
          {timeOfDay}! Here's your usage overview
        </h2>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <StatsCard
          title="Templates Trained"
          value={`${userData.train_count} / ${userData.max_trains === -1 ? '∞' : userData.max_trains}`}
          icon="T"
          color="bg-blue-500"
          description={userData.max_trains !== -1 ? `${getUsagePercentage(userData.train_count, userData.max_trains)}% used` : 'Unlimited'}
        />

        <StatsCard
          title="Scrapes Used"
          value={`${userData.scrape_count} / ${userData.max_scrapes === -1 ? '∞' : userData.max_scrapes}`}
          icon="S"
          color="bg-green-500"
          description={userData.max_scrapes !== -1 ? `${getUsagePercentage(userData.scrape_count, userData.max_scrapes)}% used` : 'Unlimited'}
        />

        <StatsCard
          title="Account Type"
          value={getAccountType()}
          icon="A"
          color="bg-purple-500"
          description={userData.role === 'admin' ? 'Full access' : 'Standard user'}
        />

        <StatsCard
          title="Total Templates"
          value={templatesCount}
          icon="D"
          color="bg-yellow-500"
          description="Active templates"
        />
      </div>
    </div>
  )
}
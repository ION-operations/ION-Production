/**
 * Notification System Component
 * Provides visual notifications for new messages and system events
 * 
 * Created: 2025-01-27
 * Purpose: Never miss messages again - notify Braden immediately
 */

import React, { useEffect, useState } from 'react'
import { X, CheckCircle, AlertCircle, Info, MessageSquare } from 'lucide-react'

export interface Notification {
  id: string
  type: 'message' | 'error' | 'success' | 'info'
  title: string
  message: string
  timestamp: Date
  read: boolean
}

interface NotificationSystemProps {
  messages: any[]
  previousMessageCount: number
  onNotificationClick?: () => void
}

export const NotificationSystem: React.FC<NotificationSystemProps> = ({
  messages,
  previousMessageCount,
  onNotificationClick
}) => {
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [unreadCount, setUnreadCount] = useState(0)

  // Detect new messages and create notifications
  useEffect(() => {
    if (messages.length > previousMessageCount) {
      const newMessages = messages.slice(previousMessageCount)
      
      newMessages.forEach((msg) => {
        // Don't notify for messages from electron-app (Braden's own messages)
        if (msg.from_ai && msg.from_ai !== 'electron-app' && msg.from_ai !== 'User') {
          const notification: Notification = {
            id: `msg-${msg.message_id}-${Date.now()}`,
            type: 'message',
            title: `New message from ${msg.from_ai}`,
            message: msg.content.substring(0, 100) + (msg.content.length > 100 ? '...' : ''),
            timestamp: new Date(msg.timestamp || Date.now()),
            read: false
          }
          
          setNotifications(prev => [...prev, notification])
          setUnreadCount(prev => prev + 1)
          
          // Show desktop notification
          if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(notification.title, {
              body: notification.message,
              icon: '/icon.png'
            })
          }
        }
      })
    }
  }, [messages.length, previousMessageCount])

  // Request notification permission on mount
  useEffect(() => {
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission()
    }
  }, [])

  const markAsRead = (id: string) => {
    setNotifications(prev => prev.map(n => n.id === id ? { ...n, read: true } : n))
    setUnreadCount(prev => Math.max(0, prev - 1))
  }

  const removeNotification = (id: string) => {
    setNotifications(prev => {
      const removed = prev.find(n => n.id === id)
      if (removed && !removed.read) {
        setUnreadCount(prev => Math.max(0, prev - 1))
      }
      return prev.filter(n => n.id !== id)
    })
  }

  const clearAll = () => {
    setNotifications([])
    setUnreadCount(0)
  }

  const getIcon = (type: Notification['type']) => {
    switch (type) {
      case 'message': return <MessageSquare className="w-5 h-5" />
      case 'error': return <AlertCircle className="w-5 h-5 text-red-500" />
      case 'success': return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'info': return <Info className="w-5 h-5 text-blue-500" />
    }
  }

  return (
    <div className="fixed top-4 right-4 z-50 flex flex-col gap-2 max-w-md">
      {/* Notifications List */}
      {notifications.length > 0 && (
        <div className="bg-gray-900 border border-gray-700 rounded-lg shadow-xl max-h-96 overflow-y-auto">
          <div className="p-3 border-b border-gray-700 flex items-center justify-between">
            <h3 className="font-semibold text-white">Notifications</h3>
            <button
              onClick={clearAll}
              className="text-gray-400 hover:text-white text-sm"
            >
              Clear All
            </button>
          </div>
          
          <div className="divide-y divide-gray-700">
            {notifications.map((notification) => (
              <div
                key={notification.id}
                className={`p-3 hover:bg-gray-800 transition-colors ${
                  !notification.read ? 'bg-gray-850' : ''
                }`}
              >
                <div className="flex items-start gap-3">
                  <div className="mt-0.5">{getIcon(notification.type)}</div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <h4 className="font-semibold text-white text-sm">{notification.title}</h4>
                      <button
                        onClick={() => removeNotification(notification.id)}
                        className="text-gray-400 hover:text-white"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                    <p className="text-gray-300 text-sm mb-1">{notification.message}</p>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-500">
                        {notification.timestamp.toLocaleTimeString()}
                      </span>
                      {!notification.read && (
                        <button
                          onClick={() => markAsRead(notification.id)}
                          className="text-xs text-blue-400 hover:text-blue-300"
                        >
                          Mark as read
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}


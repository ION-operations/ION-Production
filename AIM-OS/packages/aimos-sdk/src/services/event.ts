/**
 * Event Service - Event publishing and subscription
 */

import { AIMOSClient } from '../client'
import { EventPublishParams } from '../types'

/**
 * Event Service for inter-app communication
 */
export class EventService {
  private subscriptionIntervals: Map<string, NodeJS.Timeout> = new Map()

  constructor(private client: AIMOSClient) {}

  /**
   * Publish an event
   * 
   * @param params Event publish parameters
   */
  async publish(params: EventPublishParams): Promise<void> {
    await this.client.executeTool('send_ai_message', {
      from_ai: this.client.getAppId() || 'unknown',
      to_ai: params.target_apps && params.target_apps.length > 0 ? params.target_apps[0] : 'all',
      content: JSON.stringify({
        type: params.type,
        data: params.data,
        target_apps: params.target_apps,
      }),
      message_type: 'event',
      tags: { event_type: params.type },
    })
  }

  /**
   * Subscribe to events of a specific type
   * 
   * @param eventType Event type to subscribe to
   * @param callback Callback function to handle events
   * @param pollInterval Polling interval in milliseconds (default: 1000)
   */
  async subscribe(
    eventType: string,
    callback: (event: any) => void,
    pollInterval: number = 1000
  ): Promise<void> {
    // Stop existing subscription if any
    this.unsubscribe(eventType)

    const poll = async () => {
      try {
        const result = await this.client.executeTool('get_ai_messages', {
          from_ai: 'all',
          to_ai: this.client.getAppId() || 'all',
          message_type: 'event',
          limit: 10,
        })

        for (const msg of result.messages || []) {
          try {
            const event = JSON.parse(msg.content || '{}')
            if (event.type === eventType) {
              callback(event)
            }
          } catch (e) {
            // Skip invalid event messages
            console.warn('Skipping invalid event message:', e)
          }
        }
      } catch (e) {
        console.error('Error polling for events:', e)
      }
    }

    // Initial poll
    await poll()

    // Set up polling interval
    const interval = setInterval(poll, pollInterval)
    this.subscriptionIntervals.set(eventType, interval)
  }

  /**
   * Unsubscribe from events
   * 
   * @param eventType Event type to unsubscribe from (if not provided, unsubscribe from all)
   */
  unsubscribe(eventType?: string): void {
    if (eventType) {
      const interval = this.subscriptionIntervals.get(eventType)
      if (interval) {
        clearInterval(interval)
        this.subscriptionIntervals.delete(eventType)
      }
    } else {
      // Unsubscribe from all
      for (const interval of this.subscriptionIntervals.values()) {
        clearInterval(interval)
      }
      this.subscriptionIntervals.clear()
    }
  }
}


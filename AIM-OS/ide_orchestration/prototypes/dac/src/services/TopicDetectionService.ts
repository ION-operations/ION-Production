/**
 * Enhanced Topic Detection Service
 * LLM-based semantic topic detection and SEG integration
 */

import { llmService } from './LLMService'
import { useSEG } from '../hooks/useAIMOS'

export interface TopicDetectionResult {
  topics: Array<{
    topicId?: string // Existing topic ID if matched
    name: string
    confidence: number
    relationType?: 'new' | 'existing' | 'related' | 'derived'
    relatedTopics?: string[]
  }>
  entities: Array<{
    entityId: string
    entityType: string
    name: string
    confidence: number
  }>
  relations: Array<{
    sourceId: string
    targetId: string
    relationType: 'SUPPORTS' | 'CONTRADICTS' | 'REFERENCES' | 'DERIVES_FROM' | 'RELATES_TO'
    confidence: number
  }>
}

export class TopicDetectionService {
  /**
   * Detect topics from message content using LLM + SEG
   */
  static async detectTopicsFromContent(
    content: string,
    existingTopics: Array<{ id: string; name: string; tags: Array<{ key: string; value: string }> }>,
    segEntities?: any[]
  ): Promise<TopicDetectionResult> {
    try {
      // Step 1: LLM-based topic extraction
      const prompt = `Analyze the following message and extract:
1. Main topics/concepts mentioned
2. Entities (people, systems, concepts, files)
3. Relationships between topics

Message: "${content}"

Existing topics: ${existingTopics.map(t => t.name).join(', ')}

Return a JSON object with:
{
  "topics": [
    {
      "name": "topic name",
      "confidence": 0.0-1.0,
      "relationType": "new|existing|related|derived",
      "relatedTopics": ["topic names"]
    }
  ],
  "entities": [
    {
      "entityType": "person|system|concept|file",
      "name": "entity name",
      "confidence": 0.0-1.0
    }
  ],
  "relations": [
    {
      "sourceId": "entity or topic name",
      "targetId": "entity or topic name",
      "relationType": "SUPPORTS|CONTRADICTS|REFERENCES|DERIVES_FROM|RELATES_TO",
      "confidence": 0.0-1.0
    }
  ]
}`

      const response = await llmService.generate({
        prompt,
        systemPrompt: 'You are a topic extraction system. Extract topics, entities, and relationships from text.',
        maxTokens: 1000
      })

      // Parse LLM response
      let detectionResult: TopicDetectionResult
      try {
        // Try to extract JSON from response
        const jsonMatch = response.content.match(/\{[\s\S]*\}/)
        if (jsonMatch) {
          detectionResult = JSON.parse(jsonMatch[0])
        } else {
          throw new Error('No JSON found in response')
        }
      } catch (parseError) {
        // Fallback to keyword-based detection
        return this.keywordBasedDetection(content, existingTopics)
      }

      // Step 2: Match with existing topics
      const matchedTopics = detectionResult.topics.map(topic => {
        // Find matching existing topic
        const match = existingTopics.find(et => 
          et.name.toLowerCase() === topic.name.toLowerCase() ||
          et.tags.some(tag => tag.value.toLowerCase().includes(topic.name.toLowerCase()))
        )
        
        return {
          ...topic,
          topicId: match?.id,
          relationType: match ? 'existing' : (topic.relationType || 'new')
        }
      })

      // Step 3: Integrate with SEG entities if available
      if (segEntities && segEntities.length > 0) {
        detectionResult.entities = [
          ...detectionResult.entities,
          ...segEntities.map(e => ({
            entityId: e.id,
            entityType: e.type,
            name: e.name,
            confidence: e.confidence || 0.8
          }))
        ]
      }

      return {
        topics: matchedTopics,
        entities: detectionResult.entities,
        relations: detectionResult.relations
      }
    } catch (error) {
      console.error('LLM topic detection failed, falling back to keyword:', error)
      return this.keywordBasedDetection(content, existingTopics)
    }
  }

  /**
   * Fallback keyword-based topic detection
   */
  static keywordBasedDetection(
    content: string,
    existingTopics: Array<{ id: string; name: string; tags: Array<{ key: string; value: string }> }>
  ): TopicDetectionResult {
    const contentLower = content.toLowerCase()
    const detectedTopics: TopicDetectionResult['topics'] = []
    const detectedEntities: TopicDetectionResult['entities'] = []
    
    // Check existing topics
    existingTopics.forEach(topic => {
      const topicLower = topic.name.toLowerCase()
      
      // Check if topic name appears in content
      if (contentLower.includes(topicLower) || topicLower.includes(contentLower.split(' ')[0])) {
        detectedTopics.push({
          topicId: topic.id,
          name: topic.name,
          confidence: 0.7,
          relationType: 'existing'
        })
      }
      
      // Check tags
      topic.tags.forEach(tag => {
        if (contentLower.includes(tag.value.toLowerCase())) {
          detectedTopics.push({
            topicId: topic.id,
            name: topic.name,
            confidence: 0.6,
            relationType: 'related'
          })
        }
      })
    })
    
    // Extract potential new topics (simple keyword extraction)
    const words = content.split(/\s+/).filter(w => w.length > 4)
    const uniqueWords = [...new Set(words)]
    
    uniqueWords.slice(0, 3).forEach(word => {
      if (!existingTopics.some(t => t.name.toLowerCase().includes(word.toLowerCase()))) {
        detectedTopics.push({
          name: word.charAt(0).toUpperCase() + word.slice(1),
          confidence: 0.5,
          relationType: 'new'
        })
      }
    })
    
    return {
      topics: detectedTopics,
      entities: detectedEntities,
      relations: []
    }
  }

  /**
   * Create SEG entities from detected topics
   */
  static createSEGEntitiesFromTopics(
    topics: TopicDetectionResult['topics'],
    messageId: string
  ): Array<{ id: string; type: string; name: string; attributes: Record<string, any> }> {
    return topics.map((topic, index) => ({
      id: topic.topicId || `topic_entity_${Date.now()}_${index}`,
      type: 'topic',
      name: topic.name,
      attributes: {
        confidence: topic.confidence,
        relationType: topic.relationType,
        sourceMessageId: messageId,
        detectedAt: new Date().toISOString()
      }
    }))
  }

  /**
   * Create SEG relations from detected relationships
   */
  static createSEGRelationsFromTopics(
    relations: TopicDetectionResult['relations'],
    topicMap: Map<string, string> // Map topic names to topic IDs
  ): Array<{
    sourceId: string
    targetId: string
    relationType: string
    evidenceIds: string[]
    confidence: number
  }> {
    return relations.map(rel => ({
      sourceId: topicMap.get(rel.sourceId) || rel.sourceId,
      targetId: topicMap.get(rel.targetId) || rel.targetId,
      relationType: rel.relationType,
      evidenceIds: [],
      confidence: rel.confidence
    }))
  }
}


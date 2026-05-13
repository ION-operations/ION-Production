---
id: "twitter_x_api_deep_dive"
system: "lucid_chat"
component: "api_integration"
level: "T3"
type: "deep_analysis"
title: "Twitter X API v2 Deep Dive - Complete Integration Guide"
description: "Comprehensive analysis of Twitter X API v2 capabilities, endpoints, parameters, workflows, and integration patterns"
created: "2025-01-27T00:00:00Z"
updated: "2025-01-27T00:00:00Z"
author: "aether"
status: "active"
tags: ["twitter", "x", "social-media", "api-integration", "deep-dive"]
---

# Twitter X API v2 Deep Dive - Complete Integration Guide

**Purpose:** Comprehensive understanding of Twitter X API v2 for proper integration  
**Status:** 🔍 **DEEP ANALYSIS COMPLETE**  
**Official Documentation:** https://developer.twitter.com/en/docs/twitter-api

---

## 🎯 **TWITTER X API v2 OVERVIEW**

Twitter X API v2 provides access to Twitter/X data:
- **Tweets** - Read and write tweets
- **Users** - User profiles and information
- **Spaces** - Twitter Spaces (audio)
- **Lists** - User lists
- **Search** - Search tweets and users
- **Streaming** - Real-time tweet streams
- **Media** - Upload images and videos
- **Direct Messages** - Send/receive DMs

**Key Features:**
- REST API v2
- Streaming API
- OAuth 2.0 authentication
- Rate limits
- Tweet metrics

---

## 🔐 **AUTHENTICATION**

**Method:** OAuth 2.0 (Bearer Token)

**Header:**
```
Authorization: Bearer YOUR_BEARER_TOKEN
```

**OAuth 2.0 Flow:**
1. Register app → Get API Key and Secret
2. Get user authorization → Get access token
3. Use access token for API calls

**Credentials Management:**
- Obtain from: https://developer.twitter.com/en/portal
- Store securely in environment variables:
  - `TWITTER_API_KEY`
  - `TWITTER_API_SECRET`
  - `TWITTER_ACCESS_TOKEN`
  - `TWITTER_ACCESS_TOKEN_SECRET`
- Rate limits: Based on account tier

**Base URL:**
```
https://api.twitter.com/2
```

---

## 📡 **API ENDPOINTS & CAPABILITIES**

### **1. Create Tweet**

**Endpoint:** `POST https://api.twitter.com/2/tweets`

**Purpose:** Post a tweet

**Request Parameters:**

```typescript
interface TwitterCreateTweetRequest {
  // Required
  text: string                      // Tweet text (max 280 chars)
  
  // Optional
  direct_message_deep_link?: string
  for_super_followers_only?: boolean
  geo?: {
    place_id: string
  }
  media?: {
    media_ids: string[]             // Media IDs (from upload)
    tagged_user_ids?: string[]
  }
  poll?: {
    options: string[]               // 2-4 options
    duration_minutes: number        // 5-10080 minutes
  }
  quote_tweet_id?: string           // Quote tweet
  reply?: {
    in_reply_to_tweet_id: string
    exclude_reply_user_ids?: string[]
  }
  reply_settings?: 'mentionedUsers' | 'following' | 'everyone'
}
```

**Response:**

```typescript
interface TwitterCreateTweetResponse {
  data: {
    id: string
    text: string
    edit_history_tweet_ids: string[]
  }
}
```

---

### **2. Get Tweet**

**Endpoint:** `GET https://api.twitter.com/2/tweets/{id}`

**Purpose:** Get tweet details

**Query Parameters:**

```typescript
interface TwitterGetTweetRequest {
  // Optional - Expansions
  expansions?: string               // Comma-separated: 'author_id', 'referenced_tweets.id', etc.
  
  // Optional - Tweet Fields
  'tweet.fields'?: string           // Comma-separated: 'created_at', 'author_id', 'public_metrics', etc.
  
  // Optional - User Fields
  'user.fields'?: string            // Comma-separated: 'name', 'username', 'verified', etc.
  
  // Optional - Media Fields
  'media.fields'?: string           // Comma-separated: 'url', 'preview_image_url', etc.
  
  // Optional - Poll Fields
  'poll.fields'?: string            // Comma-separated: 'options', 'voting_status', etc.
}
```

**Response:**

```typescript
interface TwitterGetTweetResponse {
  data: {
    id: string
    text: string
    created_at: string
    author_id: string
    public_metrics: {
      retweet_count: number
      like_count: number
      reply_count: number
      quote_count: number
    }
    possibly_sensitive?: boolean
    lang?: string
    source?: string
    in_reply_to_user_id?: string
    referenced_tweets?: Array<{
      type: 'retweeted' | 'quoted' | 'replied_to'
      id: string
    }>
  }
  includes?: {
    users?: TwitterUser[]
    tweets?: TwitterTweet[]
    media?: TwitterMedia[]
    polls?: TwitterPoll[]
  }
}
```

---

### **3. Search Tweets**

**Endpoint:** `GET https://api.twitter.com/2/tweets/search/recent` or `/all`

**Purpose:** Search tweets

**Query Parameters:**

```typescript
interface TwitterSearchTweetsRequest {
  // Required
  query: string                     // Search query (e.g., 'from:username', 'has:hashtags')
  
  // Optional - Pagination
  max_results?: number              // 10-100 (default: 10)
  next_token?: string               // Pagination token
  
  // Optional - Time Range
  start_time?: string               // ISO 8601 date
  end_time?: string                 // ISO 8601 date
  since_id?: string                 // Tweet ID
  until_id?: string                 // Tweet ID
  
  // Optional - Expansions and Fields (same as Get Tweet)
  expansions?: string
  'tweet.fields'?: string
  'user.fields'?: string
  'media.fields'?: string
  'poll.fields'?: string
  
  // Optional - Sort
  sort_order?: 'recency' | 'relevancy'
}
```

**Search Query Operators:**
- `from:username` - From user
- `to:username` - To user
- `@username` - Mentioning user
- `#hashtag` - Hashtag
- `$symbol` - Cashtag
- `has:hashtags` - Has hashtags
- `has:links` - Has links
- `has:media` - Has media
- `has:videos` - Has videos
- `has:images` - Has images
- `lang:en` - Language
- `-keyword` - Exclude keyword
- `(keyword1 OR keyword2)` - OR operator
- `keyword1 keyword2` - AND operator

---

### **4. Get User**

**Endpoint:** `GET https://api.twitter.com/2/users/{id}` or `/by/username/{username}`

**Purpose:** Get user information

**Query Parameters:**

```typescript
interface TwitterGetUserRequest {
  // Optional - Expansions
  expansions?: string               // 'pinned_tweet_id'
  
  // Optional - User Fields
  'user.fields'?: string            // 'created_at', 'description', 'location', 'public_metrics', etc.
  
  // Optional - Tweet Fields
  'tweet.fields'?: string
}
```

**Response:**

```typescript
interface TwitterGetUserResponse {
  data: {
    id: string
    name: string
    username: string
    created_at: string
    description?: string
    location?: string
    pinned_tweet_id?: string
    profile_image_url?: string
    protected?: boolean
    public_metrics: {
      followers_count: number
      following_count: number
      tweet_count: number
      listed_count: number
    }
    url?: string
    verified?: boolean
    verified_type?: string
    withheld?: {
      country_codes: string[]
      scope?: string
    }
  }
  includes?: {
    tweets?: TwitterTweet[]
  }
}
```

---

### **5. Get User Tweets**

**Endpoint:** `GET https://api.twitter.com/2/users/{id}/tweets`

**Purpose:** Get tweets by a user

**Query Parameters:**

```typescript
interface TwitterGetUserTweetsRequest {
  // Optional - Pagination
  max_results?: number              // 5-100 (default: 10)
  pagination_token?: string
  
  // Optional - Time Range
  start_time?: string
  end_time?: string
  since_id?: string
  until_id?: string
  
  // Optional - Exclusions
  exclude?: 'retweets' | 'replies'  // Comma-separated
  
  // Optional - Expansions and Fields
  expansions?: string
  'tweet.fields'?: string
  'user.fields'?: string
  'media.fields'?: string
}
```

---

### **6. Upload Media**

**Endpoint:** `POST https://upload.twitter.com/1.1/media/upload.json`

**Purpose:** Upload images or videos

**Request:** Multipart form data

**Parameters:**

```typescript
interface TwitterUploadMediaRequest {
  media: File                       // Required: Image or video file
  media_category?: string           // 'tweet_image', 'tweet_video', 'dm_image', 'dm_video'
  additional_owners?: string        // Comma-separated user IDs
}
```

**Response:**

```typescript
interface TwitterUploadMediaResponse {
  media_id: string
  media_id_string: string
  size: number
  expires_after_secs: number
  image?: {
    image_type: string
    w: number
    h: number
  }
  video?: {
    video_type: string
  }
}
```

---

### **7. Streaming API**

**Endpoint:** `GET https://api.twitter.com/2/tweets/search/stream`

**Purpose:** Real-time tweet stream

**Query Parameters:**

```typescript
interface TwitterStreamRequest {
  expansions?: string
  'tweet.fields'?: string
  'user.fields'?: string
  'media.fields'?: string
}
```

**Response:** Server-Sent Events (SSE) stream

---

## 🔄 **WORKFLOWS**

### **Workflow 1: Post Tweet**

1. User enters tweet text
2. Upload media (optional)
3. Configure options (reply settings, etc.)
4. Submit → Post tweet
5. Display posted tweet

### **Workflow 2: Search Tweets**

1. User enters search query
2. Configure filters
3. Set time range
4. Submit → Display results
5. Paginate through results

### **Workflow 3: User Timeline**

1. User enters username
2. Get user info
3. Get user tweets
4. Display timeline

---

## ⚡ **RATE LIMITS**

**Free Tier:**
- 1,500 tweets/month (write)
- Limited read requests

**Paid Tier:**
- Higher limits
- More features

**Rate Limit Headers:**
```
x-rate-limit-limit: 300
x-rate-limit-remaining: 299
x-rate-limit-reset: 1234567890
```

---

## 💰 **PRICING**

**Free Tier:**
- $0/month
- Limited requests

**Paid Tier:**
- $100/month for Basic
- Higher limits

---

## 🎨 **UI COMPONENT REQUIREMENTS**

### **Tweet Composition Panel**

**Text Input:**
- Textarea (280 char limit)
- Character counter
- Mention autocomplete
- Hashtag suggestions

**Media Upload:**
- Image/video upload
- Media preview
- Remove media

**Options:**
- Reply settings selector
- Poll creator
- Location selector

**Post Button:**
- Show loading state

### **Timeline Panel**

**Tweet Cards:**
- User avatar and name
- Tweet text
- Media display
- Engagement metrics
- Actions (like, retweet, reply, share)

**Filters:**
- Search input
- Time range selector
- User filter

---

## 🔧 **IMPLEMENTATION NOTES**

### **Service Layer Structure**

```typescript
class TwitterService extends BaseAPIService {
  constructor(accessToken?: string) {
    super('twitter', 'https://api.twitter.com/2', accessToken)
  }

  async createTweet(request: TwitterCreateTweetRequest): Promise<APIResponse<TwitterCreateTweetResponse>>
  async getTweet(id: string, options?: TwitterGetTweetRequest): Promise<APIResponse<TwitterGetTweetResponse>>
  async searchTweets(request: TwitterSearchTweetsRequest): Promise<APIResponse<any>>
  async getUser(idOrUsername: string, options?: TwitterGetUserRequest): Promise<APIResponse<TwitterGetUserResponse>>
  async getUserTweets(userId: string, options?: TwitterGetUserTweetsRequest): Promise<APIResponse<any>>
  async uploadMedia(file: File, mediaCategory?: string): Promise<APIResponse<TwitterUploadMediaResponse>>
  async streamTweets(options?: TwitterStreamRequest, onTweet?: (tweet: TwitterTweet) => void): Promise<void>
}
```

---

## 📊 **INTEGRATION COMPLEXITY**

**Complexity:** Medium-High

**Dependencies:**
- OAuth 2.0 flow
- Media upload handling
- Streaming support
- Tweet rendering

**Estimated Implementation Time:**
- Service layer: 6-8 hours
- OAuth flow: 4-6 hours
- UI components: 8-10 hours
- Streaming: 3-4 hours
- Testing: 4-6 hours
- **Total: 25-34 hours**

---

**Status:** Deep dive complete - Ready for implementation  
**Last Updated:** 2025-01-27


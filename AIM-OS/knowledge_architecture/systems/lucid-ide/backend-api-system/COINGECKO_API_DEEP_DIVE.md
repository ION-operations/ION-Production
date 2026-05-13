---
id: "coingecko_api_deep_dive"
system: "lucid_chat"
component: "api_integration"
level: "T3"
type: "deep_analysis"
title: "CoinGecko API Deep Dive - Complete Integration Guide"
description: "Comprehensive analysis of CoinGecko API capabilities, endpoints, parameters, workflows, and integration patterns"
created: "2025-01-27T00:00:00Z"
updated: "2025-01-27T00:00:00Z"
author: "aether"
status: "active"
tags: ["coingecko", "cryptocurrency", "api-integration", "deep-dive"]
---

# CoinGecko API Deep Dive - Complete Integration Guide

**Purpose:** Comprehensive understanding of CoinGecko API for proper integration  
**Status:** 🔍 **DEEP ANALYSIS COMPLETE**  
**Official Documentation:** https://www.coingecko.com/en/api/documentation

---

## 🎯 **COINGECKO API OVERVIEW**

CoinGecko provides comprehensive cryptocurrency data:
- **Price Data** - Real-time and historical prices
- **Market Data** - Market cap, volume, rankings
- **Coin Information** - Detailed coin data
- **Trending Coins** - Trending cryptocurrencies
- **Exchange Data** - Exchange information
- **NFT Data** - NFT collections and floor prices
- **DeFi Data** - DeFi protocol data

**Key Features:**
- 13,000+ cryptocurrencies
- Real-time and historical data
- Free tier available
- Multiple data formats
- WebSocket support (Pro)

---

## 🔐 **AUTHENTICATION**

**Method:** API Key (Query Parameter) - Optional for free tier

**Query Parameter:**
```
x_cg_demo_api_key=YOUR_API_KEY
```

**API Key Management:**
- Obtain from: https://www.coingecko.com/en/api/pricing
- Store securely in environment variable: `COINGECKO_API_KEY`
- Free tier: 10-50 calls/minute (no API key needed)

**Base URL:**
```
https://api.coingecko.com/api/v3
```

---

## 📡 **API ENDPOINTS & CAPABILITIES**

### **1. Simple Price**

**Endpoint:** `GET https://api.coingecko.com/api/v3/simple/price`

**Purpose:** Get current price for cryptocurrencies

**Query Parameters:**

```typescript
interface CoinGeckoSimplePriceRequest {
  ids: string                       // Comma-separated coin IDs (e.g., 'bitcoin,ethereum')
  vs_currencies: string             // Comma-separated currencies (e.g., 'usd,eur')
  include_market_cap?: boolean      // Include market cap (default: false)
  include_24hr_vol?: boolean        // Include 24h volume (default: false)
  include_24hr_change?: boolean     // Include 24h change (default: false)
  include_last_updated_at?: boolean // Include last updated timestamp (default: false)
  precision?: number                // Decimal places (default: full)
}
```

**Response Structure:**

```typescript
interface CoinGeckoSimplePriceResponse {
  [coinId: string]: {
    [currency: string]: number       // Price
    [currency + '_market_cap']?: number
    [currency + '_24h_vol']?: number
    [currency + '_24h_change']?: number
    last_updated_at?: number
  }
}
```

---

### **2. Coins List**

**Endpoint:** `GET https://api.coingecko.com/api/v3/coins/list`

**Purpose:** Get list of all supported coins

**Query Parameters:**

```typescript
interface CoinGeckoCoinsListRequest {
  include_platform?: boolean        // Include platform info (default: false)
}
```

**Response:**

```typescript
interface CoinGeckoCoinsListResponse extends Array<{
  id: string
  symbol: string
  name: string
  platforms?: Record<string, string> // Platform addresses
}>
```

---

### **3. Coin Details**

**Endpoint:** `GET https://api.coingecko.com/api/v3/coins/{id}`

**Purpose:** Get detailed information about a coin

**Query Parameters:**

```typescript
interface CoinGeckoCoinDetailsRequest {
  id: string                        // Coin ID (required in path)
  localization?: boolean            // Include localized strings (default: true)
  tickers?: boolean                 // Include ticker data (default: true)
  market_data?: boolean             // Include market data (default: true)
  community_data?: boolean          // Include community data (default: true)
  developer_data?: boolean          // Include developer data (default: true)
  sparkline?: boolean               // Include sparkline (default: false)
}
```

**Response Structure:**

```typescript
interface CoinGeckoCoinDetailsResponse {
  id: string
  symbol: string
  name: string
  asset_platform_id: string | null
  platforms: Record<string, string>
  detail_platforms: Record<string, {
    decimal_place: number | null
    contract_address: string
  }>
  block_time_in_minutes: number
  hashing_algorithm: string | null
  categories: string[]
  public_notice: string | null
  additional_notices: string[]
  localization: Record<string, {
    name: string
    description: string
  }>
  description: Record<string, string>
  links: {
    homepage: string[]
    blockchain_site: string[]
    official_forum_url: string[]
    subreddit_url: string
    repos_url: {
      github: string[]
      bitbucket: string[]
    }
  }
  image: {
    thumb: string
    small: string
    large: string
  }
  country_origin: string
  genesis_date: string | null
  sentiment_votes_up_percentage: number
  sentiment_votes_down_percentage: number
  market_cap_rank: number
  coingecko_rank: number
  coingecko_score: number
  developer_score: number
  community_score: number
  liquidity_score: number
  public_interest_score: number
  market_data: {
    current_price: Record<string, number>
    total_value_locked: number | null
    mcap_to_tvl_ratio: number | null
    fdv_to_tvl_ratio: number | null
    roi: {
      times: number
      currency: string
      percentage: number
    } | null
    ath: Record<string, number>
    ath_change_percentage: Record<string, number>
    ath_date: Record<string, string>
    atl: Record<string, number>
    atl_change_percentage: Record<string, number>
    atl_date: Record<string, string>
    market_cap: Record<string, number>
    market_cap_rank: number
    fully_diluted_valuation: Record<string, number>
    total_volume: Record<string, number>
    high_24h: Record<string, number>
    low_24h: Record<string, number>
    price_change_24h: number
    price_change_percentage_24h: number
    price_change_percentage_7d: number
    price_change_percentage_14d: number
    price_change_percentage_30d: number
    price_change_percentage_60d: number
    price_change_percentage_200d: number
    price_change_percentage_1y: number
    market_cap_change_24h: number
    market_cap_change_percentage_24h: number
    price_change_24h_in_currency: Record<string, number>
    price_change_percentage_1h_in_currency: Record<string, number>
    price_change_percentage_24h_in_currency: Record<string, number>
    price_change_percentage_7d_in_currency: Record<string, number>
    price_change_percentage_14d_in_currency: Record<string, number>
    price_change_percentage_30d_in_currency: Record<string, number>
    price_change_percentage_60d_in_currency: Record<string, number>
    price_change_percentage_200d_in_currency: Record<string, number>
    price_change_percentage_1y_in_currency: Record<string, number>
    market_cap_change_24h_in_currency: Record<string, number>
    market_cap_change_percentage_24h_in_currency: Record<string, number>
    total_supply: number | null
    max_supply: number | null
    circulating_supply: number
    sparkline_7d?: {
      price: number[]
    }
    last_updated: string
  }
  community_data: {
    facebook_likes: number | null
    twitter_followers: number | null
    reddit_average_posts_48h: number | null
    reddit_average_comments_48h: number | null
    reddit_subscribers: number | null
    reddit_accounts_active_48h: number | null
    telegram_channel_user_count: number | null
  }
  developer_data: {
    forks: number | null
    stars: number | null
    subscribers: number | null
    total_issues: number | null
    closed_issues: number | null
    pull_requests_merged: number | null
    pull_requests_contributors: number | null
    code_additions_deletions_4_weeks: {
      additions: number | null
      deletions: number | null
    } | null
    commit_count_4_weeks: number | null
    last_4_weeks_commit_activity_series: number[] | null
  }
  public_interest_stats: {
    alexa_rank: number | null
    bing_matches: number | null
  }
  status_updates: Array<{
    description: string
    category: string
    created_at: string
    user: string
    user_title: string
    pin: boolean
    project: {
      type: string
      id: string
      name: string
      symbol: string
      image: {
        thumb: string
        small: string
        large: string
      }
    }
  }>
  last_updated: string
  tickers: Array<{
    base: string
    target: string
    market: {
      name: string
      identifier: string
      has_trading_incentive: boolean
    }
    last: number
    volume: number
    converted_last: Record<string, number>
    converted_volume: Record<string, number>
    trust_score: string | null
    bid_ask_spread_percentage: number | null
    timestamp: string
    last_traded_at: string
    last_fetch_at: string
    is_anomaly: boolean
    is_stale: boolean
    trade_url: string | null
    token_info_url: string | null
    coin_id: string
    target_coin_id: string
  }>
}
```

---

### **4. Coin Market Chart**

**Endpoint:** `GET https://api.coingecko.com/api/v3/coins/{id}/market_chart`

**Purpose:** Get historical market data (prices, market caps, volumes)

**Query Parameters:**

```typescript
interface CoinGeckoMarketChartRequest {
  id: string                        // Coin ID (required in path)
  vs_currency: string                // Currency (e.g., 'usd')
  days: number | 'max'               // Number of days or 'max'
  interval?: 'daily'                // Interval (only for days >= 30)
}
```

**Response:**

```typescript
interface CoinGeckoMarketChartResponse {
  prices: Array<[number, number]>   // [timestamp, price]
  market_caps: Array<[number, number]>
  total_volumes: Array<[number, number]>
}
```

---

### **5. Trending Coins**

**Endpoint:** `GET https://api.coingecko.com/api/v3/search/trending`

**Purpose:** Get trending coins

**Response:**

```typescript
interface CoinGeckoTrendingResponse {
  coins: Array<{
    item: {
      id: string
      coin_id: number
      name: string
      symbol: string
      market_cap_rank: number
      thumb: string
      small: string
      large: string
      slug: string
      price_btc: number
      score: number
    }
  }>
  exchanges: Array<{
    id: string
    name: string
    market_type: string
    thumb: string
    large: string
  }>
  nfts: Array<{
    id: string
    name: string
    symbol: string
    thumb: string
    nft_contract_id: number
  }>
  categories: Array<{
    id: number
    name: string
    market_cap_1h_change: number
    slug: string
    coins_count: number
  }>
}
```

---

### **6. Global Market Data**

**Endpoint:** `GET https://api.coingecko.com/api/v3/global`

**Purpose:** Get global cryptocurrency market data

**Response:**

```typescript
interface CoinGeckoGlobalResponse {
  data: {
    active_cryptocurrencies: number
    upcoming_icos: number
    ongoing_icos: number
    ended_icos: number
    markets: number
    total_market_cap: Record<string, number>
    total_volume: Record<string, number>
    market_cap_percentage: Record<string, number>
    market_cap_change_percentage_24h_usd: number
    updated_at: number
  }
}
```

---

## 🔄 **WORKFLOWS**

### **Workflow 1: Price Lookup**

1. User enters coin symbol or name
2. Search coins list → Find coin ID
3. Get current price → Display price
4. Show 24h change, market cap, volume

### **Workflow 2: Coin Details**

1. User selects coin
2. Get coin details → Display:
   - Current price
   - Market data
   - Description
   - Links
   - Community data
   - Developer data

### **Workflow 3: Price Chart**

1. User selects coin
2. Select time range (1d, 7d, 30d, 1y, max)
3. Get market chart → Display price chart
4. Show volume chart
5. Show market cap chart

### **Workflow 4: Trending Coins**

1. Get trending coins → Display list
2. Show trending score
3. Click coin → Show details

---

## ⚡ **RATE LIMITS**

**Free Tier:**
- 10-50 calls/minute (no API key)
- Rate limits vary

**Paid Tier:**
- Higher rate limits
- WebSocket support

---

## 💰 **PRICING**

**Free Tier:**
- 10-50 calls/minute
- Free forever

**Paid Tier:**
- $129/month for Basic
- Higher rate limits
- WebSocket support

---

## 🎨 **UI COMPONENT REQUIREMENTS**

### **Price Lookup Panel**

**Coin Search:**
- Search input with autocomplete
- Coin list dropdown

**Price Display:**
- Current price (large)
- 24h change (with color)
- Market cap
- 24h volume
- Price chart (sparkline)

### **Coin Details Panel**

**Coin Header:**
- Coin name and symbol
- Logo
- Rank

**Price Section:**
- Current price
- ATH/ATL
- Price change (1h, 24h, 7d, 30d, etc.)

**Market Data:**
- Market cap
- Volume
- Supply (circulating, total, max)
- Market cap rank

**Charts:**
- Price chart (interactive)
- Volume chart
- Market cap chart

**Additional Info:**
- Description
- Links (website, GitHub, etc.)
- Community stats
- Developer stats

### **Trending Panel**

**Trending List:**
- Trending coins grid
- Trending score
- Price and change
- Click → Show details

---

## 🔧 **IMPLEMENTATION NOTES**

### **Service Layer Structure**

```typescript
class CoinGeckoService extends BaseAPIService {
  constructor(apiKey?: string) {
    super('coingecko', 'https://api.coingecko.com/api/v3', apiKey)
  }

  async getSimplePrice(request: CoinGeckoSimplePriceRequest): Promise<APIResponse<CoinGeckoSimplePriceResponse>>
  async getCoinsList(includePlatform?: boolean): Promise<APIResponse<CoinGeckoCoinsListResponse>>
  async getCoinDetails(id: string, options?: CoinGeckoCoinDetailsRequest): Promise<APIResponse<CoinGeckoCoinDetailsResponse>>
  async getMarketChart(id: string, vsCurrency: string, days: number | 'max'): Promise<APIResponse<CoinGeckoMarketChartResponse>>
  async getTrending(): Promise<APIResponse<CoinGeckoTrendingResponse>>
  async getGlobal(): Promise<APIResponse<CoinGeckoGlobalResponse>>
  
  // Helpers
  async searchCoins(query: string): Promise<APIResponse<CoinGeckoCoinsListResponse>>
  async getCoinPrice(coinId: string, currency: string): Promise<APIResponse<number>>
}
```

---

## 📊 **INTEGRATION COMPLEXITY**

**Complexity:** Medium-High

**Dependencies:**
- Charting library
- Number formatting
- Currency conversion

**Estimated Implementation Time:**
- Service layer: 4-6 hours
- UI components: 6-8 hours
- Chart integration: 4-6 hours
- Testing: 3-4 hours
- **Total: 17-24 hours**

---

**Status:** Deep dive complete - Ready for implementation  
**Last Updated:** 2025-01-27

